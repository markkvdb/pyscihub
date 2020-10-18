"""Main module."""

import logging
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import unicodedata


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
        response = self.session.post(self.url, data={"request": query})

        if response.status_code != 200:
            logging.error(f"Could not connect to Sci-Hub via: {response.url}")
        else:
            # if status code is okay then transform into beautiful soup
            soup = BeautifulSoup(response.text, features="lxml")
            data = self.extract_data(soup)

            if self.is_valid(data):
                self.save_pdf(data)

    def extract_data(self, soup: BeautifulSoup):
        # url regex
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        pdf_url = re.findall(
            regex, soup.find("div", id="buttons").select("ul li a")[0]["onclick"]
        )[0][0]

        return {
            "citation": soup.find("div", id="citation").get_text(),
            "link": soup.find("div", id="link").find("a")["href"],
            "pdf": pdf_url,
        }

    def is_valid(self, data):
        """Check if data is valid"""
        if data["citation"] is None or data["link"] is None or data["pdf"] is None:
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

            with open(self.output_path / fn_name, "wb") as pdf:
                pdf.write(response.content)
        else:
            logging.error(f"Could not open PDF {data['pdf']}")
