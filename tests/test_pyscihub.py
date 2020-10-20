#!/usr/bin/env python

"""Tests for `pyscihub` package."""


import pytest
import re
import shutil
import csv
from click.testing import CliRunner
from pathlib import Path

from pyscihub import pyscihub
from pyscihub import cli
from pyscihub import tools


TEST_REFERENCES = [
    {
        "query": "A heuristic algorithm for a single vehicle static bike sharing rebalancing problem",
        "authors": None,
        "title": "A heuristic algorithm for a single vehicle static bike sharing rebalancing problem",
    },
    {
        "query": "Iterated local search: Framework and applications",
        "authors": None,
        "title": "Iterated local search: Framework and applications",
    },
    {
        "query": "Fong, C.Y., et al., Chloral hydrate as a sedating agent for neurodiagnostic procedures in children. Cochrane Database of Systematic Reviews, 2017. 2017(11).",
        "authors": "Fong, C.Y., et al.",
        "title": "Chloral hydrate as a sedating agent for neurodiagnostic procedures in children.",
    },
    {
        "query": "Forbes, H., et al., The Effects of Group Membership on College Students' Social Exclusion of Peers and Bystander Behavior. Journal of Psychology, 2020. 154(1): p. 15-37.",
        "authors": "Forbes, H., et al.",
        "title": "The Effects of Group Membership on College Students' Social Exclusion of Peers and Bystander Behavior.",
    },
    {
        "query": 'Force, S., The "innocent bystander" complications following esophagectomy: Atrial fibrillation, recurrent laryngeal nerve injury, chylothorax, and pulmonary complications. Seminars in Thoracic and Cardiovascular Surgery, 2004. 16(2): p. 117-123.',
        "authors": "Force, S.",
        "title": 'The "innocent bystander" complications following esophagectomy: Atrial fibrillation, recurrent laryngeal nerve injury, chylothorax, and pulmonary complications.',
    },
    {
        "query": "Forfar, J.C., D.C. Russell, and M.F. Oliver, Haemodynamic effects of sulphinpyrazone on exercise responses in normal subjects. Lancet, 1980. 2(8197): p. 718-20.",
        "authors": "Forfar, J.C., D.C. Russell, and M.F. Oliver",
        "title": "Haemodynamic effects of sulphinpyrazone on exercise responses in normal subjects.",
    },
    {
        "query": "Fornes, P. and D. Lecomte, Pathology of sport-related sudden death. [French]. Revue du Praticien, 2001. 51(SPEC.ISS): p. 31-35.",
        "authors": "Fornes, P. and D. Lecomte",
        "title": "Pathology of sport-related sudden death.",
    },
    {
        "query": "Freedenberg, V.A., P.S. Hinds, and E. Friedmann, Mindfulness-Based Stress Reduction and Group Support Decrease Stress in Adolescents with Cardiac Diagnoses: A Randomized Two-Group Study. Pediatric Cardiology, 2017. 38(7): p. 1415-1425.",
        "authors": "Freedenberg, V.A., P.S. Hinds, and E. Friedmann",
        "title": "Mindfulness-Based Stress Reduction and Group Support Decrease Stress in Adolescents with Cardiac Diagnoses: A Randomized Two-Group Study.",
    },
]

TEST_QUERIES = [
    {
        "query": "Lourenço, H. R., Martin, O. C., & Stützle, T. (2010). Iterated Local Search: Framework and Applications. International Series in Operations Research & Management Science, 363–397. doi:10.1007/978-1-4419-1665-5_12",
        "clean_query": "10.1007/978-1-4419-1665-5_12",
    },
    {
        "query": "Cruz, F., Subramanian, A., Bruck, B. P., & Iori, M. (2017). A heuristic algorithm for a single vehicle static bike sharing rebalancing problem. Computers & Operations Research, 79, 19–33. doi:10.1016/j.cor.2016.09.025",
        "clean_query": "10.1016/j.cor.2016.09.025",
    },
    {
        "query": "https://www.sciencedirect.com/science/article/abs/pii/S0305054816302489",
        "clean_query": "https://www.sciencedirect.com/science/article/abs/pii/S0305054816302489",
    },
]


@pytest.mark.parametrize("test_ref", TEST_REFERENCES)
def test_reference_regex(test_ref):
    """Test if regex for references correctly captures the title (and authors)."""

    # set REGEX
    REF_REGEX = tools.ref_regex_simple()

    mo = re.search(REF_REGEX, test_ref["query"])
    assert mo.group("authors") == test_ref["authors"]
    assert mo.group("title") == test_ref["title"]


@pytest.mark.parametrize("test_query", TEST_QUERIES)
def test_doi_and_url_regex(test_query):
    """Test that query parser correctly captures DOIs and URLs."""
    assert test_query["clean_query"] == tools.extract_valid_query(test_query["query"])


@pytest.fixture
def init_empty_scihub(tmpdir):
    test_output_path = tmpdir.mkdir("output")
    return pyscihub.SciHub("https://sci-hub.se", test_output_path.realpath())


@pytest.fixture
def init_populated_scihub(tmpdir):
    # create new folder and move data from tests/data/demo_pdfs
    test_output_path = Path(tmpdir.mkdir("output"))
    demo_path = Path("data/demo_pdfs")
    demo_files = [
        demo_file for demo_file in Path(demo_path).iterdir() if demo_file.is_file()
    ]
    for demo_file in demo_files:
        shutil.copy2(demo_file, test_output_path)

    # initiate scihub
    scihub = pyscihub.SciHub("https://sci-hub.se", str(test_output_path.absolute()))

    # change file location of pdfs
    lines = list(csv.reader(open(test_output_path / "pdf_paths.csv", "r")))
    for line in lines[1:]:
        print(line[1])
        line[1] = f"{tmpdir.realpath()}/{line[1]}"
        print(line[1])
    writer = csv.writer(open(test_output_path / "pdf_paths.csv", "w"))
    writer.writerows(lines)

    return scihub


def test_download_arg_type(init_empty_scihub):
    """Test something."""
    scihub = init_empty_scihub

    with pytest.raises(ValueError) as excinfo:
        scihub.download(set("abc"))
        assert "queries argument should be a list or a single string." in excinfo.value


def test_empty_pdf_path(init_empty_scihub):
    """Test that pdf_paths dictionary is indeed empty."""
    scihub = init_empty_scihub

    pdf_paths = scihub.get_pdf_paths()
    assert type(pdf_paths) == dict
    assert len(pdf_paths) == 0


def test_populated_pdf_paths(init_populated_scihub):
    """Test that pdf_paths contains pdf_paths of entries in CSV AND actual files."""
    scihub = init_populated_scihub

    pdf_paths = scihub.get_pdf_paths()
    print(pdf_paths)
    assert pdf_paths[
        "A heuristic algorithm for a single vehicle static bike sharing rebalancing problem"
    ]
    assert pdf_paths[
        "Forbes, H., et al., The Effects of Group Membership on College Students' Social Exclusion of Peers and Bystander Behavior. Journal of Psychology, 2020. 154(1): p. 15-37."
    ]
    with pytest.raises(KeyError) as excinfo:
        pdf_paths[
            "Foo, B., et al., hERG quality control and the long QT syndrome. Journal of Physiology, 2016. 594(9): p. 2469-81."
        ]
        assert (
            "KeyError: 'Foo, B., et al., hERG quality control and the long QT syndrome. Journal of Physiology, 2016. 594(9): p. 2469-81.'"
            in excinfo.value
        )


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    # check if main program shows all commands
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert "cli [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "file" in result.output
    assert "single" in result.output

    # check if help flag is properly configured
    help_result = runner.invoke(cli.cli, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message" in help_result.output
