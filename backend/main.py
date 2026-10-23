"""Command-line entry point: check the database connection and export training CSVs.

Run from the backend/ directory:
    python main.py check
    python main.py export
"""
import argparse

from db.connect import test_connection
from db.query import export_outlets_csv, export_warehouses_csv


def main():
    parser = argparse.ArgumentParser(description="SynapseSupply backend utilities")
    parser.add_argument("command", choices=["check", "export"])
    args = parser.parse_args()

    if args.command == "check":
        raise SystemExit(0 if test_connection() else 1)

    export_outlets_csv()
    export_warehouses_csv()


if __name__ == "__main__":
    main()
