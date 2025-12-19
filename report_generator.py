from datetime import datetime


def generate_text_report(
    prod_file_name: str,
    test_file_name: str,
    transaction: str,
    diffs: list
):
    lines = []

    lines.append("=" * 60)
    lines.append("            X12 FILE COMPARISON REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"PROD File : {prod_file_name}")
    lines.append(f"TEST File : {test_file_name}")
    lines.append("")
    lines.append(f"Transaction Set : {transaction}")
    lines.append(f"Comparison Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-" * 60)

    if not diffs:
        lines.append("")
        lines.append("RESULT : PASS")
        lines.append("------------------------------------------------------------")
        lines.append("")
        lines.append("No differences detected between PROD and TEST files.")
        lines.append("All segments and elements match exactly.")
    else:
        for d in diffs:
            lines.append("")
            lines.append(f"Segment Pos : {d.get('segment_pos', '-')}")
            lines.append(f"Segment ID  : {d.get('segment', '-')}")
            lines.append(f"Difference  : {d.get('difference', d.get('type'))}")
            if "prod_value" in d:
                lines.append(f"PROD Value  : {d['prod_value']}")
            if "test_value" in d:
                lines.append(f"TEST Value  : {d['test_value']}")
            lines.append("-" * 60)

        lines.append("")
        lines.append("RESULT : FAIL")
        lines.append(f"Total Differences Found : {len(diffs)}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    return "\n".join(lines)
