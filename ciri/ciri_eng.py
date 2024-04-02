import argparse
import logging
import os
import shutil
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict

from ciri.ciri_logger import logger
from ciri.ciri_runner import ciri_runner
from ciri.pre_processing.shot.shot_selection import ShotSelection
from ciri.pre_processing.code_retrieval.info_provider import InfoProvider


def _create_output_directory(directory):
	"""
    If directory exists, it deletes it and creates a new one.
    If it doesn't exist, it simply creates it.
    """
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)


def set_new_handler_for_logger(new_log_loc):
	# Identify and remove the existing FileHandler from the logger
	for h in logger.handlers:
		if isinstance(h, logging.FileHandler):
			logger.removeHandler(h)
	new_handler = logging.FileHandler(new_log_loc)
	logger.addHandler(new_handler)


def _ciri_eng(args, input_path: str, output_path: str, model=None, tokenizer=None):
	print("[Ciri] Start")
	print(f"[Ciri] Running for file {input_path}")
	logger.debug(f"[Ciri] Running for file {input_path}")
	input_file_content = Path(input_path).read_text()
	logger.debug(f"[Ciri] Input file content:\n{input_file_content}")
	if args.validconfig_shot_num + args.misconfig_shot_num > 0:
		shot_content = ShotSelection(
			args,
			input_file_content,
		).select()
		input_file_content = shot_content + input_file_content
	logger.debug(f"[Ciri] Shot+File to be queried:\n{input_file_content}")
	config_file_content = Path(input_path).read_text()
	if args.read_code:
		ip = InfoProvider(args.system, args.read_code_loc, args.file_format, args.language)
		input_file_content += ip.generate(config_file_content)
	else:
		input_file_content += config_file_content
	ciri_runner(args, file_content=input_file_content, output_path=output_path, model=model, tokenizer=tokenizer)


def ciri_eng(args: Dict):
	input_path = args.input_path
	output_path = args.output_path
	if os.path.isdir(input_path):
		_create_output_directory(output_path)
		file_list = os.listdir(input_path)
		logger.debug(f"{len(file_list)} file(s) to process.")
		checkpoint = args.model
		model = None
		tokenizer = None
		if checkpoint.startswith("deepseek"):
			model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map='auto', torch_dtype=torch.bfloat16,
			                                             trust_remote_code=True).to("cuda")
			tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
		elif checkpoint.startswith("codellama"):
			model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map='auto', torch_dtype=torch.float16).to("cuda")
			tokenizer = AutoTokenizer.from_pretrained(checkpoint)
		for file_name in file_list:
			input_file_loc = os.path.join(input_path, file_name)
			output_file_loc = os.path.join(output_path, file_name)
			set_new_handler_for_logger(output_file_loc)
			_ciri_eng(args, input_file_loc, output_file_loc, model, tokenizer)
	elif os.path.isfile(input_path):
		if os.path.exists(output_path):
			os.remove(output_path)
		logger.debug("1 file to process.")
		_ciri_eng(args, input_path, output_path)
	else:
		raise ValueError(f"'{input_path}' is neither a file nor a directory.")


def main():
	parser = argparse.ArgumentParser(
		description="Run the Ciri engine on a file or a directory of files."
	)
	parser.add_argument(
		"--input_path",
		required=True,
		type=str,
		help="Path to the input file or directory.",
	)
	parser.add_argument(
		"--output_path",
		required=True,
		type=str,
		help="Path to the output file or directory.",
	)
	parser.add_argument(
		"--model",
		required=True,
		type=str,
		help="Name of the model.",
	)
	parser.add_argument(
		"--system",
		required=True,
		type=str,
		help="Name of the system to use for processing.",
	)
	parser.add_argument(
		"--version",
		required=True,
		type=str,
		help="Version of the system to use for processing.",
	)
	parser.add_argument(
		"--validconfig_shot_num",
		required=False,
		default=1,
		type=int,
		help="Number of shots to use for the model.",
	)
	parser.add_argument(
		"--misconfig_shot_num",
		required=False,
		default=3,
		type=int,
		help="Number of shots to use for the model.",
	)
	parser.add_argument(
		"--shot_selection",
		required=False,
		default="random",
		type=str,
		help="Shot selection Strategy.",
	)
	parser.add_argument(
		"--file_format",
		required=False,
		default="xml",
		type=str,
		help="Config File Format",
	)
	parser.add_argument(
		"--language",
		required=False,
		default="java",
		type=str,
		help="Project Programming Language",
	)
	parser.add_argument(
		"--read_code",
		required=False,
		default=False,
		type=bool,
		help="Whether to read the configuration parameter from the code.",
	)
	parser.add_argument(
		"--read_code_loc",
		required=False,
		type=str,
		help="Path of the code repository.",
	)
	parser.add_argument(
		"--shot_system",
		required=False,
		default=None,
		type=str,
	)
	args = parser.parse_args()
	logger.debug(f"Arguments: {args}")
	ciri_eng(args)


if __name__ == "__main__":
	main()
