from langchain_core.tools import tool
from github import Github, Auth # type: ignore[import-not-found]
from config.settings import GITHUB_TOKEN
import requests

def init_github():
    auth = Auth.Token(GITHUB_TOKEN)
    return Github(auth=auth)

@tool
def create_issue(repository_name: str, title: str, body: str):
    """ Function for creating github issue"""
    gh = init_github()
    repo = gh.get_repo(repository_name)

    repo.create_issue(
        title=title,
        body=body,
        labels=["bug"],        
    )

    return {"message": "issue created"}
