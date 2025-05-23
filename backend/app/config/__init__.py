import os
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = BASE_DIR / ".env"
load_dotenv(env_file)


class Config:

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    CALENDAR_AGENT_MODEL = os.getenv("CALENDAR_AGENT_MODEL")
    ITINERARY_PLANNER_MODEL = os.getenv("ITINERARY_PLANNER_MODEL")
    GENERAL_CONVERSATION_MODEL = os.getenv("GENERAL_CONVERSATION_MODEL")
    PLACE_RESEARCHER_MODEL = os.getenv("PLACE_RESEARCHER_MODEL")
    PLACE_RESPONSE_MODEL = os.getenv("PLACE_RESPONSE_MODEL")

    SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL")


# Create a config instance
config = Config()
