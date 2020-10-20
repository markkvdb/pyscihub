"""Tools for handling queries."""

import re
import os
import logging


def ref_regex():
    """Return regex for valid reference."""
    FIRST_AUTHOR = r"(?P<first_author>[A-Z][\w\-']+(?:,\s(?:[A-Z]\.)+))"
    SECOND_AUTHOR = r"(?P<other_author>(?:[A-Z]\.)+\s[A-Z][\w\-']+)"
    ET_AL = r"et al\."
    BETWEEN_AUTHORS = r"(?:(?:[,]?\sand\s)|(?:\,\s))"
    ALL_AUTHORS = (
        r"(?:"
        + FIRST_AUTHOR
        + r"(?:(?:"
        + BETWEEN_AUTHORS
        + SECOND_AUTHOR
        + r")+|(?:"
        + BETWEEN_AUTHORS
        + ET_AL
        + r"))?\,\s)?"
    )  # optional

    TITLE = r"(?P<title>[^.]+)"
    JOURNAL = r"(?:\s(?P<journal>[^.]+)[,.])?"  # optional
    YEAR = r"(?:\s(?P<year>(19|20)\d{2})(?:[^.]+)[,.])?"  # optional
    VOLUME = r"(?:\s(?P<volume>\d+(\(\d+\))))?"  # optional
    PAGE = r"(?:\: p\. (?P<page>[0-9e.]+(?:\-[0-9e.]+)?))?"  # optional

    return ALL_AUTHORS + TITLE + JOURNAL + YEAR + VOLUME + PAGE


def ref_regex_simple():
    """Return regex query to extract authors and title from reference."""
    FIRST_AUTHOR = r"(?P<first_author>[A-Z][\w\-']+(?:,\s(?:[A-Z]\.)+))"
    SECOND_AUTHOR = r"(?P<other_author>(?:[A-Z]\.)+\s[A-Z][\w\-']+)"
    ET_AL = r"et al\."
    BETWEEN_AUTHORS = r"(?:(?:[,]?\sand\s)|(?:\,\s))"
    ALL_AUTHORS = (
        r"(?:(?P<authors>"
        + FIRST_AUTHOR
        + r"(?:(?:"
        + BETWEEN_AUTHORS
        + SECOND_AUTHOR
        + r")+|(?:"
        + BETWEEN_AUTHORS
        + ET_AL
        + r"))?)\,\s)?"
    )  # optional
    TITLE = r"(?P<title>[^.]+[\.]?)"

    return r"^" + ALL_AUTHORS + TITLE


def extract_valid_query(string):
    """Valid query either contains title, doi or url."""
    DOI_REGEX = r"10.\d{4,9}\/[-._;()\/:a-zA-Z0-9]+"
    URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    REF_REGEX = ref_regex_simple()

    if (mo := re.search(DOI_REGEX, string)) is not None:
        query = mo.group()
        logging.debug(f"{query} is DOI.")
    elif (mo := re.search(URL_REGEX, string)) is not None:
        query = mo.group()
        logging.debug(f"{query} is URL.")
    elif (mo := re.search(REF_REGEX, string)) is not None:
        query = mo.group("title")
        logging.debug(f"{query} is title.")
    else:
        return None

    return query


def valid_fn(path, fn_name):
    """Shorten file name in case it exceeds system's maximum length."""
    PC_PATH_MAX = os.pathconf("/", "PC_PATH_MAX") - 4
    PC_NAME_MAX = os.pathconf("/", "PC_NAME_MAX") - 4
    full_len = len(path + fn_name)

    if full_len > os.pathconf("/", "PC_PATH_MAX"):
        logging.debug("Path too long. Will shorten.")
        fn_name = fn_name[0 : (PC_PATH_MAX - full_len)]
    if len(fn_name) > PC_NAME_MAX:
        logging.debug("File name too long. Will shorten.")
        fn_name = fn_name[0 : (PC_NAME_MAX - len(fn_name))]

    return fn_name