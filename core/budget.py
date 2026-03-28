class BudgetManager:
    def __init__(self, default_limit: float = 0.001):
        self.default_limit = default_limit

    def is_within_budget(self, cost: float, dynamic_limit: float = None) -> bool:
        limit_to_check = dynamic_limit if dynamic_limit is not None else self.default_limit
        return cost <= limit_to_check
