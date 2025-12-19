def parse_x12(content: str):
    segments = []
    raw_segments = content.strip().split("~")

    for idx, raw in enumerate(raw_segments, start=1):
        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split("*")
        segments.append({
            "line": idx,
            "segment": parts[0],
            "elements": parts[1:]
        })

    return segments
