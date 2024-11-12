import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../.env")  # This will automatically look for a .env file in the root directory

class Config:
    # Access the environment variable using os.getenv
    GENAI_API_KEY = os.getenv('GENAI_API_KEY')  # Will return None if not set
    SECRET_KEY = os.urandom(24)
