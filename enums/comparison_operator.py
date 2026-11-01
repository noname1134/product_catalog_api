from enum import Enum


class ComparisonOperator(str, Enum):
    lt = "lt"
    gt = "gt"
    eq = "eq"