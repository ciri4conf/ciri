from typing import Dict

from ciri.post_processing import selection
from ciri.query.llm_gen import GPTGen, ClaudeGen, LlamaGen, DeepseekGen
from ciri.ciri_logger import logger
from ciri.post_processing.reason_cluster import get_dominant_reason


def ciri_runner(args: Dict, file_content: str, output_path: str, model, tokenizer):
    if args.model in ["gpt-3.5-turbo-0125", "gpt-4-0125-preview"]:
        llm_gen = GPTGen(args, file_content)
    elif args.model.startswith("claude"):
        llm_gen = ClaudeGen(args, file_content)
    elif args.model.startswith("codellama"):
        llm_gen = LlamaGen(args, file_content, model, tokenizer)
    elif args.model.startswith("deepseek"):
        llm_gen = DeepseekGen(args, file_content, model, tokenizer)
    else:
        raise Exception(f"The model {args.model} has not been supported.")

    reach_agreement = False
    while not reach_agreement:
        answerParser = llm_gen.generate()
        selectionGen = selection.selection()
        pure_result = selectionGen.select(answerParser.candidate_pool.pool)
        if len(pure_result) > 1:
            result = "NO CONSISTENT RESULT"
        elif pure_result[0] == ["None"]:
            result = "The CONFIGURATION FILE IS CORRECT"
            reach_agreement = True
        else:
            result = (
                f"There are {len(pure_result[0])} misconfiguration parameters in the input: "
                + "\t".join(pure_result[0])
            )
            reach_agreement = True
    logger.info("Final result:\n")
    logger.info(result)
    print(f"[Ciri] Result: {result}")
    if len(pure_result) <= 1 and pure_result[0] != ["None"]:
        raw_answer = answerParser.answer_pool.pool
        for misconf_param in pure_result[0]:
            reason_list = []
            for raw_answer_item in raw_answer:
                if set(raw_answer_item["errParameter"]) == set(pure_result[0]):
                    index = raw_answer_item["errParameter"].index(misconf_param)
                    reason_list.append(raw_answer_item["reason"][index])
            reason = get_dominant_reason(reason_list)
            print(f"[Ciri] Reason for {misconf_param}: {reason}")
            logger.info(f"[Ciri] Reason for {misconf_param}: {reason}")
    print(f"[Ciri] Writing log file to {output_path}")
    print("[Ciri] End")
