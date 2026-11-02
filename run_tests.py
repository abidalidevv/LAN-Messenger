import unittest
import sys
import os

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("=" * 65)
    print("[LAN Messenger] RUNNING AUTOMATED UNIT & STRESS BENCHMARK TESTS")
    print("=" * 65)

    loader = unittest.TestLoader()
    suite = loader.discover("tests")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 65)
        print("[SUCCESS] ALL TESTS & BENCHMARKS PASSED PERFECTLY (100% INTEGRITY)")
        print("=" * 65)
        sys.exit(0)
    else:
        print("\n" + "=" * 65)
        print("[FAILED] SOME TESTS FAILED")
        print("=" * 65)
        sys.exit(1)

