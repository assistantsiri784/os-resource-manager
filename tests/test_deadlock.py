import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.deadlock import bankers_safety, detect_deadlock
class DeadlockTests(unittest.TestCase):
    def test_safe_state(self):
        r = bankers_safety([[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],
            [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]], [3,3,2])
        self.assertTrue(r["safe"])
        self.assertTrue(r["sequence"])
    def test_invalid_maximum(self):
        with self.assertRaises(ValueError):
            bankers_safety([[2]], [[1]], [0])
    def test_detect_deadlock(self):
        r = detect_deadlock([[1],[1]], [[1],[1]], [0])
        self.assertTrue(r["deadlock_detected"])
if __name__ == "__main__": unittest.main()
