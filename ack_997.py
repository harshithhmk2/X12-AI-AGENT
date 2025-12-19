from datetime import datetime

def generate_997(validation_result, functional_id):
    """
    Generate X12 997 Functional Acknowledgment
    """

    ack_status = validation_result["ack_status"]
    rejected = ack_status == "REJECTED"

    ak5 = "R" if rejected else "A"
    ak9 = "R" if rejected else "A"
    accepted = 0 if rejected else 1

    now = datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M")

    segments = [
        "ST*997*0001~",
        f"AK1*{functional_id}*1~",
        f"AK2*{functional_id}*0001~",
        f"AK5*{ak5}~",
        f"AK9*{ak9}*1*1*{accepted}~",
        "SE*6*0001~"
    ]

    return "\n".join(segments)
