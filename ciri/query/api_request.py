import openai
import signal
import time
from typing import Dict, List


# Set up a signal handler to raise an exception after a specified timeout
def handler(signum, frame):
    raise Exception("Request timed out.")


def create_codex_config(
    message: str,
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> Dict:
    """Generate configuration for the Codex engine."""
    return {
        "model": model,
        "prompt": message,
        "temperature": temperature,
        "stop": ["```"],
        "max_tokens": max_tokens,
    }


def create_gpt_config(
    message: str,
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 512,
    system_message: str = "You are a helpful assistant.",
) -> Dict:
    """Generate configuration for the GPT engine."""
    return {
        "engine": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message},
        ],
        "temperature": temperature,
        "stop": ["```"],
        "max_tokens": max_tokens,
    }


def request_engine(config: Dict, engine_type: str) -> List[str]:
    """Request either Codex or GPT engine based on the engine type provided.
    
    Args:
        config: The configuration dictionary.
        engine_type: Either 'codex' or 'gpt'.
    
    Returns:
        A list of response(s) from the engine.
    """
    while True:
        try:
            # Set the timeout for the API request
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(100)

            if engine_type == "codex":
                response = openai.Completion.create(**config)
                return [i.text.strip("\n") for i in response.choices]
            elif engine_type == "gpt":
                response = openai.ChatCompletion.create(**config)
                return [i.message.content.strip("\n") for i in response.choices] 
            
        except (openai.error.InvalidRequestError,
                openai.error.RateLimitError,
                openai.error.APIConnectionError) as e:
            print(f"{e.__class__.__name__}. Retrying...")
            time.sleep(5)
        except Exception as e:
            print("Unknown error. Retrying...")
            print(e)
            time.sleep(1)
        finally:
            # Always cancel the alarm 
            signal.alarm(0)
            
