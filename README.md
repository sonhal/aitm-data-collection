# Evaluating AitM


## Goal

- Find NodeJs application that use OIDC/OAuth 2.0
- LoC with authentication

## Steps

- search for projects using Github api search

    `oidc-client filename:package.json path:/ express filename:package.json`
- look for files that indicate that they implement authentication

- get average, median, min and max LoC of authentication code

- Sample some of the projects (maybe especially outliers)

## To run the jupyter notebook
1. Make sure you have ran `poetry install`
2. Install the poetry venv in the notebook server. Run the command `python -m ipykernel install --user --name=<name of the venv> jupyter notebook`
3. Run `jupyter notebook` in the project dir