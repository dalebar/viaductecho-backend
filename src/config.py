import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
    
    KEYWORDS = ['stockport', 'macclesfield', 'buxton', 'high peak', 
                'wilmslow', 'cheadle', 'glossop', 'hyde', 'dukinfield', 'stalybridge']