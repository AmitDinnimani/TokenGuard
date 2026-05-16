import unittest
from core.budget import BudgetManager
from observer.operations import CostCalculator

class TestCore(unittest.TestCase):
    def test_budget_manager_within_limit(self):
        bm = BudgetManager(default_limit=0.05)
        self.assertTrue(bm.is_within_budget(0.01))
        self.assertTrue(bm.is_within_budget(0.05))
        self.assertFalse(bm.is_within_budget(0.06))

    def test_budget_manager_dynamic_limit(self):
        bm = BudgetManager(default_limit=0.05)
        self.assertTrue(bm.is_within_budget(0.1, dynamic_limit=0.2))
        self.assertFalse(bm.is_within_budget(0.1, dynamic_limit=0.05))

    def test_cost_calculator(self):
        # 2 / 1,000,000 = 0.000002
        self.assertEqual(CostCalculator.calculate_input_cost(1000), 0.002)
        self.assertEqual(CostCalculator.calculate_output_cost(1000), 0.004)

    def test_compression_ratio(self):
        self.assertEqual(CostCalculator.calculate_compression_ratio(100, 50), 0.5)
        self.assertEqual(CostCalculator.calculate_compression_ratio(0, 50), 0.0)

if __name__ == '__main__':
    unittest.main()
