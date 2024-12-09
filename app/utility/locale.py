from dotenv import load_dotenv
import os 

load_dotenv()

class Config:
    GITHUB_PAT = str(os.getenv('GITHUB_PAT'))
    GEMINI_KEY = str(os.getenv('GEMINI_KEY'))
    REDIS_HOST = str(os.getenv('REDIS_HOST'))
    REDIS_PORT = int(os.getenv('REDIS_PORT', 11062))
    REDIS_USERNAME = str(os.getenv('REDIS_USERNAME', 'default'))
    REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))
    POSTGRES_URL = str(os.getenv('POSTGRES_URL'))
    