from agents.core import run_core
from tools.weather_tool import get_weather
from tools.joke_generator_tool import generate_joke
from tools.github_tool import create_issue
from tools.gmail_tool import draft_email

def run_agent(query):
    # Instantiate OpenAI
    response = run_core(query, [
        get_weather, 
        generate_joke, 
        create_issue,
        draft_email
    ])

    return {"code": 200, "message": response}

    