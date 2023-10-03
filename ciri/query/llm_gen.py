import openai
import os
from typing import Dict, List

from ciri.post_processing.answer_parser import AnswerParser
from ciri.post_processing.pool import BasePool
from ciri.query.api_request import (
    create_codex_config,
    create_gpt_config,
    request_engine,
)
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

Anser:
```json
"""
    return prompt


class CodexGen:
    def __init__(self, args: Dict, config_file: str):
        self.model = args.model
        self.system = args.system
        self.version = args.version
        self.config_file = config_file
        self.prompt = get_prompt(self.system, self.version)
        self.pool_len = 10
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def codex_generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        config = create_codex_config(message, self.model)
        answerList = request_engine(config, "codex")
        return answerList

    def generate(self, output_path):
        answerParser = AnswerParser()
        while not answerParser.candidate_pool.full_status:
            new_outputs = self.codex_generate()
            answerParser.extracter(new_outputs)
        logger.info("Raw json:\n")
        for answer in answerParser.answer_pool.pool:
            logger.info(str(answer) + "\n")
        return answerParser


class GPTGen:
    def __init__(self, args: Dict, config_file: str):
        self.model = args.model
        self.system = args.system
        self.version = args.version
        self.config_file = config_file
        self.prompt = get_prompt(self.system, self.version)
        self.pool_len = 10

    def gpt_generate(self) -> List:
        message = f"{self.config_file}\n{self.prompt}"
        config = create_gpt_config(message, self.model)
        answerList = request_engine(config, "gpt")
        return answerList

    def generate(self, output_path):
        answerParser = AnswerParser()
        while not answerParser.candidate_pool.full_status:
            new_outputs = self.gpt_generate()
            answerParser.extracter(new_outputs)
        logger.info("Raw json:\n")
        for answer in answerParser.answer_pool.pool:
            logger.info(str(answer) + "\n")
        return answerParser

