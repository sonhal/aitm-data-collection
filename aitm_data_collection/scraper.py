import os
import re
import datetime
import typing
from time import sleep
import pickle
from collections import namedtuple

from dotenv import load_dotenv
from github import Github, Repository, ContentFile, RateLimitExceededException, GithubException
from typing import List
import statistics
import pandas

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
    try:
        for query in queries:
            print(f"AitM Scraper running query = {query}")
            result = g.search_code(query=query)
            print(f"Total results from query = {result.totalCount}")

            for i in range(0, result.totalCount):
                page = result.get_page(i)

                # create a mapping of repos to likely authentication related source files (js, ts) in the repo
                new = {file.repository: find_auth_files(file.repository) for file in page}
                repo_to_auth_files = {**repo_to_auth_files, **new}
        repo_to_auth_files = dict(filter(lambda elem: len(elem[1]) > 0, repo_to_auth_files.items()))
        print(f"result nr = {len(repo_to_auth_files)}")
        print(repo_to_auth_files)
    except RateLimitExceededException as e:
        print(e)

    loc_array = []
    for repo, auth_files in repo_to_auth_files.items():
        for file, loc in auth_files:
            loc_array.append(loc)
    print(f"total loc = {sum(loc_array)}")
    print(f"average loc = {statistics.mean(loc_array)}")
    print(f"median loc = {statistics.median(loc_array)}")
    print(f"standard deviation loc = {statistics.stdev(loc_array)}")
    print(f"min loc = {min(loc_array)}")
    print(f"max loc = {max(loc_array)}")


def find_repos_for(query, token):
    g = Github(token)
    result = g.search_code(query=query)
    repos = []
    i = 0
    while i < result.totalCount:  # use while loop so we don`t skip page on exceptions
        try:
            repos += result.get_page(i)
            i += 1
        except RateLimitExceededException as e:
            reset_at = datetime.datetime.fromtimestamp(float(e.headers["x-ratelimit-reset"]))
            reset_in = (reset_at - datetime.datetime.now())
            reset_in_seconds = min(reset_in.seconds + 5, 600)
            print(
                f"Github error = {e.data} "
                f"x-ratelimit-limit = {e.headers['x-ratelimit-limit']}  "
                f"x-ratelimit-remaining = {e.headers['x-ratelimit-remaining']} "
                f"x-ratelimit-reset = {e.headers['x-ratelimit-reset']} ({reset_in.seconds}s)")
            print(f"ratelimit hit, waiting {reset_in_seconds} sec...")
            sleep(reset_in_seconds)
        except GithubException as e:
            print(f"Github exception {e.data}")
            print("Halting search and returning results found")
            break
    return repos


def find_auth_files(repo: Repository) -> typing.List:
    print(f"Searching for auth files for repo = {repo.url}")
    try:
        root_contents = repo.get_contents("")
        return search_repo_files(root_contents, repo)
    except GithubException as ge:
        if ge.status == 403:
            print(f"Access denied for repo, skipping: {ge}")
        else:
            raise ge


AuthFile = namedtuple("AuthFile", "file , loc")


def search_repo_files(root_contents, repo):
    auth_files = []
    while root_contents:
        file_content = root_contents.pop(0)
        if file_content.type == "dir" and is_server_or_auth_dir(file_content.name):
            root_contents.extend(repo.get_contents(file_content.path))
        else:
            if is_auth_file(file_content.name):
                print(f"auth file = {file_content.name} found for repo = {repo.name}")
                auth_files.append(AuthFile(file_content, file_loc(file_content)))
    return auth_files


def is_auth_file(name: str) -> bool:
    return True if auth_regex.match(name) else False


def is_server_or_auth_dir(name: str) -> bool:
    for pattern in dir_patterns:
        if pattern in name:
            return True
    return False


def avg_loc(files):
    summer = 0
    for file in files:
        summer += file_loc(file)
    return summer


def file_loc(file: ContentFile):
    return len(file.decoded_content.split(b"\n"))


def repo_auth_file_mapping_to_flat(mappings):
    data = []
    for repo, auth_files in mappings.items():
        for auth_file in auth_files:
            data.append((repo.html_url, auth_file.file.html_url, auth_file.loc))
    return data


def store_repos(repositories):
    with open("../data/repos_store.pickle", 'wb') as store:
        pickle.dump(repositories, store)


def load_repos() -> List[Repository.Repository]:
    with open("../data/repos_store.pickle", 'rb') as store:
        return pickle.load(store)


def store_mappings(repo_to_auth):
    with open("../data/repo_to_auth_mapping.pickle", 'wb') as store:
        pickle.dump(repo_to_auth, store)


def load_mappings() -> List[Repository.Repository]:
    with open("../data/repo_to_auth_mapping.pickle", 'rb') as store:
        return pickle.load(store)


if __name__ == '__main__':
    load_dotenv()
    scraper()
