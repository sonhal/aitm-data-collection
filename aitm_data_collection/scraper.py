import os

from dotenv import load_dotenv
from github import Github



def scraper():
    # First create a Github instance:

    # using an access token
    g = Github(os.getenv("AITM_TOKEN"))

    result = g.search_repositories(query="language:javascript oidc-client in:file").reversed
    print(result.totalCount)

    page = result.get_page(1)
    print(page)


    # repositories = g.search_repositories(query='language:python')
    # for repo in repositories:
    #     print(repo)


if __name__ == '__main__':
    load_dotenv()
    scraper()