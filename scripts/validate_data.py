"""Validate processed dataset row counts and sample records."""

from app.services.data_loader import DataLoader


def main() -> None:
    loader = DataLoader()
    df = loader.load()
    store = loader.get_restaurant_store()

    print(f"Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Valid rating: {df['rating'].notna().mean() * 100:.1f}%")
    print(f"Valid cost: {df['cost_for_two'].notna().mean() * 100:.1f}%")
    print(f"Locations: {len(store.get_locations())}")
    print(f"Cuisines: {len(store.get_cuisines())}")

    sample = next(store.iter_restaurants())
    print("Sample restaurant:", sample.model_dump())


if __name__ == "__main__":
    main()
