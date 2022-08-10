"""Command line tool to fetch the Asset Code of the Pi."""

from srobo_pitools import AssetCode

def main() -> None:
    ac = AssetCode()
    print(ac.get_asset_code())

if __name__ == "__main__":
    main()
