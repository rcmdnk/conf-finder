# conf-finder

[![test](https://github.com/rcmdnk/conf-finder/actions/workflows/test.yml/badge.svg)](https://github.com/rcmdnk/conf-finder/actions/workflows/test.yml)
[![test coverage](https://img.shields.io/badge/coverage-check%20here-blue.svg)](https://github.com/rcmdnk/conf-finder/tree/coverage)

Configuration file finder.

The configuration file/directory is searched for in the following locations by default:

- The current directory
- Git root repository (if the current directory is within a repository)
- XDG config home (`$XDG_CONFIG_HOME`; if not set, **~/.config** is used)
- Home directory

To locate the configuration directory, the tool searches for a dot-prefixed
name (e.g., .**mytool**) in all locations except for the XDG config home.
Within the XDG config home, a name without the dot prefix (e.g., **mytool**)
is searched for.

If no directory is found, the path under the XDG config home is returned.

To locate the configuration file, the tool first searches for a dot-prefixed
file (e.g., **.myconf.txt**) in all locations except for the XDG config home.
Within the XDG config home, a file name without the dot prefix
(e.g., **myconf.txt**) is searched for. Following this, an attempt is made
to find the file within the located configuration directories.

If no file is found, the path under the configuration directory within
the XDG config home is returned.

## Requirement

- Python 3.9, 3.10, 3.11

## Installation

```bash
$ pip install conf-finder
```

## Usage

```python
from conf_finder import ConfFinder


cf = ConfFinder("mytool")
print(cf.directory())
```

This script searches for:

- **./.mytool**
- **<Git root directory>/.mytool** if here is under the git repository.
- **$XDG_CONFIG_HOME/mytool** (If `XDG_CONFIG_HOME` is not set, use `~/.config`.)
- **~/.mytool**

If no directory is found, return `$XDG_CONFIG_HOME/mytool` (or `~/.config/mytool`).

```python
from conf_finder import ConfFinder


cf = ConfFinder("mytool")
print(cf.conf(exe="toml"))
```

This script searches for:

- **./.mytool.toml**
- **<Git root directory>/.mytool.toml** if here is under the git repository.
- **$XDG_CONFIG_HOME/mytool.toml** (If `XDG_CONFIG_HOME` is not set, use `~/.config`.)
- **~/.mytool.toml**
- **./.mytool/conf.toml**
- **<Git root directory>/.mytool/conf.toml**
- **$XDG_CONFIG_HOME/mytool/conf.toml**
- **~/.mytool/conf.toml**

```python
from conf_finder import ConfFinder


cf = ConfFinder("mytool")
print(cf.conf("mytool", "toml", "myconf"))
```

This script searches for:

- **./.myconf.toml**
- **<Git root directory>/.myconf.toml**
- **$XDG_CONFIG_HOME/myconf.toml**
- **~/.myconf.toml**
- **./.mytool/myconf.toml**
- **<Git root directory>/.mytool/myconf.toml**
- **$XDG_CONFIG_HOME/mytool/myconf.toml**
- **~/.mytool/myconf.toml**

If you wish to search for only files directly placed under the search directories,
`conf_type` to `'file'`:

```python
from conf_finder import ConfFinder


cf = ConfFinder("mytool", conf_type="file")
print(cf.conf("mytool", "toml", "myconf"))
```

This script searches for:

- **./.myconf.toml**
- **<Git root directory>/.myconf.toml**
- **$XDG_CONFIG_HOME/myconf.toml**
- **~/.myconf.toml**

If no file is found, **$XDG_CONFIG_HOME/myconf.toml** is returned.

To search for only directories, `conf_type` to `'dir'` instead.
