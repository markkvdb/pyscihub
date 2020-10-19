"""Tools for handling queries."""

import re


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
    TITLE = r"(?P<title>[^.]+[\.]?)"

    return r"^" + ALL_AUTHORS + TITLE


def extract_valid_query(string):
    """Valid query either contains title, doi or url."""
    DOI_REGEX = r"10.\d{4,9}\/[-._;()\/:A-Z0-9]+"
    URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    REF_REGEX = ref_regex_simple()

    if (mo := re.search(DOI_REGEX, string)) is not None:
        query = mo.group()
    elif (mo := re.search(URL_REGEX, string)) is not None:
        query = mo.group()
    elif (mo := re.search(REF_REGEX, string)) is not None:
        query = mo.group("title")
    else:
        return None

    return query