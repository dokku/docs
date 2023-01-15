"""
checks links in the docs to make sure they work
"""
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor

import bs4
import requests


def get_broken_links(text):
    """
    checks for broken links in a doc file
    """
    # Set root domain.
    root_domain = "dokku.com"

    # Internal function for validating HTTP status code.
    def _validate_url(url):
        response = requests.head(url, timeout=10)
        if response.status_code == 404:
            broken_links.append(url)

    # Parse HTML from request.
    soup = bs4.BeautifulSoup(text, features="html.parser")

    # Create a list containing all links with the root domain.
    links = []
    links = [anchor.get("href") for anchor in soup.find_all("a")]
    links = [link for link in links if link]
    links = [link for link in links if f"//{root_domain}" in link]

    # Initialize list for broken links.
    broken_links = []

    # Loop through links checking for 404 responses, and append to list.
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(_validate_url, links)

    return broken_links


def main():
    """
    main function
    """

    files_with_bad_links = []
    broken_links = []
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".html"):
                continue

            full_path = os.path.join(root, filename)
            print(f"====> Processing {full_path}")
            text = ""
            with open(full_path, encoding="utf-8") as file:
                text = file.read()

            links = get_broken_links(text)
            if len(links) > 0:
                files_with_bad_links.append(full_path)
                broken_links.extend(links)

    print("====> Files")
    for full_path in files_with_bad_links:
        print(f"      {full_path}")

    print("====> Links")
    for link in broken_links:
        print(f"      {link}")

if __name__ == "__main__":
    main()
