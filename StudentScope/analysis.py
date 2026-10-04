"""Pure data functions for the StudentScope PSC project."""
import numpy as np
import pandas as pd

COLUMNS = ['student_id', 'student_name', 'semester', 'subject', 'exam', 'exam_order', 'marks', 'max_marks']
KEY = ['student_id', 'semester', 'subject', 'exam_order']

def clean_data(raw):
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(sorted(missing)))
    df = raw[COLUMNS].copy()
    reasons = pd.Series('', index=df.index)
    for col in ['student_id', 'student_name', 'subject', 'exam']:
        df[col] = df[col].fillna('').astype(str).str.strip()
        reasons.loc[df[col].eq('')] += f'{col} is empty; '
    for col in ['semester', 'exam_order', 'marks', 'max_marks']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        reasons.loc[~np.isfinite(df[col])] += f'{col} must be finite numeric; '
    for col in ['semester', 'exam_order']:
        reasons.loc[(df[col] < 1) | (df[col] % 1 != 0)] += f'{col} must be a positive integer; '
    reasons.loc[(df.marks < 0) | (df.max_marks <= 0) | (df.marks > df.max_marks)] += 'Invalid marks range; '
    rejected = raw.loc[reasons.ne('')].copy()
    rejected['reason'] = reasons[reasons.ne('')]
    good = df.loc[reasons.eq('')].copy()
    duplicates = good.duplicated(KEY, keep='last')
    if duplicates.any():
        dup = good.loc[duplicates].copy()
        dup['reason'] = 'Duplicate student/semester/subject/exam order; last row retained'
        rejected = pd.concat([rejected, dup], ignore_index=True)
    good = good.loc[~duplicates].copy()
    good[['semester', 'exam_order']] = good[['semester', 'exam_order']].astype(int)
    good['percentage'] = good.marks / good.max_marks * 100
    return good.reset_index(drop=True), rejected.reset_index(drop=True)

def subject_summary(df):
    result = df.groupby('subject', as_index=False).agg(marks=('marks', 'sum'), max_marks=('max_marks', 'sum'), exams=('exam', 'size'))
    result['percentage'] = result.marks / result.max_marks * 100
    return result.sort_values('percentage', ascending=False)

def forecast(df):
    data = df.groupby('exam_order', as_index=False).percentage.mean().sort_values('exam_order')
    if len(data) < 3:
        return None
    x, y = data.exam_order.to_numpy(), data.percentage.to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    next_order = int(x.max()) + 1
    return data, slope * x + intercept, next_order, float(np.clip(slope * next_order + intercept, 0, 100))

def safe_csv(df):
    out = df.copy()
    for col in out.select_dtypes(include=['object', 'string']).columns:
        out[col] = out[col].map(lambda v: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v)
    return out.to_csv(index=False).encode('utf-8-sig')
