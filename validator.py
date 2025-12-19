from collections import Counter
import json
import os

# ======================================================
# CONFIG
# ======================================================

ANCHOR_SEGMENTS = {"HL", "CTT", "SE"}

ISA_IGNORED_ELEMENTS = {8, 9, 12, 14}   # date, time, control#, usage
GS_IGNORED_ELEMENTS = {3, 4, 5}         # date, time, group control#

IGNORED_CONTROL_SEGMENTS = {"GE", "IEA"}

# ======================================================
# HELPERS
# ======================================================

def detect_transaction(segments):
    for s in segments:
        if s["segment"] == "ST" and s["elements"]:
            return s["elements"][0]
    return None


def load_rules(transaction):
    path = os.path.join("rules", f"{transaction}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


# ======================================================
# RULE VALIDATION (997 DECISION PHASE)
# ======================================================

def validate_segments(segments, rules):
    errors = []
    counts = Counter(s["segment"] for s in segments)

    # Mandatory segments → FATAL
    for seg in rules.get("mandatory_segments", []):
        if counts[seg] == 0:
            errors.append({
                "segment": seg,
                "difference": "MISSING_MANDATORY_SEGMENT",
                "severity": "FATAL"
            })

    # Max-use violations → ERROR
    for seg, max_allowed in rules.get("max_use", {}).items():
        if counts[seg] > max_allowed:
            errors.append({
                "segment": seg,
                "difference": "MAX_USE_EXCEEDED",
                "found": counts[seg],
                "allowed": max_allowed,
                "severity": "ERROR"
            })

    return errors


# ======================================================
# ANALYTICAL COMPARISON (NON-997)
# ======================================================

def compare_elements(prod_segments, test_segments):
    errors = []
    i = j = 0

    while i < len(prod_segments) and j < len(test_segments):
        prod = prod_segments[i]
        test = test_segments[j]
        seg = prod["segment"]

        # Fully ignored control trailers
        if seg in IGNORED_CONTROL_SEGMENTS and test["segment"] in IGNORED_CONTROL_SEGMENTS:
            i += 1
            j += 1
            continue

        # Segment match
        if prod["segment"] == test["segment"]:
            max_elems = max(len(prod["elements"]), len(test["elements"]))

            for idx in range(max_elems):
                if seg == "ISA" and idx in ISA_IGNORED_ELEMENTS:
                    continue
                if seg == "GS" and idx in GS_IGNORED_ELEMENTS:
                    continue

                pv = prod["elements"][idx] if idx < len(prod["elements"]) else ""
                tv = test["elements"][idx] if idx < len(test["elements"]) else ""

                if pv != tv:
                    errors.append({
                        "segment_pos": i + 1,
                        "segment": seg,
                        "difference": f"ELEMENT_{idx + 1}_MISMATCH",
                        "prod_value": pv,
                        "test_value": tv,
                        "severity": "ERROR"
                    })

            i += 1
            j += 1
            continue

        # Segment mismatch → anchor realignment
        errors.append({
            "segment_pos": i + 1,
            "segment": prod["segment"],
            "difference": "SEGMENT_ID_MISMATCH",
            "prod_value": prod["segment"],
            "test_value": test["segment"],
            "severity": "ERROR"
        })

        prod_anchor = next(
            (x for x in range(i + 1, len(prod_segments))
             if prod_segments[x]["segment"] == test["segment"]
             and test["segment"] in ANCHOR_SEGMENTS),
            None
        )

        test_anchor = next(
            (y for y in range(j + 1, len(test_segments))
             if test_segments[y]["segment"] == prod["segment"]
             and prod["segment"] in ANCHOR_SEGMENTS),
            None
        )

        if prod_anchor is not None:
            i = prod_anchor
        elif test_anchor is not None:
            j = test_anchor
        else:
            i += 1
            j += 1

    return errors


# ======================================================
# MAIN ENTRY — 997 AUTHORITY
# ======================================================

def validate(x12_segments, p_x12_segments):
    tx1 = detect_transaction(x12_segments)
    tx2 = detect_transaction(p_x12_segments)

    # Transaction mismatch → immediate reject
    if tx1 != tx2:
        return {
            "transaction": None,
            "ack_status": "REJECTED",
            "fatal_errors": [{
                "segment": "ST",
                "difference": "TRANSACTION_MISMATCH",
                "severity": "FATAL"
            }],
            "all_errors": []
        }

    rules = load_rules(tx1)
    if not rules:
        return {
            "transaction": tx1,
            "ack_status": "REJECTED",
            "fatal_errors": [{
                "segment": "ST",
                "difference": "RULES_NOT_FOUND",
                "severity": "FATAL"
            }],
            "all_errors": []
        }

    # Phase 1: rule validation (997 decision)
    rule_errors = []
    rule_errors.extend(validate_segments(x12_segments, rules))
    rule_errors.extend(validate_segments(p_x12_segments, rules))

    fatal_errors = [e for e in rule_errors if e["severity"] == "FATAL"]

    # 🛑 STOP-ON-FATAL → 997 REJECT
    if fatal_errors:
        return {
            "transaction": tx1,
            "ack_status": "REJECTED",
            "fatal_errors": fatal_errors,
            "all_errors": rule_errors
        }

    # Phase 2: analytical comparison (does NOT affect 997)
    comparison_errors = compare_elements(x12_segments, p_x12_segments)

    return {
        "transaction": tx1,
        "ack_status": "ACCEPTED",
        "fatal_errors": [],
        "all_errors": rule_errors + comparison_errors
    }
