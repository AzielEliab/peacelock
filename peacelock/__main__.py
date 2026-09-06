"""Allow ``python -m peacelock`` to invoke the CLI."""

from peacelock.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
