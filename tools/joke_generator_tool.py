from langchain_core.tools import tool
import requests

@tool
def generate_joke() -> dict:
    """ Generate a random joke """
    res = requests.get("https://official-joke-api.appspot.com/random_joke").json()

    return res