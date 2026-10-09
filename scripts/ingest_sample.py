"""Ingest sample documents to bootstrap the system."""
from pathlib import Path
from datetime import date
from src.ingestion.pipeline import ingest_batch
from src.models.schemas import DocumentMetadata, AccessLevel, SourceType


SAMPLES = [
    (
        Path("data/raw/refund_policy_v1.txt"),
        DocumentMetadata(
            doc_id="refund-v1",
            version="1.0",
            product="CloudBackup",
            region="US",
            access_level=AccessLevel.PUBLIC,
            effective_date=date(2023, 1, 1),
            expiry_date=date(2024, 1, 1),
            source_type=SourceType.POLICY,
            citation_label="CloudBackup Refund Policy v1.0 (2023)",
        ),
    ),
    (
        Path("data/raw/refund_policy_v2.txt"),
        DocumentMetadata(
            doc_id="refund-v2",
            version="2.0",
            product="CloudBackup",
            region="US",
            access_level=AccessLevel.PUBLIC,
            effective_date=date(2024, 1, 1),
            expiry_date=None,
            source_type=SourceType.POLICY,
            supersedes=["refund-v1"],
            citation_label="CloudBackup Refund Policy v2.0 (2024)",
        ),
    ),
]


if __name__ == "__main__":
    total = ingest_batch(SAMPLES)
    print(f"Ingested {total} chunks.")