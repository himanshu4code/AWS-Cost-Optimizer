"""Backward-compatible wrapper for the CLI script in scripts/cost_optimizer.py."""

from scripts.cost_optimizer import main


if __name__ == '__main__':
    raise SystemExit(main())
