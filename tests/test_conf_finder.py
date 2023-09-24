from pathlib import Path

import pytest

from conf_finder import ConfFinder


@pytest.fixture
def cf(monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg")
    monkeypatch.setenv("HOME", "/home/user")
    return ConfFinder("mytool")


@pytest.fixture
def git_dir(tmp_path):
    git_dir = tmp_path / "git_dir"
    (git_dir / ".git").mkdir(parents=True)
    (git_dir / "test").mkdir(parents=True)
    (git_dir / ".git" / "objects").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "refs").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "refs").mkdir(parents=True, exist_ok=True)
    (git_dir / ".git" / "HEAD").touch()
    return git_dir


def test_get_dir_path_cwd(cf, monkeypatch, tmp_path):
    assert cf.get_dir_path("cwd") == Path(".").resolve()
    monkeypatch.chdir(tmp_path)
    assert cf.get_dir_path("cwd") == tmp_path


def test_get_dir_path_git(cf, monkeypatch, tmp_path, git_dir):
    monkeypatch.chdir(tmp_path)
    assert cf.get_dir_path("git") is None
    monkeypatch.chdir(git_dir / "test")
    assert cf.get_dir_path("git") == git_dir
    assert cf.get_dir_path("git_root") == git_dir


def test_get_dir_path_home(cf, monkeypatch):
    assert cf.get_dir_path("home") == Path.home()


def test_get_dir_path_xdg(cf, monkeypatch):
    assert cf.get_dir_path("xdg") == Path("/tmp/xdg")
    assert cf.get_dir_path("xdg_config_home") == Path("/tmp/xdg")
    assert cf.get_dir_path("XDG_CONFIG_HOME") == Path("/tmp/xdg")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert cf.get_dir_path("xdg") == Path("/home/user/.config")


def test_set_default_dir(cf, monkeypatch):
    cf.set_default_dir("/tmp/xdg")
    assert cf._default_dir == Path("/tmp/xdg")


def test_get_dir_list(cf):
    assert cf._search_dir_list[0] == Path(".").resolve()
    assert cf._search_dir_list[-2] == Path("/tmp/xdg")
    assert cf._search_dir_list[-1] == Path.home()
    assert cf._non_dot_dir_list == [Path("/tmp/xdg")]


def test_set_search_dir_list(cf):
    cf.set_search_dir_list(["a", "b"])
    assert cf._search_dir_list == [Path("a"), Path("b")]


def test_set_non_dot_dir_list(cf):
    cf.set_non_dot_dir_list(["a", "b"])
    assert cf._non_dot_dir_list == [Path("a"), Path("b")]


def test_cwd(cf):
    assert cf.cwd() == Path(".").resolve()


def test_git_root(cf, monkeypatch, tmp_path, git_dir):
    monkeypatch.chdir(tmp_path)
    assert cf.git_root() is None
    monkeypatch.chdir(git_dir / "test")
    assert cf.git_root() == git_dir


def test_home(cf):
    assert cf.home() == Path.home()


def test_xdg_config_home(cf):
    assert cf.xdg_config_home() == Path("/tmp/xdg")


def test_directory(cf, monkeypatch, tmp_path, git_dir):
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


def test_conf(cf, monkeypatch, git_dir):
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


def test_conf_conf_type(cf, monkeypatch, tmp_path):
    assert cf.conf() == cf.xdg_config_home() / "mytool" / "conf"
    cf.conf_type = "file"
    assert cf.conf() == cf.xdg_config_home() / "mytool"
    monkeypatch.chdir(tmp_path)
    cf.set_search_dir_list(cf.search_dir_list)
    (tmp_path / ".mytool.toml").touch()
    (tmp_path / ".mytool").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".mytool" / "conf.toml").touch()
    cf.conf_type = "both"
    assert cf.conf(ext="toml") == tmp_path / ".mytool.toml"
    cf.conf_type = "file"
    assert cf.conf(ext="toml") == tmp_path / ".mytool.toml"
    cf.conf_type = "dir"
    assert cf.conf(ext="toml") == tmp_path / ".mytool" / "conf.toml"
