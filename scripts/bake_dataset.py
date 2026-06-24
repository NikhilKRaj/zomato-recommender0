"""Pre-process and cache the restaurant dataset at deploy/build time (Railway)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.data_loader import DataLoader


def main() -> None:
    loader = DataLoader()
    df = loader.load()
    print(f"Baked dataset: {len(df)} restaurants -> {loader.cache_path}")


if __name__ == "__main__":
    main()
