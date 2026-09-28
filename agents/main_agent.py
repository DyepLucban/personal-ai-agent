from agents.core import run_core
from tools.weather_tool import get_weather
from tools.joke_generator_tool import generate_joke
from tools.github_tool import create_issue
from tools.gmail_tool import draft_email
from tools.db_search_tool import database_search

def run_agent(query):
    # Instantiate OpenAI
    response = run_core(query, [
        get_weather,
        generate_joke,
        create_issue,
        draft_email,
        database_search
    ])

    return {"code": 200, "message": response}

    