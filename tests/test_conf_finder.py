from pathlib import Path

import pytest

from conf_finder import ConfFinder


@pytest.fixture
def cf(monkeypatch: pytest.MonkeyPatch) -> ConfFinder:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg")
    monkeypatch.setenv("HOME", "/home/user")
    return ConfFinder("mytool")


@pytest.fixture
def git_dir(tmp_path: Path) -> Path:
    git_dir = tmp_path / "git_dir"
    (git_dir / ".git").mkdir(parents=True)
    (git_dir / "test").mkdir(parents=True)
    (git_dir / ".git" / "objects").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "refs").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "refs").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "HEAD").touch()
    return git_dir


def test_get_dir_path_cwd(
    cf: ConfFinder, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert cf.get_dir_path("cwd") == Path.cwd()
    monkeypatch.chdir(tmp_path)
    assert cf.get_dir_path("cwd") == tmp_path


def test_get_dir_path_git(
    cf: ConfFinder,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    git_dir: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    assert cf.get_dir_path("git") is None
    monkeypatch.chdir(git_dir / "test")
    assert cf.get_dir_path("git") == git_dir
    assert cf.get_dir_path("git_root") == git_dir


def test_get_dir_path_home(cf: ConfFinder) -> None:
    assert cf.get_dir_path("home") == Path.home()


def test_get_dir_path_xdg(
    cf: ConfFinder, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert cf.get_dir_path("xdg") == Path("/tmp/xdg")
    assert cf.get_dir_path("xdg_config_home") == Path("/tmp/xdg")
    assert cf.get_dir_path("XDG_CONFIG_HOME") == Path("/tmp/xdg")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert cf.get_dir_path("xdg") == Path("/home/user/.config")


def test_set_default_dir(cf: ConfFinder) -> None:
    cf.set_default_dir("/tmp/xdg")
    assert cf._default_dir == Path("/tmp/xdg")


def test_get_dir_list(cf: ConfFinder) -> None:
    assert cf._search_dir_list[0] == Path.cwd()
    assert cf._search_dir_list[-2] == Path("/tmp/xdg")
    assert cf._search_dir_list[-1] == Path.home()
    assert cf._non_dot_dir_list == [Path("/tmp/xdg")]


def test_set_search_dir_list(cf: ConfFinder) -> None:
    cf.set_search_dir_list(["a", "b"])
    assert cf._search_dir_list == [Path("a"), Path("b")]


def test_set_non_dot_dir_list(cf: ConfFinder) -> None:
    cf.set_non_dot_dir_list(["a", "b"])
    assert cf._non_dot_dir_list == [Path("a"), Path("b")]


def test_cwd(cf: ConfFinder) -> None:
    assert cf.cwd() == Path.cwd()


def test_git_root(
    cf: ConfFinder,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    git_dir: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    assert cf.git_root() is None
    monkeypatch.chdir(git_dir / "test")
    assert cf.git_root() == git_dir


def test_home(cf: ConfFinder) -> None:
    assert cf.home() == Path.home()


def test_xdg_config_home(cf: ConfFinder) -> None:
    assert cf.xdg_config_home() == Path("/tmp/xdg")


def test_directory(
    cf: ConfFinder,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    git_dir: Path,
) -> None:
    assert cf.directory() == cf.xdg_config_home() / "mytool"
    (git_dir / ".mytool").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(git_dir)
    cf.set_search_dir_list(cf.search_dir_list)
    assert cf.directory() == git_dir / ".mytool"
    (tmp_path / ".mytool").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".mytool" / "config").touch()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    cf.set_search_dir_list(cf.search_dir_list)
    assert cf.directory("config") == tmp_path / ".mytool"
    (git_dir / ".mytool" / "config").touch()
    assert cf.directory("config") == git_dir / ".mytool"


def test_conf(
    cf: ConfFinder, monkeypatch: pytest.MonkeyPatch, git_dir: Path
) -> None:
    assert cf.conf() == cf.xdg_config_home() / "mytool" / "conf"
    assert cf.conf(ext="toml") == cf.xdg_config_home() / "mytool" / "conf.toml"
    assert (
        cf.conf(ext="toml", file_name="myconf")
        == cf.xdg_config_home() / "mytool" / "myconf.toml"
    )
    monkeypatch.chdir(git_dir / "test")
    cf.set_search_dir_list(cf.search_dir_list)
    (git_dir / ".mytool").mkdir()
    (git_dir / ".mytool" / "conf.toml").touch()
    assert cf.conf(ext="toml") == git_dir / ".mytool" / "conf.toml"
    (git_dir / "test" / ".mytool").mkdir()
    (git_dir / "test" / ".mytool" / "conf.toml").touch()
    assert cf.conf(ext="toml") == git_dir / "test" / ".mytool" / "conf.toml"
    (git_dir / "test" / ".mytool.toml").touch()
    assert cf.conf(ext="toml") == git_dir / "test" / ".mytool.toml"


def test_conf_conf_type(
    cf: ConfFinder, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert cf.conf() == cf.xdg_config_home() / "mytool" / "conf"
    cf.conf_type = "file"
    assert cf.conf() == cf.xdg_config_home() / "mytool"
    monkeypatch.chdir(tmp_path)
    cf.set_search_dir_list(cf.search_dir_list)
    types = ["toml", "yaml", "json"]
    (tmp_path / ".mytool").mkdir(parents=True, exist_ok=True)
    for t in types:
        (tmp_path / f".mytool.{t}").touch()
        (tmp_path / ".mytool" / f"conf.{t}").touch()
    cf.conf_type = "both"
    for t in types:
        assert cf.conf(ext=t) == tmp_path / f".mytool.{t}"
    cf.conf_type = "file"
    for t in types:
        assert cf.conf(ext=t) == tmp_path / f".mytool.{t}"
    cf.conf_type = "dir"
    for t in types:
        assert cf.conf(ext=t) == tmp_path / ".mytool" / f"conf.{t}"


def test_read(
    cf: ConfFinder, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    cf.set_search_dir_list(cf.search_dir_list)
    types = ["toml", "yaml", "json"]
    with (tmp_path / ".mytool.toml").open("w") as f:
        f.write("""[toml]
var1 = 1
""")
    with (tmp_path / ".mytool.yaml").open("w") as f:
        f.write("""---
yaml:
    var1: 1
""")
    with (tmp_path / ".mytool.json").open("w") as f:
        f.write('{"json": {"var1": 1}}')

    cf.conf_type = "file"
    for t in types:
        assert cf.read(ext=t) == {t: {"var1": 1}}
