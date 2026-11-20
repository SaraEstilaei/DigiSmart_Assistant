import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("QBC13_API_KEY")
BASE_URL = "https://193.93.169.12/v1"

if not API_KEY:
    raise ValueError(
        "Error: QBC13_API_KEY environment variable not found in .env file!"
    )

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)
