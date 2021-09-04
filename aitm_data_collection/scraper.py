
def scraper():
    from github import Github

    # First create a Github instance:

    # using an access token
    g = Github("access_token")

    g.search_code()


if __name__ == '__main__':
    scraper()