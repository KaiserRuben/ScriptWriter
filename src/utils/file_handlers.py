import json
import os
import logging
from typing import Union


def load_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        return {}

def save_json(file_path: str, data: Union[dict, list]):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    logging.info(f"Saved JSON to {file_path}")

def load_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return ""

def save_txt(file_path: str, content: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)
    logging.info(f"Saved text to {file_path}")