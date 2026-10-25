import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.disk import fcfs, sstf, scan, cscan
class DiskTests(unittest.TestCase):
    def test_fcfs_movement(self):
        self.assertEqual(fcfs([10,20], 0, 100)["total_movement"], 20)
    def test_sstf(self):
        self.assertEqual(sstf([10,20], 12, 100)["sequence"][0], 10)
    def test_invalid_request(self):
        with self.assertRaises(ValueError): fcfs([100], 0, 100)
    def test_scan_and_cscan(self):
        self.assertTrue(scan([10,20,80], 50, 100)["total_movement"] > 0)
        self.assertTrue(cscan([10,20,80], 50, 100)["total_movement"] > 0)
if __name__ == "__main__": unittest.main()
