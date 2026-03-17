import json

def stream_events(path):
    with open(path, "r") as f:
        first = f.read(1)
        f.seek(0)

        if first == "[":
            data = json.load(f)
            return data

       
        events = []
        for line in f:
            line = line.strip()

            if not line:
                continue

            # remove trailing comma (very common)
            if line.endswith(","):
                line = line[:-1]

            events.append(json.loads(line))

        return events