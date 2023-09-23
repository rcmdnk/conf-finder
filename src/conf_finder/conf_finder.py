from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConfFinder:
    """Configuration file finder.

    Parameters
    ----------
    name : str
        Name of the configuration directory or file.
    search_dir_list : list[str]
        List of base directories to search for the configuration directory or
        file, in the order specified. By default, a search is done in the
        following order: current directory, git root directory, XDG config home
        directory, and the Home directory.
    non_dot_dir : list[str]
        List of base directories to search for non-dot configuration
        directories or files, in the order specified.
        By default, XDG config home is in the list.
    default_dir: str
        Default base directory used if no directory is found.
        Defaults to XDG config home.
    """

    name: str
    search_dir_list: list[str] = field(
        default_factory=lambda: ["cwd", "git_root", "xdg_config_home", "home"]
    )
    non_dot_dir: list[str] = field(default_factory=lambda: ["xdg_config_home"])
    default_dir: str = "xdg_config_home"

    def __post_init__(self) -> None:
        """Post initialization."""
        self._default_dir: Path
        self._search_dir_list: list[Path]
        self._non_dot_dir_list: list[Path]
        self.set_default_dir(self.default_dir)
        self.set_search_dir_list(self.search_dir_list)
        self.set_non_dot_dir_list(self.non_dot_dir)

    def get_dir_path(self, dir_name: str) -> Path | None:
        match dir_name.lower():
            case "cwd":
                return self.cwd()
            case "git_root" | "git":
                return self.git_root()
            case "xdg_config_home" | "xdg":
                return self.xdg_config_home()
            case "home":
                return self.home()
            case _:
                return Path(dir_name)

    def set_default_dir(self, default_dir: str) -> None:
        if (path := self.get_dir_path(default_dir)) is None:
            if default_dir in ["git_root", "git"]:
                raise ValueError("Git repository is not found.")
            raise ValueError(f"Invalid default_dir: {default_dir}")
        self._default_dir = path

    def get_dir_list(self, dir_list: list[str]) -> list[Path]:
        return [y for x in dir_list if (y := self.get_dir_path(x)) is not None]

    def set_search_dir_list(self, search_dir_list: list[str]) -> None:
        self._search_dir_list = self.get_dir_list(search_dir_list)
        if not self._search_dir_list:
            raise ValueError("search_dir_list is empty.")

    def set_non_dot_dir_list(self, non_dot_dir: list[str]) -> None:
        self._non_dot_dir_list = self.get_dir_list(non_dot_dir)
        if not self._non_dot_dir_list:
            raise ValueError("non_dot_dir is empty.")

    @staticmethod
    def cwd() -> Path:
        """Get the current working directory."""
        return Path.cwd()

    @staticmethod
    def git_root() -> Path | None:
        """Get the root directory of the git repository."""
        from git import InvalidGitRepositoryError, Repo

        try:
            repo = Repo(".", search_parent_directories=True)
            return (
                Path(repo.working_tree_dir) if repo.working_tree_dir else None
            )
        except InvalidGitRepositoryError:
            return None

    @staticmethod
    def home() -> Path:
        """Get the home directory."""
        return Path.home()

    @staticmethod
    def xdg_config_home() -> Path:
        """Get the XDG config home directory."""
        import os

        return Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()

    def directory(self, file: str = "") -> Path:
        """Find the directory for the configuration files.

        Parameters
        ----------
        file: str
            If file is given, the directory with the file will be returned.

        Returns
        -------
        path: Path
            The configuration directory path.
        """
        for d in self._search_dir_list:
            if d in self._non_dot_dir_list:
                path = d / self.name
            else:
                path = d / ("." + self.name)
            if path.is_dir():
                if not file or (path / file).is_file():
                    return path
        if self._default_dir in self._non_dot_dir_list:
            return self._default_dir / self.name
        return self._default_dir / ("." + self.name)

    def conf(self, ext: str = "", file_name: str = "") -> Path:
        """Find the configuration file.

        Parameters
        ----------
        ext: str
            The extension of the configuration file.
        file_name: str
            The name (without extension) of the configuration file. If
            file_name is not given, '.conf' (or 'conf' for non_dot_dir) will be
            used for files directly under the base directories. For files under
            the configuration directories, self.name is used.

        Returns
        -------
        path: Path
            The configuration file path.
        """
        file = file_name if file_name else self.name
        if ext:
            file += "." + ext

        for d in self._search_dir_list:
            if d in self._non_dot_dir_list:
                path = d / file
            else:
                path = d / ("." + file)

            if path.is_file():
                return path

        file = file_name if file_name else "conf"
        if ext:
            file += "." + ext

        for d in self._search_dir_list:
            if d in self._non_dot_dir_list:
                path = d / self.name / file
            else:
                path = d / ("." + self.name) / file

            if path.is_file():
                return path

        if self._default_dir in self._non_dot_dir_list:
            return self._default_dir / self.name / file
        return self._default_dir / ("." + self.name) / file
