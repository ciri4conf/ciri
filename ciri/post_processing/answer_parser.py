import json
import re
from typing import Dict, List

from ciri.post_processing.pool import BasePool
from ciri.ciri_logger import logger


class AnswerParser:
	def __init__(self, pool_len: int = 3):
		self.pool_len = pool_len
		self.candidate_pool = BasePool(pool_len)
		self.answer_pool = BasePool(pool_len)

	def _is_valid_no_error(self, candidate: Dict) -> bool:
		return not candidate.get("hasError") and not candidate.get("errParameter") and not candidate.get("reason")

	def _is_valid_with_error(self, candidate: Dict) -> bool:
		error_properties = candidate.get("errParameter", [])
		reasons = candidate.get("reason", [])

		if not error_properties or not reasons:
			return False

		if len(error_properties) != len(reasons):
			print("The length of the error properties and the reasons are not the same.")

		return all(isinstance(ep, str) for ep in error_properties)

	def inspector(self, candidate):
		if "hasError" not in candidate:
			return False

		if not candidate["hasError"]:
			return self._is_valid_no_error(candidate)
		else:
			return self._is_valid_with_error(candidate)

	def extracter(self, answerList: List) -> None:
		for answer in answerList:
			if self.candidate_pool.full_status:
				break
			try:
				pattern = r'{\n.*?\n}'
				matches = re.findall(pattern, answer, re.DOTALL)
				if len(matches) != 1:
					logger.debug(f"Error: {answer} is not a valid json string.")
					continue
				answer_json = json.loads(matches[0])
			except json.JSONDecodeError:
				logger.debug(f"Error: {answer} is not a valid json string.")
				continue

			if self.inspector(answer_json):
				if not answer_json["hasError"]:
					self.candidate_pool.add(["None", ])
				else:
					self.candidate_pool.add(answer_json["errParameter"])
				self.answer_pool.add(answer_json)
			else:
				logger.debug(f"Error: {answer} is not a valid answer.")
