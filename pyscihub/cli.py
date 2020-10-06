"""Console script for pyscihub."""
import sys
import click

from pyscihub import SciHub


@click.command()
def main(args=None):
    """Console script for pyscihub."""
    scihub = SciHub("https://sci-hub.se", "output")

    data = scihub.fetch_search(
        "A heuristic algorithm for a single vehicle static bike sharing rebalancing problem"
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
