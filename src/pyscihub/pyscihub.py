"""Main module."""

import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import List, TypedDict, Union

import click
import requests
from bs4 import BeautifulSoup

from .tools import extract_valid_query, valid_fn


class Result(TypedDict):
    citation: str | None
    link: str | None
    pdf: str | None


class SciHub(object):
    """The SciHub object can be used to download PDFs from SciHub after initialisation."""

    def __init__(self, url: str, output: Path):
        """Initialises the SciHub object with the Sci-Hub url ``url`` and writes all PDFs to the ``output_path`` folder.

        Args:
            url (str): Sci-Hub URL to use
            output_path (Path): The folder to download all PDFs to
        """
        # make sure that the output path exists
        output.mkdir(parents=True, exist_ok=True)

        self._url = url
        self._output_path = output
        self.session = requests.Session()

    def download(self, queries: Union[List[str], str]):
        """Download articles for provided queries

        Args:
            queries (list(str)): List of queries to look up

        Raises:
            ValueError: If argument is not a string or list of strings
        """
        # make sure queries is of the right format
        if isinstance(queries, str):
            queries = list(queries)
        elif not isinstance(queries, list):
            raise ValueError("queries argument should be a list or a single string.")

        # get existing downloads or create empty dict for pdf locations
        pdf_paths = self._get_pdf_paths()

        # remove queries that have a valid pdf file already
        queries = self._exclude_existing_queries(queries, pdf_paths)

        try:
            with click.progressbar(queries) as bar:
                for query in bar:
                    try:
                        pdf_path = self._fetch_search(query)
                        if pdf_path:
                            pdf_paths[query] = pdf_path
                    except (KeyboardInterrupt, SystemExit) as err:
                        raise err
                    except:
                        logging.error(f"Something went wrong for query: {query}")
                        pdf_paths[query] = ""
        except (KeyboardInterrupt, SystemExit):
            logging.info(
                f"Exiting program. Saving PDF information to {self._output_path}."
            )
        finally:
            self._save_pdf_paths(pdf_paths)

    def _get_pdf_paths(self) -> dict[str, str]:
        """Checks for existing pdf_path file or return empty one

        Returns:
            dict: Dictionary containing existing PDFs
        """
        f_path = self._output_path / "pdf_paths.csv"
        pdf_paths: dict[str, str] = dict()

        if f_path.is_file():
            logging.debug("pdf_paths.csv file detected.")
            with open(f_path, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["pdf_path"] != "":
                        if Path(row["pdf_path"]).is_file():
                            pdf_paths[row["query"]] = row["pdf_path"]

        return pdf_paths

    def _save_pdf_paths(self, pdf_paths: dict[str, str]):
        """Saves the queries and corresponding paths to the PDFs after downloading

        Args:
            pdf_paths (dict): Dictionary of paths to the downloaded PDFs
        """
        f_path = self._output_path / "pdf_paths.csv"

        if len(pdf_paths.keys()) > 0:
            with open(f_path, "w") as f:
                w = csv.writer(f)
                w.writerow(["query", "pdf_path"])
                for k, v in pdf_paths.items():
                    w.writerow([k, v])

    def _exclude_existing_queries(
        self, queries: list[str], pdf_paths: dict[str, str]
    ) -> list[str]:
        """Remove queries of which we already have a PDF file

        Args:
            queries (list(str)): List of queries to look up
            pdf_paths (dict): Dictionary of paths to the downloaded PDFs

        Returns:
            list(str): Filtered list of queries
        """
        return [query for query in queries if query not in pdf_paths.keys()]

    def _fetch_search(self, query: str):
        """Try to find page and return PDF location if succeeded

        Args:
            query (list(str)): List of queries to look up

        Returns:
            str: File location of downloaded PDF corresponding to query
        """
        clean_query = extract_valid_query(query)
        if not clean_query:
            logging.error(
                f"Could not extract valid query from: {query}. Try providing a valid URL, doi or title."
            )
            return None
        else:
            response = self.session.post(self._url, data={"request": clean_query})
            return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> str | None:
        """Handle a valid response

        Args:
            response (Response): requests.Response object

        Returns:
            str: File location of downloaded PDF corresponding to query
        """
        if response.status_code != 200:
            logging.error(f"Could not connect to Sci-Hub via: {response.url}")
            return None
        else:
            # if status code is okay then transform into beautiful soup
            soup = BeautifulSoup(response.text, features="lxml")
            if self._page_is_valid(soup):
                data = self._extract_data(soup)
                if self._data_is_valid(data):
                    return self._save_pdf(data)

            return None

    def _page_is_valid(self, soup: BeautifulSoup) -> bool:
        """Sometimes we cannot find the article or we need to solve a CAPTCHA

        Args:
            soup (BeautifulSoup): Soup of the requested search query

        Returns:
            bool: True if shown page is not a missing article or CAPTCHA page
        """
        if re.search(r"article not found", soup.get_text()):
            logging.warn(f"Could not find article.")
            return False
        elif re.search(r"Для просмотра статьи разгадайте капчу", soup.get_text()):
            logging.warn(f"Could not open page due to CAPTCHA.")
            return False
        else:
            return True

    def _extract_data(self, soup: BeautifulSoup) -> Result:
        """Extract citation, URL and PDF link from page

        Args:
            soup (BeautifulSoup): Soup of the requested search query

        Returns:
            dict: A dictionary containing the citation, URL and PDF link
        """
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

    def _data_is_valid(self, data: Result):
        """Check if extracted data contains a valid PDF link

        Args:
            data (dict): A dictionary containing the citation, URL and PDF link

        Returns:
            bool: True if data contains a PDF link
        """
        if data["pdf"] is None:
            return False
        else:
            return True

    def _save_pdf(self, data: Result) -> str | None:
        """Try to download the PDF from the link and save it to the output folder

        Args:
            data (dict): A dictionary containing the citation, URL and PDF link

        Returns:
            str: File location of downloaded PDF corresponding to query
        """
        # open PDF
        if data["pdf"] is None:
            logging.error(f"No PDF link found for: {data['citation']}")
            return None
        if data["citation"] is None:
            logging.error(f"No citation found for: {data['pdf']}")
            return None

        response = requests.get(data["pdf"])

        if response.status_code == 200:
            fn_name = unicodedata.normalize("NFKD", data["citation"])
            fn_name = re.sub(r"[^\w\s-]", "", fn_name).strip().lower()
            fn_name = re.sub(r"[-\s]+", "-", fn_name)
            fn_name = valid_fn(str(self._output_path.resolve()), fn_name)
            fn_name = f"{fn_name}.pdf"

            try:
                with open(self._output_path / fn_name, "wb") as pdf:
                    pdf.write(response.content)

                return str(self._output_path.resolve() / fn_name)
            except OSError as err:
                logging.error(err.strerror)
        else:
            logging.error(f"Could not download PDF from: {data['pdf']}")

        return None
