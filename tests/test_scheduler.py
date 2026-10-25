import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.scheduler import fcfs, sjf, srtf, round_robin, priority_preemptive

PS = [{"pid":"P1","arrival":0,"burst":5,"priority":2},
      {"pid":"P2","arrival":1,"burst":3,"priority":1}]
class SchedulerTests(unittest.TestCase):
    def test_fcfs_waiting(self):
        r = fcfs(PS)
        self.assertEqual([m["waiting"] for m in r["metrics"]], [0,4])
    def test_sjf_completes_all(self):
        self.assertEqual(len(sjf(PS)["metrics"]), 2)
    def test_srtf_preempts(self):
        r = srtf(PS)
        self.assertEqual(r["metrics"][1]["completion"], 4)
    def test_round_robin_invalid_quantum(self):
        with self.assertRaises(ValueError): round_robin(PS, 0)
    def test_negative_burst_rejected(self):
        with self.assertRaises(ValueError):
            fcfs([{"pid":"X","arrival":0,"burst":0,"priority":1}])
    def test_priority_result(self):
        self.assertEqual(len(priority_preemptive(PS)["metrics"]), 2)
if __name__ == "__main__": unittest.main()
