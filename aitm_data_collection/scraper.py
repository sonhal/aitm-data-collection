import os
import re
import typing

from dotenv import load_dotenv
from github import Github, Repository, ContentFile

auth_file_regex_pattern = ".*?(auth|login|oidc|session).*?\.(ts|js)"
auth_regex = re.compile(auth_file_regex_pattern)


dir_patterns = ["auth", "oidc", "login", "session", "src", "server", "srv"]


def scraper():
    query = "oidc-client filename:package.json path:/ express filename:package.json"
    # using an access token
    g = Github(os.getenv("AITM_TOKEN"))

    print(f"query = {query}")
    result = g.search_code(query=query)
    print(f"Total results from query = {result.totalCount}")

    # Get one of the available pages
    page = result.get_page(0)

    # create a mapping of repos to likely authentication related source files (js, ts) in the repo
    repo__auth_files = {file.repository: find_auth_files(file.repository) for file in page}
    print(repo__auth_files)


def find_auth_files(repo: Repository) -> typing.List:
    print(f"Searching for auth files for repo = {repo.name}")
    auth_files = []
    root_contents = repo.get_contents("")
    while root_contents:
        file_content = root_contents.pop(0)
        if file_content.type == "dir" and is_server_or_auth_dir(file_content.name):
            root_contents.extend(repo.get_contents(file_content.path))
        else:
            if is_auth_file(file_content.name):
                print(f"auth file = {file_content.name} found for repo = {repo.name}")
                auth_files.append(file_content)
    return auth_files


def is_auth_file(name: str) -> bool:
    return True if auth_regex.match(name) else False


def is_server_or_auth_dir(name: str) -> bool:
    for pattern in dir_patterns:
        if pattern in name:
            return True
    return False


if __name__ == '__main__':
    load_dotenv()
    scraper()
