from fastapi import FastAPI, UploadFile, File
from parser import parse_x12
from validator import validate
from ai.groq_agent import analyze
from report_generator import generate_text_report
from ack_997 import generate_997
import os

app = FastAPI(title="X12 AI Validation & Comparison Agent")

# Directory to store reports
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@app.post("/validate")
async def validate_x12(
    x12: UploadFile = File(...),
    p_x12: UploadFile = File(...)
):
    # Read uploaded files
    x12_content = (await x12.read()).decode("utf-8")
    p_x12_content = (await p_x12.read()).decode("utf-8")

    # Parse X12 files
    x12_segments = parse_x12(x12_content)
    p_x12_segments = parse_x12(p_x12_content)

    # Perform validation
    validation_result = validate(x12_segments, p_x12_segments)

    transaction = validation_result["transaction"]
    ack_status = validation_result["ack_status"]
    all_errors = validation_result["all_errors"]
    fatal_errors = validation_result["fatal_errors"]

    # 🔹 Generate 997 ACK
    ack_997 = generate_997(
        validation_result=validation_result,
        functional_id=transaction
    )
    # Generate ACK filename
    ack_filename = f"ack_997_{transaction}_{ack_status}.x12"
    ack_file_path = os.path.join(REPORT_DIR, ack_filename)

    # Write ACK to file
    with open(ack_file_path, "w", encoding="utf-8") as f:
        f.write(ack_997)

    # 💡 Skip AI if no errors
    if not all_errors:
        ai_analysis = (
            "✅ Validation successful.\n\n"
            "No structural, element-level, or rule-based differences were detected. "
            "The X12 file is compliant and accepted for downstream processing."
        )
    else:
        ai_analysis = analyze(validation_result)

    # Generate text report
    report_text = generate_text_report(
        prod_file_name=x12.filename,
        test_file_name=p_x12.filename,
        transaction=transaction,
        diffs=all_errors
    )

    report_file_path = os.path.join(REPORT_DIR, "x12_compare_result.txt")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    if ack_status == "REJECTED":
        status = "REJECTED"
    elif all_errors:
        status = "ACCEPTED_WITH_ERRORS"
    else:
        status = "ACCEPTED_CLEAN"

    return {
        "transaction": transaction,
        "status": status,
        "ack_status": ack_status,
        "fatal_error_count": len(fatal_errors),
        "error_count": len(all_errors),
        "validation_errors": all_errors,
        #"ack_997": ack_997,
        "ack_997_report_path": ack_file_path,
        "analysis": ai_analysis,
        "text_report_path": report_file_path
    }
