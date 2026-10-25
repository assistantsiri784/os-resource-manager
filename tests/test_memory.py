import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.memory import allocate_memory
class MemoryTests(unittest.TestCase):
    def test_first_fit(self):
        r = allocate_memory([{"pid":"P1","memory":90}], [100,200], "first_fit")
        self.assertEqual(r["allocations"][0]["block_index"], 0)
        self.assertEqual(r["remaining_blocks"], [10,200])
    def test_unallocated(self):
        r = allocate_memory([{"pid":"P1","memory":500}], [100], "best_fit")
        self.assertEqual(r["unallocated"], ["P1"])
    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            allocate_memory([{"pid":"P1","memory":5}], [10], "unknown")
if __name__ == "__main__": unittest.main()
