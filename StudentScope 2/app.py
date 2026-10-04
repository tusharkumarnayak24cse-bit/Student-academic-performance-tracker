from pathlib import Path
import io
from html import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from analysis import COLUMNS, clean_data, subject_summary, forecast, safe_csv

st.set_page_config(page_title='StudentScope | Academic Analytics', page_icon='🎓', layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
.stApp{background:#f4f6fb;color:#18233e;font-family:'DM Sans',sans-serif}
h1,h2,h3{letter-spacing:-.035em} .block-container{padding:2rem 2.5rem 4rem;max-width:1440px}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e5e9f3}
[data-testid="stSidebar"] h1{font-size:1.5rem}
[data-testid="stMetric"]{background:#fff;border:1px solid #e3e8f2;border-radius:18px;padding:20px}
[data-testid="stMetricValue"]{font-size:clamp(1.3rem,2.4vw,2rem);overflow-wrap:anywhere}
.hero{position:relative;overflow:hidden;background:linear-gradient(115deg,#172c59,#354cc4);padding:32px 36px;border-radius:24px;color:white;margin-bottom:24px;box-shadow:0 12px 35px #243d8220}
.hero:after{content:'';position:absolute;right:-60px;top:-100px;width:290px;height:290px;border:45px solid #ffffff09;border-radius:50%;pointer-events:none}
.hero h1{color:white!important;margin:8px 0;font-size:clamp(2rem,4vw,3rem)}
.hero p{color:#dce5ff;margin:0}.eyebrow{font-size:11px;letter-spacing:.18em;font-weight:700}.badge{display:inline-block;margin-top:20px;padding:6px 12px;border:1px solid #ffffff30;border-radius:30px;font-size:12px;color:#e5ecff}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:12px 0 16px}
.kpi{min-width:0;background:#fff;border:1px solid #e4e9f3;border-radius:20px;padding:22px;box-shadow:0 5px 18px #24365305;animation:rise .45s ease both;transition:transform .2s,box-shadow .2s}
.kpi:hover{transform:translateY(-3px);box-shadow:0 12px 25px #24365312}.kpi:nth-child(2){animation-delay:.06s}.kpi:nth-child(3){animation-delay:.12s}.kpi:nth-child(4){animation-delay:.18s}
.kpi-label{font-size:12px;font-weight:600;color:#68758d}.kpi-value{font-size:clamp(1.5rem,2.7vw,2.3rem);font-weight:700;letter-spacing:-.04em;margin:10px 0 3px;line-height:1.2;overflow-wrap:anywhere}.kpi-note{font-size:12px;color:#778398}.kpi-accent .kpi-value{color:#4255ce}
.subject-card{background:#fff;padding:18px 20px;border:1px solid #e5e9f3;border-radius:16px;margin:10px 0}.subject-row{display:flex;justify-content:space-between;gap:12px;font-weight:600}.track{height:8px;border-radius:8px;background:#edf0f7;margin:12px 0}.fill{height:100%;border-radius:8px;background:linear-gradient(90deg,#5365d9,#8593f3)}.subject-note{font-size:12px;color:#738097}
.stButton button,.stDownloadButton button{border-radius:10px;transition:transform .15s}.stButton button:hover,.stDownloadButton button:hover{transform:translateY(-1px)}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:600px){.block-container{padding:1rem 1rem 3rem}.hero{padding:24px}.kpi{padding:16px}.kpi-value{font-size:1.7rem}.hero h1{font-size:2rem}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>""", unsafe_allow_html=True)
# Play only on a new browser session, never on normal widget reruns.
if not st.session_state.get('intro_shown', False):
    st.session_state.intro_shown = True
    st.markdown("""
<style>
#intro-skip{position:fixed;opacity:0;pointer-events:none}
.ss-intro{position:fixed;inset:0;z-index:999999;background:radial-gradient(ellipse at 20% 15%,#3442a0 0,transparent 55%),linear-gradient(135deg,#0b142c,#192550);color:#fff;display:flex;align-items:center;justify-content:center;padding:24px;overflow:auto;animation:intro-dismiss .65s ease 4.3s forwards}
.ss-intro-inner{text-align:center;width:min(900px,100%);margin:auto}
.ss-intro-kicker{color:#a9baff;letter-spacing:.24em;font-size:11px;font-weight:700;animation:intro-rise .65s both}
.ss-intro-title{font-size:clamp(36px,7vw,76px);font-weight:700;letter-spacing:-.055em;line-height:1.1;margin:18px 0;color:white;animation:intro-rise .7s .15s both}
.ss-intro-sub{color:#c8d2f4;margin-bottom:28px;animation:intro-rise .7s .3s both}
.ss-members{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.ss-member{border:1px solid #ffffff25;background:#ffffff09;border-radius:18px;padding:22px 12px;animation:intro-rise .65s .5s both}
.ss-member:nth-child(2){animation-delay:.8s}.ss-member:nth-child(3){animation-delay:1.1s}
.ss-initial{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#8796ff25;color:#cbd4ff;margin:0 auto 14px;font-size:18px;font-weight:700}
.ss-name{font-weight:600;font-size:18px}.ss-id{font-size:12px;letter-spacing:.04em;color:#b7c6f5;margin-top:6px}
.ss-intro-progress{height:3px;background:#ffffff15;width:160px;margin:30px auto 12px;border-radius:4px;overflow:hidden}
.ss-intro-progress:after{content:'';display:block;width:100%;height:100%;background:#a9baff;transform-origin:left;animation:intro-progress 4.3s linear both}
.ss-intro-hint{font-size:12px;color:#b7c6f5}.ss-skip{display:inline-block;margin-top:16px;border:1px solid #ffffff40;border-radius:24px;padding:8px 20px;color:white;cursor:pointer;font-size:13px}
#intro-skip:checked + .ss-intro{display:none}#intro-skip:focus-visible + .ss-intro .ss-skip{outline:3px solid #b7c6ff;outline-offset:4px}
@keyframes intro-rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes intro-progress{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes intro-dismiss{to{opacity:0;visibility:hidden;pointer-events:none}}
@media(max-width:600px){.ss-members{grid-template-columns:1fr;gap:8px}.ss-member{padding:12px;display:grid;grid-template-columns:42px 1fr;text-align:left;column-gap:12px}.ss-initial{width:38px;height:38px;grid-row:span 2;margin:0}.ss-name{font-size:16px}.ss-id{margin-top:3px}.ss-intro-sub{margin-bottom:18px}.ss-intro-progress{margin-top:20px}}
@media(prefers-reduced-motion:reduce){.ss-intro,#intro-skip{display:none!important}}
</style>
<input type="checkbox" id="intro-skip" aria-label="Skip welcome animation">
<div class="ss-intro"><div class="ss-intro-inner">
<div class="ss-intro-kicker">PSC PROJECT • PRESENTED BY</div>
<div class="ss-intro-title">StudentScope</div>
<div class="ss-intro-sub">Your marks. Your progress. Our project.</div>
<div class="ss-members">
<div class="ss-member"><div class="ss-initial">TN</div><div class="ss-name">Tushar Nayak</div><div class="ss-id">IU2441230774</div></div>
<div class="ss-member"><div class="ss-initial">BP</div><div class="ss-name">Bhargav Padmani</div><div class="ss-id">IU2441230775</div></div>
<div class="ss-member"><div class="ss-initial">AG</div><div class="ss-name">Arkey Gatrad</div><div class="ss-id">IU2441230776</div></div>
</div><div class="ss-intro-progress"></div><div class="ss-intro-hint">Your dashboard opens automatically</div>
<label class="ss-skip" for="intro-skip">Skip intro →</label>
</div></div>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">STUDENT WORKSPACE / ACADEMIC ANALYTICS</div><h1>Make every result count.</h1><p>Understand your progress. Focus your effort. Reach your next milestone.</p><span class="badge">StudentScope • Performance dashboard</span></div>', unsafe_allow_html=True)
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
    st.markdown("""<div class="subject-card"><div class="eyebrow">PROJECT TEAM</div>
    <div style="display:flex;flex-wrap:wrap;gap:18px 40px;margin-top:14px">
    <div><strong>Tushar Nayak</strong><div class="subject-note">IU2441230774</div></div>
    <div><strong>Bhargav Padmani</strong><div class="subject-note">IU2441230775</div></div>
    <div><strong>Arkey Gatrad</strong><div class="subject-note">IU2441230776</div></div>
    </div></div>""", unsafe_allow_html=True)
    st.header('A clearer view of your progress')
    total = filtered.marks.sum()
    maximum = filtered.max_marks.sum()
    percentage = 100 * total / maximum
    attention = int((summary.percentage < threshold).sum())
    cards = [
        ('Recorded marks', f'{total:,.1f}', f'out of {maximum:,.0f} available marks'),
        ('Weighted percentage', f'{percentage:.1f}%', 'Across your selected assessments'),
        ('Strongest subject', str(summary.iloc[0].subject), f'{summary.iloc[0].percentage:.1f}% weighted score'),
        ('Needs attention', str(attention), f'Subjects below your {threshold}% target'),
    ]
    st.markdown('<div class="kpi-grid">' + ''.join(
        f'<div class="kpi kpi-accent"><div class="kpi-label">{escape(label)}</div>'
        f'<div class="kpi-value">{escape(value)}</div><div class="kpi-note">{escape(note)}</div></div>'
        for label, value, note in cards) + '</div>', unsafe_allow_html=True)
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
    st.subheader('Your subject snapshot')
    for row in summary.itertuples():
        note = 'On track' if row.percentage >= threshold else f'{threshold-row.percentage:.1f} points to your target'
        st.markdown(f'<div class="subject-card"><div class="subject-row"><span>{escape(str(row.subject))}</span><span>{row.percentage:.1f}%</span></div><div class="track"><div class="fill" style="width:{min(100,max(0,row.percentage)):.1f}%"></div></div><div class="subject-note">{escape(note)}</div></div>', unsafe_allow_html=True)
    with st.expander('Detailed subject totals'):
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
