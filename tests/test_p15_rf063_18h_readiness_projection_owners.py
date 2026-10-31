import unittest
from scripts.diagnostics import run_m26_scorecard as m
class T(unittest.TestCase):
 def test_b7_max_drawdown_ratio(self):self.assertEqual(m._max_drawdown_ratio([]),(0.0,0.0));self.assertEqual(m._max_drawdown_ratio([100.,80.]),(20.,.2))
 def test_b8_risk_adjusted(self):self.assertEqual(m._risk_adjusted([])['sample_count'],0.);self.assertEqual(m._risk_adjusted([1.,-1.])['pnl_mean'],0.)
if __name__=='__main__':unittest.main()
