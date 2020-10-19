"""Console script for pyscihub."""
import sys
import logging
import click
from time import sleep
from random import gauss

from .pyscihub import SciHub


@click.group()
@click.option(
    "--output",
    "-o",
    help="Output path for PDFs",
    default="./output/",
    type=click.Path(exists=True),
)
@click.option("--verbose", is_flag=True)
@click.pass_context
def cli(ctx, output, verbose):
    """CLI to download PDFs from Sci-Hub."""
    ctx.ensure_object(dict)
    ctx.obj["OUTPUT"] = output
    ctx.obj["VERBOSE"] = verbose


@cli.command("file")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def make_file(ctx, file_path):
    scihub = SciHub("https://sci-hub.se", ctx.obj["OUTPUT"])

    # open file
    with open(file_path, "r") as f:
        queries = f.readlines()

    scihub.download(queries)


@cli.command("single")
@click.argument("query", type=str)
@click.pass_context
def make_query(ctx, query):
    scihub = SciHub("https://sci-hub.se", ctx.obj["OUTPUT"])
    scihub.download(query)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()  # pragma: no cover
