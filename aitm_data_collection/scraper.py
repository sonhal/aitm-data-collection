import os
import re
import typing

from dotenv import load_dotenv
from github import Github, Repository, ContentFile

auth_file_regex_pattern = ".*?(auth|login|oidc|session).*?\.(ts|js)"
auth_regex = re.compile(auth_file_regex_pattern)

dir_patterns = ["auth", "oidc", "login", "session", "src", "server", "srv", "app", "middleware", "services", "service"]

query1 = "oidc-client filename:package.json path:/ express filename:package.json"
query2 = "openid-client filename:package.json path:/ express filename:package.json"

queries = [query1, query2]

def scraper():

    # using an access token
    g = Github(os.getenv("AITM_TOKEN"))
    repo_to_auth_files = {}
    for query in queries:
        print(f"AitM Scraper running query = {query}")
        result = g.search_code(query=query)
        print(f"Total results from query = {result.totalCount}")

        # Get one of the available pages

        for i in range(0, result.totalCount):
            page = result.get_page(i)

            # create a mapping of repos to likely authentication related source files (js, ts) in the repo
            new = {file.repository: find_auth_files(file.repository) for file in page}
            repo_to_auth_files = {**repo_to_auth_files, **new}
    repo_to_auth_files = dict(filter(lambda elem: len(elem[1]) > 0, repo_to_auth_files.items()))
    print(f"result nr = {len(repo_to_auth_files)}")
    print(repo_to_auth_files)

    summer = 0
    for repo, auth_files in repo_to_auth_files.items():
        for file, loc in auth_files:
            summer += loc
    print(f"total loc = {summer}")
    print(f"average loc = {summer / len(repo_to_auth_files)}")


def find_auth_files(repo: Repository) -> typing.List:
    print(f"Searching for auth files for repo = {repo.url}")
    auth_files = []
    root_contents = repo.get_contents("")
    while root_contents:
        file_content = root_contents.pop(0)
        if file_content.type == "dir" and is_server_or_auth_dir(file_content.name):
            root_contents.extend(repo.get_contents(file_content.path))
        else:
            if is_auth_file(file_content.name):
                print(f"auth file = {file_content.name} found for repo = {repo.name}")
                auth_files.append((file_content, file_loc(file_content)))
    return auth_files


def is_auth_file(name: str) -> bool:
    return True if auth_regex.match(name) else False


def is_server_or_auth_dir(name: str) -> bool:
    for pattern in dir_patterns:
        if pattern in name:
            return True
    return False


def file_loc(file: ContentFile):
    return sum(1 for _ in file.content.split("\n"))


if __name__ == '__main__':
    load_dotenv()
    scraper()
