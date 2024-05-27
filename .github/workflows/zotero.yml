name: Zotero

on:
  pull_request:
    branches:
      - master
      - main
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    # available images: https://github.com/actions/runner-images#available-images
    runs-on: ubuntu-latest
    steps:
      - name: Checkout 🛎️
        uses: actions/checkout@v4
      - name: Setup Ruby
        uses: actions/setup-python@v4
        with:
	      id: python
          python-version: "3.9"
          cache: 'pip'
          cache-dependency-path: requrements.txt
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        if: steps.python.outputs.cache-hit != 'true'
      - name: Run Zotero
        run: python _plugins/zotero.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: Zotero file
