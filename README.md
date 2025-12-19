
# X12 AI Validation & 997 Acknowledgment Agent

An **enterprise-grade EDI X12 validation, comparison, and acknowledgment system** built with **FastAPI**.  
It validates X12 transactions (850, 856, 810, etc.), compares PROD vs TEST files, generates **ANSI X12 997 Functional Acknowledgments**, and produces **human-readable analytical reports**.

This project mirrors real-world EDI engines (IBM Sterling / OpenText / Cleo) in architecture and behavior.

---

## 🚀 Features

- ✅ Supports common X12 transaction sets (850, 856, 810, 855, 940, 997)
- ✅ Rule-based validation (mandatory segments, max-use rules)
- ✅ Stop-on-FATAL (ANSI X12 compliant)
- ✅ Anchor-based segment realignment (prevents cascading errors)
- ✅ Selective ISA / GS element ignore (best practice)
- ✅ Generates **997 Functional Acknowledgment**
- ✅ Saves ACK as downloadable `.x12` file
- ✅ Generates legacy-style text comparison report
- ✅ Optional AI-based root-cause analysis (Groq LLM)
- ✅ Handles large X12 files efficiently (linear-time logic)

---

## 🏗 Architecture Overview

```
Client
  |
  |-- POST /validate
  |
FastAPI
  |
  |-- parser.py        → Parse X12 into segments
  |-- validator.py     → Rule + structural validation (997 authority)
  |-- ack_997.py       → Generate X12 997 ACK
  |-- report_generator → Text comparison report
  |-- groq_agent.py    → AI analysis (optional)
  |
reports/
  ├── x12_compare_result.txt
  └── ack_997_<TX>_<STATUS>.x12
```

---

## 📦 Project Structure

```
x12-ai-agent/
├── main.py
├── parser.py
├── validator.py
├── ack_997.py
├── report_generator.py
├── ai/
│   └── groq_agent.py
├── rules/
│   ├── 850.json
│   ├── 856.json
│   └── 810.json
├── reports/
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate    # Windows
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ (Optional) Set Groq API key
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## ▶️ Run the Application

```bash
uvicorn main:app --reload
```

Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

---

## 🔁 API Usage

### POST `/validate`

**Inputs**
- `x12`   → PROD X12 file
- `p_x12` → TEST / processed X12 file

**Response includes**
- Validation status (`ACCEPTED_CLEAN`, `ACCEPTED_WITH_ERRORS`, `REJECTED`)
- 997 acknowledgment status
- List of validation errors
- Generated 997 ACK (string + file path)
- Text comparison report path
- AI-based analysis (if errors exist)

---

## 🧾 Status Semantics (Important)

| Status | Meaning |
|------|--------|
| ACCEPTED_CLEAN | No errors |
| ACCEPTED_WITH_ERRORS | Business differences, but EDI-valid |
| REJECTED | Fatal structural errors |
| 997 ACK ACCEPTED | Syntax valid |
| 997 ACK REJECTED | Syntax invalid |

> **Note:** 997 reflects *syntactic acceptance*, not business correctness.

---

## 📄 Example 997 ACK

```
ST*997*0001~
AK1*856*1~
AK2*856*0001~
AK5*A~
AK9*A*1*1*1~
SE*6*0001~
```

---

## 🧠 Why This Design Is Correct

- Validation and acknowledgment are decoupled
- Stop-on-fatal prevents noisy diffs
- Anchor-based alignment avoids false mismatches
- ACK generation follows ANSI X12 rules strictly
- Matches real enterprise EDI engines

---

## 📈 Scalability Notes

- Linear-time validation
- Safe for large X12 files (tens of MB)
- Can be upgraded to streaming parsing for GB-scale files

---

## 🔮 Future Enhancements

- AK3 / AK4 segment-level error reporting
- 999 Implementation Acknowledgment
- Batch-level ACK generation
- Trading-partner-specific rule profiles
- Streaming parser for very large files


## 📜 License

MIT License
