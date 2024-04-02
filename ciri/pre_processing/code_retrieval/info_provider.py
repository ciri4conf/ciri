import os
from ciri.pre_processing.code_retrieval.code_crawler import CodeCrawler


class InfoProvider:
	def __init__(self, system: str, read_code_loc: str, config_format: str, language: str):
		self.system = system
		self.read_code_loc = read_code_loc
		self.config_format = config_format
		self.language = language
		self.cur_path = os.path.dirname(os.path.abspath(__file__))

	def get_usage(self, param):
		cc = CodeCrawler(self.read_code_loc, self.language)
		cache_file = os.path.join(self.cur_path, f".cache/{self.system}/{param}")
		if os.path.exists(cache_file):
			if os.path.getsize(cache_file) == 0:
				return None
			else:
				with open(cache_file) as f:
					return f.read()
		else:
			return None

	def generate(self, content: str):
		lines = content.split("\n")
		output_line = []
		if self.config_format == "xml":
			for num, line in enumerate(lines):
				output_line.append(line)
				if "<name" in line:
					param = line.split("<name>")[1].split("</name>")[0]
					usage = self.get_usage(param)
				elif "<value" in line:
					if usage is not None and "final" not in usage:
						output_line.append(f"  <usage>{usage}</usage>")
			return "\n".join(output_line)
		if self.config_format == "kv":
			for num, line in enumerate(lines):
				output_line.append(line)
				if "=" in line or ": " in line:
					if "=" in line:
						param = line.strip().split("=")[0]
					elif ": " in line:
						param = line.strip().split(": ")[0]
					usage = self.get_usage(param)
					if usage is not None:
						output_line.append(f"# Usage: {usage}")
			return "\n".join(output_line)
