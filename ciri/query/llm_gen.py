import anthropic
import openai
import time
from openai import OpenAI
from typing import Dict, List

from ciri.post_processing.answer_parser import AnswerParser
from ciri.ciri_logger import logger


def get_prompt(system: str, version: str) -> str:
    prompt = \
        f"""
Question: Are there any mistakes in the above configuration file for {system} version {version}? Respond in a json format similar to the following:
{{
    "hasError": boolean, // true if there are errors, false if there are none.
    "errParameter": [], // List containing properties with errors. If there are no errors, leave this as an empty array.
    "reason": [] // List containing explanations for each error. If there are no errors, leave this as an empty array.
}}

Answer:
```json
"""
    return prompt


class BaseGen:
    def __init__(self, args: Dict, config_file: str):
        self.model = args.model
        self.system = args.system
        self.version = args.version
        self.config_file = config_file
        self.prompt = get_prompt(self.system, self.version)
        self.pool_len = 3

    def _generate(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def generate(self):
        answerParser = AnswerParser(self.pool_len)
        while not answerParser.candidate_pool.full_status:
            new_outputs = self._generate()
            answerParser.extracter(new_outputs)
        logger.info("Raw json:")
        for answer in answerParser.answer_pool.pool:
            logger.info(answer)
        return answerParser


class GPTGen(BaseGen):
    def __init__(self, args: Dict, config_file: str):
        super().__init__(args, config_file)

    def _generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        client = OpenAI()
        while True:
            try:
                response = client.chat.completions.create(messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ], model=self.model, temperature=0.2, max_tokens=512, stop=["\n```"])
                break
            except (openai.APIConnectionError, openai.RateLimitError) as e:
                print(f"{e.__class__.__name__}. Retrying...")
                time.sleep(5)
            except Exception as e:
                print("Unknown error. Retrying...")
                print(e)
                time.sleep(1)

        answerList = [i.message.content.strip("\n") for i in response.choices]
        return answerList


class ClaudeGen(BaseGen):
    def __init__(self, args: Dict, config_file: str):
        super().__init__(args, config_file)

    def _generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        client = anthropic.Anthropic()
        while True:
            try:
                response = client.messages.create(model=self.model, system="You are a helpful assistant.",
                                                  messages=[{"role": "user", "content": message}],
                                                  temperature=0.2, stop_sequences=["\n```\n"], max_tokens=512)
                break
            except anthropic.RateLimitError as e:
                print(f"Rate limit error: {e}")
                time.sleep(5)
        return [i.text for i in response.content]


class LlamaGen(BaseGen):
    def __init__(self, args: Dict, config_file: str, model, tokenizer):
        super().__init__(args, config_file)
        self.model = model
        self.tokenizer = tokenizer

    def _generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        input_ids = self.tokenizer.encode(message, return_tensors="pt").to("cuda")
        input_len = len(input_ids[0])
        outputs = self.model.generate(input_ids, max_new_tokens=512, do_sample=True, temperature=0.2,
                                      eos_token_id=28956)
        answerList = []
        for output in outputs:
            answerList.append(self.tokenizer.decode(output[input_len:-1], skip_special_tokens=True))
        return answerList


class DeepseekGen:
    def __init__(self, args: Dict, config_file: str, model, tokenizer):
        super().__init__(args, config_file)
        self.model = model
        self.tokenizer = tokenizer

    def _generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        messages = [
            {'role': 'user', 'content': message}
        ]
        input_ids = self.tokenizer.apply_chat_template(messages, add_generation_prompt=False, return_tensors="pt").to(
            "cuda")
        input_len = len(input_ids[0])
        outputs = self.model.generate(input_ids, max_new_tokens=512, do_sample=True, temperature=0.2,
                                      eos_token_id=10252)
        answerList = []
        for output in outputs:
            answerList.append(self.tokenizer.decode(output[input_len:-1], skip_special_tokens=True))
        return answerList
