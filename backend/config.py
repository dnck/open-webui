import os
import yaml
#import chromadb
#from chromadb import Settings
from secrets import token_bytes
from base64 import b64encode
from constants import ERROR_MESSAGES
from pathlib import Path

script_dirname, script_filename = os.path.split(os.path.abspath(__file__))
project_root_dir = os.path.dirname(script_dirname)


try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(os.path.join(project_root_dir, ".env")))
except ImportError:
    print("dotenv not installed, skipping...")


def load_config(config_fp: str) -> dict:
    """Load configuration settings from YAML file."""
    with open(config_fp, "r") as file:
        config = yaml.safe_load(file)
        return config
    return {}

settings = load_config(os.path.join(script_dirname, "config.yaml"))

####################################
# ENV (dev,test,prod)
####################################

ENV = settings["environment"]
print(f"ENV = {ENV}")


####################################
# DATA/FRONTEND BUILD DIR
####################################

DATA_DIR = str(Path(settings["data_dir"]).resolve())
FRONTEND_BUILD_DIR = str(Path(settings["front_build_dir"]))

####################################
# File Upload DIR
####################################

UPLOAD_DIR = settings["upload_dir"]
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


####################################
# Cache DIR
####################################

CACHE_DIR = f"{DATA_DIR}/cache"
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

####################################
# OLLAMA_API_BASE_URL
####################################

OLLAMA_API_BASE_URL = settings["ollama_api_base_url"]
print(f"OLLAMA_API_BASE_URL = {OLLAMA_API_BASE_URL}")

if ENV == "prod":
    if OLLAMA_API_BASE_URL == "/ollama/api":
        OLLAMA_API_BASE_URL = "http://host.docker.internal:11434/api"

####################################
# OPENAI_API
####################################

OPENAI_API_KEY = settings["openai_api_key"]
OPENAI_API_BASE_URL = settings["openai_api_base_url"]

####################################
# WEBUI
####################################

ENABLE_SIGNUP = settings["enable_signup"]
DEFAULT_MODELS = settings.get("default_models")

def fix_wacky_idea(settings):
    result = []
    for suggestion in settings["default_prompt_suggestions"]:
        result.append({
            "title": [suggestion["title"]],
            "content": suggestion["content"]
        })
    return result

DEFAULT_PROMPT_SUGGESTIONS = fix_wacky_idea(settings)
print(DEFAULT_PROMPT_SUGGESTIONS)
# DEFAULT_PROMPT_SUGGESTIONS = os.environ.get(
#     "DEFAULT_PROMPT_SUGGESTIONS",
#     [
#         {
#             "title": ["Help me study", "vocabulary for a college entrance exam"],
#             "content": "Help me study vocabulary: write a sentence for me to fill in the blank, and I'll try to pick the correct option.",
#         },
#         {
#             "title": ["Give me ideas", "for what to do with my kids' art"],
#             "content": "What are 5 creative things I could do with my kids' art? I don't want to throw them away, but it's also so much clutter.",
#         },
#         {
#             "title": ["Tell me a fun fact", "about the Roman Empire"],
#             "content": "Tell me a random fun fact about the Roman Empire",
#         },
#         {
#             "title": ["Show me a code snippet", "of a website's sticky header"],
#             "content": "Show me a code snippet of a website's sticky header in CSS and JavaScript.",
#         },
#     ],
# )

####################################
# WEBUI_VERSION
####################################

WEBUI_VERSION = settings["webui_version"]

####################################
# WEBUI_AUTH (Required for security)
####################################

WEBUI_AUTH = settings["webui_auth"]

####################################
# WEBUI_SECRET_KEY
####################################

WEBUI_SECRET_KEY = settings["webui_secret_key"]

if WEBUI_AUTH and WEBUI_SECRET_KEY == "":
    raise ValueError(ERROR_MESSAGES.ENV_VAR_NOT_FOUND)

####################################
# RAG
####################################
CHROMA_DATA_PATH = settings["chroma_data_path"]
EMBED_MODEL = settings["embed_model"]
# CHROMA_CLIENT = chromadb.PersistentClient(
#     path=CHROMA_DATA_PATH, settings=Settings(allow_reset=True,
#                                              anonymized_telemetry=False)
# )
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100

####################################
# Transcribe
####################################
WHISPER_MODEL_NAME = settings["whisper_model_name"]
