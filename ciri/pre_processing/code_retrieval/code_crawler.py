import re
import subprocess


class CodeCrawler:
	def __init__(self, repo_loc: str, language: str):
		self.repo_loc = repo_loc
		self.language = language

	def search(self, param: str):
		if self.language == "java":
			command = f"grep -rh --include='*.java' '\"{param}\"' {self.repo_loc} | sed 's|^{self.repo_loc}/||'"
			try:
				output = subprocess.check_output(command, shell=True, text=True)
			except subprocess.CalledProcessError as e:
				output = e.output
			processed_out = [line.strip() for line in output.split("\n")]
			keywords = (" final ", " static ", "import ")
			filter_out = [line for line in processed_out if
		              not any(keyword in line for keyword in keywords) and ";" in line and not line.endswith(f"= \"{param}\";")]
			if len(filter_out) == 0:
				return None
			max_processed_out = max(filter_out, key=len)
			if len(max_processed_out) < 2 * len(param):
				return None
			return max_processed_out
		if self.language == "go":
			command = f"grep -rh --include='*.go' '\"{param}\"' {self.repo_loc} | sed 's|^{self.repo_loc}/||'"
			try:
				output = subprocess.check_output(command, shell=True, text=True)
			except subprocess.CalledProcessError as e:
				output = e.output
			processed_out = [line.strip() for line in output.split("\n")]
			filter_out = []
			if len(filter_out) != 0:
				return max(filter_out, key=len)
			return None
		if self.language == "c":
			command = f"grep -rh --include='*.c' '{param}' {self.repo_loc} | sed 's|^{self.repo_loc}/||'"
			try:
				output = subprocess.check_output(command, shell=True, text=True)
			except subprocess.CalledProcessError as e:
				output = e.output
			processed_out = [line.strip() for line in output.split("\n")]
			pattern = rf"^(int|bool|double|char).*{param} ="
			filter_out = []
			for line in processed_out:
				if re.search(pattern, line) and not any(c.isupper() for c in line) and "Xinyu Lian" in line:
					filter_out.append(line)
			if len(filter_out) == 0:
				return None
			max_processed_out = max(filter_out, key=len)
			return max_processed_out

