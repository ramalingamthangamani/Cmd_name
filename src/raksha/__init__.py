"""raksha -- a small terminal experience.

Everything personal lives in ``raksha.messages``.
"""

__version__ = "1.0.0"
__all__ = ["__version__", "main"]


def main():
    """Lazy re-export so ``python -c "import raksha; raksha.main()"`` works."""
    from .cli import main as _main

    return _main()
