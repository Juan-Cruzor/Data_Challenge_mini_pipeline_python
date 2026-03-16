import os
import pyarrow as pa
import pyarrow.parquet as pq


BASE_PATH = "./data/events"


def write_parquet(events):
    """
    Persist events to partitioned parquet files.
    """

    if not events:
        return

    table = pa.Table.from_pylist(events)

    for date in set(e["timestamp"].date() for e in events):

        folder = f"{BASE_PATH}/date={date}"
        os.makedirs(folder, exist_ok=True)

        mask = pa.compute.equal(
            table["timestamp"].cast(pa.date32()),
            pa.scalar(date)
        )

        pq.write_table(
            table.filter(mask),
            f"{folder}/part.parquet"
        )