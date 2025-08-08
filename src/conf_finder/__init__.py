from .conf_finder import CONF_TYPE, EXT, ConfFinder

__all__ = ['CONF_TYPE', 'EXT', 'ConfFinder', '__version__']


def __getattr__(name: str) -> str:
    if name == '__version__':
        from .version import __version__

        return __version__
    msg = f'module {__name__} has no attribute {name}'
    raise AttributeError(msg)
