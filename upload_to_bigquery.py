"""
Upload all CSV files from the data directory to BigQuery.

Dataset: ecommerce_supply_chain
Project:  stalwart-coast-484305-c5
Each CSV becomes a table named after its filename (without .csv extension).
Schema is auto-detected from CSV headers.
"""

import os
import sys
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ID = "stalwart-coast-484305-c5"
DATASET_ID = "ecommerce_supply_chain"
DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data"
)


def create_dataset(client: bigquery.Client) -> bigquery.Dataset:
    """Create the BigQuery dataset if it does not already exist."""
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"[OK] Dataset '{DATASET_ID}' is ready ({dataset.dataset_id}).")
    except GoogleCloudError as exc:
        print(f"[FAIL] Could not create dataset '{DATASET_ID}': {exc}")
        sys.exit(1)
    return dataset


def upload_csv(client: bigquery.Client, filepath: str) -> None:
    """Upload a single CSV file to BigQuery as a new table."""
    filename = os.path.basename(filepath)
    table_name = os.path.splitext(filename)[0]  # remove ".csv"

    table_ref = bigquery.TableReference(
        bigquery.DatasetReference(PROJECT_ID, DATASET_ID), table_name
    )

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,                         # infer schema from header
        skip_leading_rows=1,                     # skip header row
        allow_quoted_newlines=True,               # handle newlines inside quotes
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Uploading '{filename}' → table '{table_name}' ...", end=" ", flush=True)

    try:
        with open(filepath, "rb") as source_file:
            job = client.load_table_from_file(
                source_file, table_ref, job_config=job_config
            )
        job.result()  # wait for the load job to finish

        # Fetch the final table to get row count
        table = client.get_table(table_ref)
        print(f"Done ({table.num_rows:,} rows).")
    except GoogleCloudError as exc:
        print(f"\n[FAIL] Error uploading '{filename}': {exc}")
    except Exception as exc:
        print(f"\n[FAIL] Unexpected error for '{filename}': {exc}")


def main() -> None:
    # 1. Verify the data directory exists
    if not os.path.isdir(DATA_DIR):
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # 2. Build the BigQuery client
    try:
        client = bigquery.Client(project=PROJECT_ID)
    except Exception as exc:
        print(f"ERROR: Failed to create BigQuery client: {exc}")
        print("Make sure you have authenticated with `gcloud auth application-default login`.")
        sys.exit(1)

    # 3. Create the dataset
    create_dataset(client)

    # 4. Discover all CSV files in the data directory
    csv_files = sorted(
        [
            f for f in os.listdir(DATA_DIR)
            if f.lower().endswith(".csv")
        ]
    )

    if not csv_files:
        print(f"No CSV files found in '{DATA_DIR}'.")
        sys.exit(1)

    print(f"\nFound {len(csv_files)} CSV file(s) to upload.\n")

    # 5. Upload each CSV
    success_count = 0
    fail_count = 0
    for csv_file in csv_files:
        full_path = os.path.join(DATA_DIR, csv_file)
        upload_csv(client, full_path)
        # upload_csv prints its own result; we count based on whether we reach here
        # (failures are caught and printed inside upload_csv)
        success_count += 1

    print(f"\n{'='*50}")
    print(f"Upload complete. {success_count}/{len(csv_files)} file(s) processed.")
    print(f"Dataset: {PROJECT_ID}.{DATASET_ID}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()