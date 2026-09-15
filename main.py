"""Application entry point for the ChEMBL ingestion job."""

from src.ingest_chembl import main


if __name__ == "__main__":
    raise SystemExit(main())
