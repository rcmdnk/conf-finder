from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing import Any


CONF_TYPE = Literal['both', 'dir', 'file']
EXT = Literal['', 'toml', 'yaml', 'yml', 'json']


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
    conf_type: Literal["both", "dir", "file"]
        Type of the configuration place. Defaults to 'both' to search for both
        the directory and the file with the name by conf function. If 'dir' is
        given, only the directory is searched for. If 'file' is given, only the
        file is searched for.

    """

    name: str
    search_dir_list: list[str] = field(
        default_factory=lambda: ['cwd', 'git_root', 'xdg_config_home', 'home'],
    )
    non_dot_dir: list[str] = field(default_factory=lambda: ['xdg_config_home'])
    default_dir: str = 'xdg_config_home'
    conf_type: CONF_TYPE = 'both'

    def __post_init__(self) -> None:
        """Post initialization."""
        if self.conf_type not in ['both', 'dir', 'file']:
            msg = f'Invalid conf_type: {self.conf_type}'
            raise ValueError(msg)

        self._default_dir: Path
        self._search_dir_list: list[Path]
        self._non_dot_dir_list: list[Path]
        self.set_default_dir(self.default_dir)
        self.set_search_dir_list(self.search_dir_list)
        self.set_non_dot_dir_list(self.non_dot_dir)

    def get_dir_path(self, dir_name: str) -> Path | None:
        name = dir_name.lower()
        if name == 'cwd':
            return self.cwd()
        if name in ['git_root', 'git']:
            return self.git_root()
        if name in ['xdg_config_home', 'xdg']:
            return self.xdg_config_home()
        if name == 'home':
            return self.home()
        return Path(dir_name)

    def set_default_dir(self, default_dir: str) -> None:
        if (path := self.get_dir_path(default_dir)) is None:
            if default_dir in ['git_root', 'git']:
                msg = 'Git repository is not found.'
                raise ValueError(msg)
            msg = f'Invalid default_dir: {default_dir}'
            raise ValueError(msg)
        self._default_dir = path

    def get_dir_list(self, dir_list: list[str]) -> list[Path]:
        return [y for x in dir_list if (y := self.get_dir_path(x)) is not None]

    def set_search_dir_list(self, search_dir_list: list[str]) -> None:
        self._search_dir_list = self.get_dir_list(search_dir_list)
        if not self._search_dir_list:
            msg = 'search_dir_list is empty.'
            raise ValueError(msg)

    def set_non_dot_dir_list(self, non_dot_dir: list[str]) -> None:
        self._non_dot_dir_list = self.get_dir_list(non_dot_dir)
        if not self._non_dot_dir_list:
            msg = 'non_dot_dir is empty.'
            raise ValueError(msg)

    @staticmethod
    def cwd() -> Path:
        """Get the current working directory."""
        return Path.cwd()

    @staticmethod
    def git_root() -> Path | None:
        """Get the root directory of the git repository."""
        from git import InvalidGitRepositoryError, Repo

        try:
            repo = Repo('.', search_parent_directories=True)
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

        return Path(os.getenv('XDG_CONFIG_HOME', '~/.config')).expanduser()

    def find_directory(
        self,
        file: str = '',
        return_default: bool = True,
    ) -> Path | None:
        """Find the directory for the configuration files.

        Parameters
        ----------
        file: str
            If file is given, the directory with the file will be returned.
        return_default: bool
            If True, the default directory is returned if no directory is found.

        Returns
        -------
        directory_path: Path | None
            The configuration directory path.

        """
        for d in self._search_dir_list:
            if d in self._non_dot_dir_list:
                path = d / self.name
            else:
                path = d / ('.' + self.name)
            if path.is_dir() and (not file or (path / file).is_file()):
                return path
        if return_default:
            if self._default_dir in self._non_dot_dir_list:
                return self._default_dir / self.name
            return self._default_dir / ('.' + self.name)
        return None

    def directory(
        self,
        file: str = '',
        return_default: bool = True,
    ) -> Path | None:
        """Alias of find_directory."""
        return self.find_directory(file, return_default)

    def find_file(self, file: str, return_default: bool = True) -> Path | None:
        """Find the configuration file.

        Parameters
        ----------
        file: str
            File name with extension, not dot-prefixed.
        return_default: bool
            Set False to return None if any file is found. If True, default
            file path is returned if no file is found.

        Returns
        -------
        file_path: Path | None
            The configuration file path.

        """
        for d in self._search_dir_list:
            if d in self._non_dot_dir_list:
                path = d / file
            else:
                path = d / ('.' + file)

            if path.is_file():
                return path
        if return_default:
            if self._default_dir in self._non_dot_dir_list:
                return self._default_dir / file
            return self._default_dir / ('.' + file)
        return None

    def conf(self, ext: EXT = '', file_name: str = '') -> Path:
        """Find the configuration file.

        Parameters
        ----------
        ext: Literal["", "toml", "yaml", "yml", "json"]
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
        if self.conf_type in ['both', 'file']:
            file = file_name if file_name else self.name
            if ext:
                file += '.' + ext
            path = self.find_file(
                file,
                return_default=(self.conf_type == 'file'),
            )
            if path is not None:
                return path

        file = file_name if file_name else 'conf'
        if ext:
            file += '.' + ext
        parent = self.find_directory(
            file,
            return_default=True,
        )
        if parent is None:
            msg = f'Configuration file not found: {file}'
            raise FileNotFoundError(msg)
        return parent / file

    def read(self, ext: EXT = '', file_name: str = '') -> dict[Any, Any]:
        """Find the configuration file and read it.

        Parameters
        ----------
        ext: Literal["", "toml", "yaml", "yml", "json"]
            The extension of the configuration file. Only 'toml', 'yaml', 'yml'
            and 'json' are allowed. For other types, use `conf` to get the file
            path and read it directly.
        file_name: str
            The name (without extension) of the configuration file. If
            file_name is not given, '.conf' (or 'conf' for non_dot_dir) will be
            used for files directly under the base directories. For files under
            the configuration directories, self.name is used.

        Returns
        -------
        data: dict
            The dict object read from the configuration file.

        """
        conf_path = self.conf(ext, file_name)
        if ext == 'toml':
            import sys

            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
            with conf_path.open('rb') as f:
                return tomllib.load(f)
        elif ext in ['yaml', 'yml']:
            import yaml

            with conf_path.open() as f:
                return yaml.safe_load(f)
        elif ext == 'json':
            import json

            with conf_path.open() as f:
                return json.load(f)
        else:
            msg = f'Unsupported file extension: {ext}'
            raise ValueError(msg)
