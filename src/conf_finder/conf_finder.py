import os
from pathlib import Path


def cwd() -> Path:
    """Get the current working directory."""
    return Path.cwd()


def git_root() -> Path | None:
    """Get the root directory of the git repository."""
    from git import InvalidGitRepositoryError, Repo

    try:
        repo = Repo(".", search_parent_directories=True)
        return Path(repo.working_tree_dir) if repo.working_tree_dir else None
    except InvalidGitRepositoryError:
        return None


def home() -> Path:
    """Get the home directory."""
    return Path.home()


def xdg_config_home() -> Path:
    """Get the XDG config home directory."""
    return Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()


def directory(name: str, file: str = "") -> Path:
    """Find the directory for the configuration files.

    Parameters
    ----------
    name: str
        The name of the configuration directory. The directory name will be
        '.' + name for other than the XDG config home directory.
    file: str
        If the file is given, the directory with the file will be returned.

    Returns
    -------
    path: Path
        The directory path. The directory is searched in the current directory,
        git root directory, XDG config home directory and the Home directory.
        If the directory is not found, the directory under the XDG config home
        directory will be returned.
    """
    if (path := (cwd() / ("." + name))).is_dir():
        if not file or (path / file).is_file():
            return path
    if root := git_root():
        if (path := (root / ("." + name))).is_dir():
            if not file or (path / file).is_file():
                return path
    if (xdg_path := (xdg_config_home() / name)).is_dir():
        if not file or (xdg_path / file).is_file():
            return xdg_path
    if (path := (home() / ("." + name))).is_dir():
        if not file or (path / file).is_file():
            return path
        return path
    return xdg_path


def conf(name: str, ext: str = "txt", file_name: str = "") -> Path:
    """Find the configuration file.

    Parameters
    ----------
    name: str
        The name of the configuration directory or file name.
    ext: str
        The extension of the configuration file.
    file_name: str
        The name of the configuration file.

    Returns
    -------
    path: Path
        The configuration file path.
        First, the dot file will be searched in the current directory, git root
        directory, XDG config home directory  or the Home directory. The dot
        file name will be '.' + file_name + '.' + ext if file_name is given,
        otherwise, the dot file name will be
        '.' + name + '.' + ext. For XDG config home directory, the initial dot
        is dropped from the file name.
        If the dot file is not found, the file will be searched under the
        configuration directories. The file name will be file_name + '.' + ext
        if file_name is given, otherwise, the file name will be
        "conf" + '.' + ext. The configuration directories are the current
        directory, git root directory, XDG config home directory and the Home
        directory. If the file is not found, the file path in the XDG config
        home directory will be used.
    """
    file = file_name if file_name else name
    if ext:
        file += "." + ext
    if (path := (cwd() / ("." + file))).is_file():
        return path
    if root := git_root():
        if (path := (root / ("." + file))).is_file():
            return path
    if (path := (xdg_config_home() / file)).is_file():
        return path
    if (path := (home() / ("." + file))).is_file():
        return path

    file = file_name if file_name else "conf"
    if ext:
        file += "." + ext
    return directory(name, file) / file
