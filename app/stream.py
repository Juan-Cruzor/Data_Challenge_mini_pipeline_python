import orjson
import ijson


def stream_events(path):
    """Function that streams the json objects
      one by one so it can handle large files without loading them entirely into memory."""

    # It reads the bytes.
    with open(path,"rb") as f:

        first=f.read(1)

        f.seek(0)
        # The first byte of a Json file would be a [ bracket.]
        if first == b"[":

            parser=ijson.items(f,"item")

            for event in parser:
                yield event

        else:

            for line in f:
                # Skips the empty lines.
                if not line.strip():
                    continue

                yield orjson.loads(line)