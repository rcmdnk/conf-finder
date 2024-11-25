from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from conf_finder import __version__


def test_version():
    with open(Path(__file__).parents[1] / "pyproject.toml", "rb") as f:
        version = tomllib.load(f)["project"]["version"]
    assert version == __version__
