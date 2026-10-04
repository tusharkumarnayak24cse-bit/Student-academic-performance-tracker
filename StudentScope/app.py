from pathlib import Path
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from analysis import COLUMNS, clean_data, subject_summary, forecast, safe_csv

st.set_page_config(page_title='StudentScope | Academic Analytics', page_icon='🎓', layout='wide')
st.markdown('''<style>
.stApp {background:#f5f7fc;color:#17223b} h1,h2,h3 {letter-spacing:-.035em}
[data-testid="stMetric"] {background:white;border:1px solid #e0e5f0;border-radius:16px;padding:18px}
[data-testid="stSidebar"] {background:#edf1fb} .block-container{padding-top:2rem}
.hero{background:linear-gradient(120deg,#182751,#405ac1);padding:30px;border-radius:22px;color:white;margin-bottom:22px}
.hero h1{color:white!important;margin:0}.hero p{color:#d7e1ff;margin-bottom:0}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="hero"><small>PSC • ACADEMIC ANALYTICS</small><h1>StudentScope</h1><p>Your marks. Your progress. Your next milestone.</p></div>', unsafe_allow_html=True)
ROOT = Path(__file__).parent
if 'records' not in st.session_state:
    st.session_state.records = pd.read_csv(ROOT / 'data/sample_marks.csv', dtype={'student_id': str})
    st.session_state.source = 'Fictional demo dataset'

def commit(raw):
    clean, rejected = clean_data(raw)
    st.session_state.records = clean[COLUMNS]
    return rejected

def chart(x, y, title, line=False):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.set_facecolor('white')
    if line:
        ax.plot(x, y, marker='o', color='#5365d9', linewidth=2.5)
    else:
        ax.bar(x, y, color='#5365d9', width=.6)
    ax.set_title(title, loc='left', pad=16, fontweight='bold')
    ax.set_ylabel('Percentage (%)'); ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='x', rotation=25)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

with st.sidebar:
    st.title('🎓 StudentScope')
    page = st.radio('Workspace', ['Overview', 'Trends & prediction', 'Target planner', 'Manage data', 'Project guide'])
    st.caption('DATA SOURCE')
    st.write(st.session_state.source)
    st.caption('Session data is temporary. Download your records before closing or refreshing; upload them next time.')
    st.download_button('Back up all records', safe_csv(st.session_state.records), 'studentscope_records.csv', 'text/csv')

if page == 'Manage data':
    st.header('Make the data yours')
    st.caption('Start with the fictional demo or upload your own marks. Exam order is chronological within each subject and semester.')
    upload_tab, entry_tab, edit_tab = st.tabs(['Upload CSV', 'Add a result', 'Edit / delete'])
    with upload_tab:
        st.download_button('Download blank CSV template', safe_csv(pd.DataFrame(columns=COLUMNS)), 'marks_template.csv')
        uploaded = st.file_uploader('Choose marks CSV', type=['csv'])
        if uploaded:
            try:
                raw = pd.read_csv(uploaded, dtype={'student_id': str})
                clean, bad = clean_data(raw)
                st.write(f'{len(clean)} valid rows · {len(bad)} rejected rows')
                st.dataframe(clean, use_container_width=True)
                if not bad.empty:
                    st.warning('Invalid rows and older duplicates are excluded. Review the reasons below.')
                    st.dataframe(bad, use_container_width=True)
                    st.download_button('Download rejected rows', safe_csv(bad), 'rejected_rows.csv')
                mode = st.radio('Import method', ['Replace current dataset', 'Merge (uploaded matching rows win)'])
                if st.button('Import valid rows', disabled=clean.empty):
                    combined = clean[COLUMNS] if mode.startswith('Replace') else pd.concat([st.session_state.records, clean[COLUMNS]], ignore_index=True)
                    commit(combined); st.session_state.source = 'Your imported dataset'; st.success('Imported. Open Overview to explore.')
            except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
                st.error(f'Cannot import: {exc}')
    with entry_tab:
        with st.form('entry', clear_on_submit=False):
            a, b = st.columns(2)
            sid = a.text_input('Enrollment / student ID')
            name = b.text_input('Student name')
            sem = a.number_input('Semester', 1, 20, 5)
            subject = b.text_input('Subject', placeholder='PSC')
            exam = a.text_input('Exam label', placeholder='Mid-sem 1')
            order = b.number_input('Exam order', 1, 100, 1)
            marks = a.number_input('Marks obtained', 0.0, 10000.0, 15.0)
            maximum = b.number_input('Maximum marks', 1.0, 10000.0, 20.0)
            st.caption('An existing result with the same student, semester, subject and exam order will be replaced.')
            if st.form_submit_button('Save result'):
                row = pd.DataFrame([[sid, name, sem, subject, exam, order, marks, maximum]], columns=COLUMNS)
                valid, bad = clean_data(row)
                if not bad.empty:
                    st.error(bad.reason.iloc[0])
                else:
                    commit(pd.concat([st.session_state.records, row], ignore_index=True))
                    st.session_state.source = 'Edited dataset'; st.success('Result saved.')
    with edit_tab:
        edited = st.data_editor(st.session_state.records, num_rows='dynamic', use_container_width=True, key='editor')
        if st.button('Apply table changes'):
            valid, bad = clean_data(edited)
            if not bad.empty:
                st.error('Fix invalid or duplicate rows before applying changes.'); st.dataframe(bad)
            else:
                commit(edited); st.session_state.source = 'Edited dataset'; st.success('Changes saved.'); st.rerun()
        confirm = st.checkbox('I understand that reset replaces all current records')
        a, b = st.columns(2)
        if a.button('Reset demo', disabled=not confirm):
            st.session_state.records = pd.read_csv(ROOT / 'data/sample_marks.csv', dtype={'student_id': str})
            st.session_state.source = 'Fictional demo dataset'; st.rerun()
        if b.button('Start empty', disabled=not confirm):
            st.session_state.records = pd.DataFrame(columns=COLUMNS)
            st.session_state.source = 'Empty dataset'; st.rerun()
    st.stop()

if page == 'Project guide':
    st.header('Student Academic Performance Analyzer Using Python')
    st.markdown((ROOT / 'PROJECT_GUIDE.md').read_text())
    st.stop()

df, _ = clean_data(st.session_state.records)
if df.empty:
    st.info('No results yet. Open Manage data to add results or load the demo.'); st.stop()
with st.sidebar:
    students = sorted(df.student_id.unique())
    sid = st.selectbox('Student', students, format_func=lambda x: f'{df.loc[df.student_id.eq(x), "student_name"].iloc[-1]} · {x}')
    student = df[df.student_id.eq(sid)]
    semesters = sorted(student.semester.unique())
    selected = st.multiselect('Semesters', semesters, default=semesters)
    subjects = sorted(student[student.semester.isin(selected)].subject.unique())
    chosen = st.multiselect('Subjects', subjects, default=subjects)
    threshold = st.slider('Needs-attention threshold (%)', 0, 100, 60)
filtered = student[student.semester.isin(selected) & student.subject.isin(chosen)]
if filtered.empty:
    st.info('Select at least one semester and subject containing marks.'); st.stop()
summary = subject_summary(filtered)
st.caption(f'{student.student_name.iloc[-1]} · {sid} · {len(filtered)} recorded results')

if page == 'Overview':
    st.header('A clearer view of your progress')
    a, b, c, d = st.columns(4)
    a.metric('Recorded marks', f'{filtered.marks.sum():g} / {filtered.max_marks.sum():g}')
    b.metric('Weighted percentage', f'{100 * filtered.marks.sum() / filtered.max_marks.sum():.1f}%')
    c.metric('Strongest subject', summary.iloc[0].subject)
    d.metric('Needs attention', int((summary.percentage < threshold).sum()))
    st.caption('Weighted percentage = total obtained ÷ total maximum × 100. These recorded-assessment totals are not an official university result or SGPA.')
    left, right = st.columns([1.3, 1])
    with left: chart(summary.subject, summary.percentage, 'Subject comparison')
    with right:
        st.subheader('Focus list')
        weak = summary[summary.percentage < threshold]
        if weak.empty: st.success('All selected subjects meet your threshold.')
        else:
            for r in weak.itertuples(): st.warning(f'{r.subject}: {r.percentage:.1f}% — {threshold-r.percentage:.1f} percentage points below your target.')
        st.caption('The threshold is your chosen study target, not an official pass rule.')
    sems = filtered.groupby('semester', as_index=False)[['marks', 'max_marks']].sum()
    chart(sems.semester.astype(str), sems.marks / sems.max_marks * 100, 'Semester-wise performance', True)
    st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
    st.download_button('Download subject analysis', safe_csv(summary.round(2)), 'subject_analysis.csv')
    with st.expander('View and download selected records'):
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button('Download selected results', safe_csv(filtered), 'selected_results.csv')

elif page == 'Trends & prediction':
    st.header('Track change. Estimate what comes next.')
    a, b = st.columns(2)
    sem = a.selectbox('Semester for trend', sorted(filtered.semester.unique()))
    sub = b.selectbox('Subject for trend', sorted(filtered[filtered.semester.eq(sem)].subject.unique()))
    history = filtered[(filtered.semester.eq(sem)) & (filtered.subject.eq(sub))].sort_values('exam_order')
    chart(history.exam_order.astype(str), history.percentage, f'{sub} · assessment trend', True)
    st.dataframe(history[['exam_order', 'exam', 'marks', 'max_marks', 'percentage']].round(2), hide_index=True, use_container_width=True)
    result = forecast(history)
    if result is None:
        st.info('Add at least three distinct exam orders for this subject and semester to estimate the next result.')
    else:
        data, fitted, next_order, predicted = result
        st.metric(f'Estimated percentage · assessment {next_order}', f'{predicted:.1f}%')
        st.caption('NumPy fits y = mx + c to exam order and percentage. The next estimate is clipped to 0–100%. This is an educational trend estimate, not a guaranteed result; exam difficulty and preparation can change outcomes.')
        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.plot(data.exam_order, data.percentage, 'o-', label='Recorded', color='#5365d9')
        ax.plot(data.exam_order, fitted, '--', label='Linear fit', color='#929bb5')
        ax.scatter([next_order], [predicted], marker='*', s=200, color='#10a88c', label='Next estimate')
        ax.set(xlabel='Exam order', ylabel='Percentage (%)', ylim=(0,105)); ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        st.download_button('Download estimate', safe_csv(pd.DataFrame([{'student_id':sid,'semester':sem,'subject':sub,'next_exam_order':next_order,'estimated_percentage':round(predicted,2)}])), 'prediction.csv')
    st.subheader('Optional grade mapping')
    st.caption('No university grading scheme is assumed. Enter approved percentage boundaries if you want to map recorded percentages and the estimate to grades.')
    mapping = st.text_area('One grade per line: label,minimum percentage', placeholder='Enter your institution’s official boundaries here')
    if mapping.strip():
        try:
            rules = [(parts[0].strip(), float(parts[1])) for line in mapping.splitlines() if line.strip() for parts in [line.split(',')]]
            if any(not label or not 0 <= cutoff <= 100 for label, cutoff in rules) or len({x[1] for x in rules}) != len(rules) or min(x[1] for x in rules) != 0:
                raise ValueError('Use unique cutoffs from 0 to 100, including a lowest cutoff of 0.')
            rules.sort(key=lambda x:x[1], reverse=True)
            grade = lambda score: next(label for label, cutoff in rules if score >= cutoff)
            graded = history[['exam', 'percentage']].copy(); graded['grade'] = graded.percentage.map(grade)
            st.dataframe(graded, hide_index=True)
            if result: st.info(f'Estimated next grade under your supplied rules: {grade(predicted)}')
        except (ValueError, IndexError): st.error('Use one label,number per line with unique cutoffs between 0 and 100, including 0.')

elif page == 'Target planner':
    st.header('Plan your next assessment')
    sem = st.selectbox('Semester to plan', sorted(filtered.semester.unique()))
    sub = st.selectbox('Subject to plan', sorted(filtered[filtered.semester.eq(sem)].subject.unique()))
    current = filtered[(filtered.semester.eq(sem)) & (filtered.subject.eq(sub))]
    a, b = st.columns(2)
    target = a.number_input('Desired combined percentage', 0.0, 100.0, 75.0)
    next_max = b.number_input('Next assessment maximum marks', 1.0, 10000.0, 40.0)
    required = target / 100 * (current.max_marks.sum() + next_max) - current.marks.sum()
    if required > next_max:
        best = 100 * (current.marks.sum() + next_max) / (current.max_marks.sum() + next_max)
        st.warning(f'This target is not reachable in one assessment. Even {next_max:g}/{next_max:g} gives {best:.1f}% combined.')
    elif required <= 0: st.success('Your recorded marks already secure this combined target, even with zero in the next assessment.')
    else: st.metric('Minimum marks needed', f'{required:.2f} / {next_max:g}')
    st.caption('Assumes the selected recorded assessments and the next assessment are added directly, without university-specific weighting. If only whole marks are awarded, round the required marks up.')
