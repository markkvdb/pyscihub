#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
    "beautifulsoup4>=4.0",
    "requests>=2.0",
]

setup_requirements = []

test_requirements = ["pytest>=6.0"]

setup(
    author="Mark van der Broek",
    author_email="markvanderbroek@gmail.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description="Command-line and Python API to download PDFs directly from Sci-Hub",
    entry_points={
        "console_scripts": [
            "pyscihub=pyscihub.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="pyscihub",
    name="pyscihub",
    packages=find_packages(include=["pyscihub", "pyscihub.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/markkvdb/pyscihub",
    version="0.1.1",
    zip_safe=False,
)
