"""Main module."""

import logging
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import unicodedata

from .tools import extract_valid_query


class SciHub(object):
    def __init__(self, url, output_path):
        self.url = url
        self.output_path = Path(output_path)
        self.session = requests.Session()

    def run(self, queries):
        if type(queries) == str:
            queries = list(queries)

        for query in queries:
            self.fetch_search(query)

    def fetch_search(self, query):
        """Try to find page and return URL and PDF link."""
        clean_query = extract_valid_query(query)
        if not clean_query:
            logging.error(
                f"Could not extract valid query from: {query}. Try providing a valid URL, doi or title."
            )
        else:
            response = self.session.post(self.url, data={"request": clean_query})

            if response.status_code != 200:
                logging.error(f"Could not connect to Sci-Hub via: {response.url}")
            else:
                # if status code is okay then transform into beautiful soup
                soup = BeautifulSoup(response.text, features="lxml")
                if self.page_contains_pdf(soup):
                    data = self.extract_data(soup)
                    if self.is_valid(data):
                        self.save_pdf(data)

    def extract_data(self, soup: BeautifulSoup):
        # url regex
        URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        pdf_url = re.findall(
            URL_REGEX, soup.find("div", id="buttons").select("ul li a")[0]["onclick"]
        )[0][0]

        # if URL does not contain https, then add it
        if not re.match(r"^https://", pdf_url):
            pdf_url = f"https://{pdf_url}"

        return {
            "citation": soup.find("div", id="citation").get_text(),
            "link": soup.find("div", id="link").find("a")["href"],
            "pdf": pdf_url,
        }

    def is_valid(self, data):
        """Check if data is valid"""
        if data["pdf"] is None:
            return False
        else:
            return True

    def page_contains_pdf(self, soup: BeautifulSoup):
        """Sometimes we cannot find the article or we need to solve a CAPTCHA."""
        if re.search(r"article not found", soup.get_text()):
            logging.warn(f"Could not find article with query: {clean_query}")
            return False
        elif re.search(r"Для просмотра статьи разгадайте капчу", soup.get_text()):
            logging.warn(f"Could not open page due to CAPTCHA.")
            return False
        else:
            return True

    def save_pdf(self, data):
        """Save pdf if provided."""
        # open PDF
        response = requests.get(data["pdf"])

        if response.status_code == 200:
            fn_name = unicodedata.normalize("NFKD", data["citation"])
            fn_name = re.sub(r"[^\w\s-]", "", fn_name).strip().lower()
            fn_name = re.sub(r"[-\s]+", "-", fn_name)
            fn_name = f"{fn_name}.pdf"

            try:
                with open(self.output_path / fn_name, "wb") as pdf:
                    pdf.write(response.content)
            except OSError as err:
                logging.error(err.strerror)
        else:
            logging.error(f"Could not download PDF from: {data['pdf']}")
