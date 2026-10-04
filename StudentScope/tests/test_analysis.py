import unittest
import pandas as pd
from analysis import clean_data, subject_summary, forecast, COLUMNS

class AnalysisTests(unittest.TestCase):
 def rows(self, marks=(10,15,20)):
  return pd.DataFrame([['001','Student',5,'PSC',f'E{i}',i,m,20] for i,m in enumerate(marks,1)],columns=COLUMNS)
 def test_forecast_and_minimum(self):
  d,_=clean_data(self.rows()); self.assertEqual(forecast(d)[3],100)
  self.assertIsNone(forecast(d.head(2)))
 def test_invalid_and_duplicates(self):
  raw=self.rows(); raw.loc[1,'marks']=21; raw=pd.concat([raw,raw.iloc[[0]]],ignore_index=True)
  d,bad=clean_data(raw); self.assertEqual(len(d),2); self.assertEqual(len(bad),2)
 def test_weighted_percentage(self):
  raw=self.rows((10,10)); raw.loc[1,'max_marks']=40
  d,_=clean_data(raw); self.assertAlmostEqual(subject_summary(d).percentage.iloc[0],100/3)
 def test_empty_and_missing(self):
  d,_=clean_data(pd.DataFrame(columns=COLUMNS)); self.assertTrue(d.empty)
  with self.assertRaises(ValueError): clean_data(pd.DataFrame({'x':[1]}))
 def test_nonfinite(self):
  raw=self.rows(); raw['marks']=raw.marks.astype(float); raw.loc[0,'marks']=float('inf'); d,bad=clean_data(raw); self.assertEqual(len(bad),1)
