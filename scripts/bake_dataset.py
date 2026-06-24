"""Pre-process and cache the restaurant dataset at deploy/build time (Railway)."""

from app.services.data_loader import DataLoader


def main() -> None:
    loader = DataLoader()
    df = loader.load()
    print(f"Baked dataset: {len(df)} restaurants -> {loader.cache_path}")


if __name__ == "__main__":
    main()
