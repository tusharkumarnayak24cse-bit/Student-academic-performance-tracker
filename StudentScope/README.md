# StudentScope
Student Academic Performance Analyzer Using Python — PSC group project.

## Run on Windows, macOS or Linux
Install Python 3.10 or newer. Extract this ZIP and open a terminal inside the StudentScope folder.

```bash
python -m venv .venv
```
Activate on Windows:
```bat
.venv\Scripts\activate
```
Activate on macOS/Linux:
```bash
source .venv/bin/activate
```
Install and run:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
On macOS, use `python3` for the first command if `python` is unavailable.
Open http://localhost:8501 in your browser. Keep the terminal open; Ctrl+C stops the app.
This is a Python application: opening app.py or a CSV directly will not launch it.

## Contents
- app.py: Streamlit interface, charts and interaction flow
- analysis.py: reusable validation, aggregation, forecasting and export functions
- data/sample_marks.csv: fictional demonstration data
- data/marks_template.csv: empty import template
- PROJECT_GUIDE.md: aim, algorithms, team division, demonstration and viva notes
- tests/test_analysis.py: calculation and validation tests
- tests/test_app.py: Streamlit screen smoke tests

## CSV structure
`student_id,student_name,semester,subject,exam,exam_order,marks,max_marks`
One row is one assessment result. Use stable subject spelling. Exam order starts at 1 and increases chronologically within each subject and semester. Marks can be fractional; maximum must be positive. Marks must be between 0 and maximum. Import reads IDs as text to preserve leading zeros.
The sample contains 144 fictional results: 3 students × 2 semesters × 6 subjects × 4 assessments.

## Data safety and persistence
Records stay in the current browser session and are not saved to a database. Use **Back up all records** and upload the CSV next time. New sessions start with demo data. There are no accounts, passwords, external data APIs or real student records in this package. If you later host it online, use fictional or consented data for demonstrations.

## Grades
No institution grading scheme is hard-coded. Optional grade boundaries on the prediction page must be supplied from your approved university rules. Enter one `label,minimum percentage` per line, including the lowest threshold of 0. Grade mapping does not calculate SGPA.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Submission
Read PROJECT_GUIDE.md and fill the three member names/enrollment details. Understand and demonstrate the algorithms and customize the project according to your faculty's requirements.
