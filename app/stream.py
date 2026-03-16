import orjson
import ijson


def stream_events(path):

    with open(path,"rb") as f:

        first=f.read(1)

        f.seek(0)

        if first==b"[":

            parser=ijson.items(f,"item")

            for event in parser:
                yield event

        else:

            for line in f:

                if not line.strip():
                    continue

                yield orjson.loads(line)