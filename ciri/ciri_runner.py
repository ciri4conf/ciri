import argparse
import os
import shutil
from pathlib import Path
from typing import Dict

from ciri.post_processing import answer_parser, pool, selection
from ciri.query.llm_gen import CodexGen, GPTGen
from ciri.ciri_logger import logger
from ciri.post_processing.reason_cluster import get_dominant_reason


def ciri_runner(args: Dict, file_content: str, output_path: str):
    if args.model in ["code-davinci-002", "babbage-002", "davinci-002"]:
        llm_gen = CodexGen(args, file_content)
    elif args.model in ["gpt-3.5-turbo", "gpt-4"]:
        llm_gen = GPTGen(args, file_content)
    else:
        raise Exception(f"The model {args.model} has not been supported.")

    answerParser = llm_gen.generate(output_path)
    selectionGen = selection.selection()
    pure_result = selectionGen.select(answerParser.candidate_pool.pool)
    if len(pure_result) > 1:
        result = "NO CONSISTENT RESULT"
    elif pure_result[0] == ["None"]:
        result = "The CONFIGURATION FILE IS CORRECT"
    else:
        result = (
            f"There are {len(pure_result[0])} misconfiguration parameters in the input: "
            + "\t".join(pure_result[0])
        )
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
