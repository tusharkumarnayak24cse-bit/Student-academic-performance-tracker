### Aim
Build a Python dashboard that helps students understand subject performance, compare semesters and estimate future assessment performance from historical marks.

### Features and screenshot coverage
- Semester-wise marks and grades: records include semester; optional user-supplied grade boundaries map percentages to grades.
- Subject trends: chronological assessment charts for each subject within a semester.
- Subject comparisons: weighted percentages account for different assessment maximum marks.
- Predicted grade trajectory: NumPy linear fitting estimates the next percentage; optional grading rules map it to a grade.
- Personal dataset: manual entry, editable table, CSV imports, fictional demo and CSV backup.
- Analysis: Pandas cleaning, grouping, aggregation and filters; Matplotlib charts.

### Three-member division
| Member | Module | Viva responsibility |
|---|---|---|
| Member 1 — enter name / enrollment | Data entry, CSV import, validation | File handling, exceptions, DataFrames |
| Member 2 — enter name / enrollment | Analysis, targets and prediction | NumPy, grouping, formulas, regression |
| Member 3 — enter name / enrollment | Streamlit dashboard, charts and exports | UI state, Matplotlib, integration testing |

Every member should understand the complete flow. Replace these placeholders with your team details before submission.

### Data flow
CSV/manual entry → validation → session records → student/semester/subject filters → aggregation or prediction → charts and CSV report.

### Algorithms and formulas
1. Convert numeric columns; reject missing, non-finite and impossible values.
2. Require positive integer semester and exam order. Keep the last duplicate result for a matching student, semester, subject and exam order.
3. Percentage = marks / maximum × 100.
4. Combined percentage = sum(marks) / sum(maximum) × 100. This is not the simple average of percentages when maximum marks differ.
5. Fit y = mx + c with `numpy.polyfit` using at least three exam orders for one student/subject/semester. Predict at the next order and bound the estimate to 0–100.
6. Required next marks = target_percentage / 100 × (current maximum + next maximum) − current marks.

### Design choices and limitations
The app is a session-based academic prototype. Download CSV backups before refreshing or closing; no database or user accounts are included. A fresh session loads fictional demo records. No actual classmates' records are bundled. No official Indus grading or SGPA rules are assumed. You can supply approved percentage grade boundaries, but this is not credit-weighted SGPA calculation. Assessment marks are added directly; official assessment weights and separate passing rules are not modeled. Different exam difficulties can make a linear forecast unreliable. Cross-semester totals may compare different courses. Data from the same subject name is combined in Overview when multiple semesters are selected; the prediction screen isolates a semester.

### Demo sequence
1. Open Overview and choose Demo Student A.
2. Compare semester 4 and 5, then filter to semester 5.
3. Inspect weak subjects and export a subject report.
4. Open Trends & prediction; choose PSC and show the linear fit.
5. Try a 75% goal in Target planner.
6. Add a result or upload the sample CSV; demonstrate validation with an invalid mark.
7. Download a backup and re-import it.

### Viva questions
**Why Pandas?** It supports tabular data cleaning, filtering, grouping and CSV handling.

**Why NumPy?** It supplies numerical arrays and least-squares polynomial fitting.

**What does polyfit(x, y, 1) do?** It returns the slope and intercept of a best-fit straight line.

**Why normalize marks?** Comparing 18/20 to 30/40 using raw marks is misleading; their percentages are 90% and 75%.

**Why three assessments?** Two points always define a line; three is a minimal project guard, though more comparable assessments are preferable.

**What is session state?** Streamlit's per-session storage keeps records available across interactions that rerun the script.

**How are duplicates handled?** A composite key identifies the result; the last matching row wins during import or entry.

**Can a prediction be guaranteed?** No. It extrapolates observed trends and does not model preparation, exam difficulty or changing conditions.

**What can be improved?** SQLite persistence, authenticated accounts, official institution-specific grading and weighted assessments, and evaluation of predictions on held-out exams.


## Project team

| Student | Enrollment number |
| --- | --- |
| Tushar Nayak | IU2441230774 |
| Bhargav Padmani | IU2441230775 |
| Arkey Gatrad | IU2441230776 |
