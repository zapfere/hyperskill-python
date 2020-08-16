from abc import ABC, abstractmethod
from argparse import Namespace
from math import ceil, floor, log

MONTHS_IN_YEAR = 12
HUNDRED_PERCENT = 100


class Calculator(ABC):
    def __init__(self, args: Namespace):
        self._args = args

    @abstractmethod
    def calculate(self):
        raise NotImplementedError


class AnnuityCalculator(Calculator):
    def calculate(self):
        nominal_interest = calculate_nominal_interest(self._args.interest)
        if self._args.payment is None:
            calculate_annuity(
                self._args.principal,
                self._args.periods,
                nominal_interest
            )
        elif self._args.principal is None:
            calculate_principal(
                self._args.payment,
                self._args.periods,
                nominal_interest
            )
        elif self._args.periods is None:
            calculate_duration(
                self._args.principal,
                self._args.payment,
                nominal_interest
            )
        else:
            raise RuntimeError("Unexpected state detected")


class DifferentiatedCalculator(Calculator):
    def calculate(self):
        nominal_interest = calculate_nominal_interest(self._args.interest)
        total_payment = 0.0
        for i in range(1, self._args.periods + 1):
            payment = calculate_diff_payment(
                i,
                self._args.periods,
                self._args.principal,
                nominal_interest
            )
            total_payment += payment
            print(f"Month {i}: paid out {payment}")
        print()
        overpayment = round(total_payment - self._args.principal)
        print("Overpayment =", overpayment)


def calculate_nominal_interest(interest: float) -> float:
    return interest / (MONTHS_IN_YEAR * HUNDRED_PERCENT)


def calculate_duration(principal: float,
                       payment: float,
                       nominal_interest: float):
    n = calculate_periods(principal, payment, nominal_interest)
    periods = ceil(n)
    result = get_period_str(periods)
    print(result)
    print_overpayment(principal, payment, periods)


def calculate_periods(principal: float,
                      payment: float,
                      nominal_interest: float) -> float:
    log_base = 1 + nominal_interest
    log_param = payment / (payment - nominal_interest * principal)
    return log(log_param) / log(log_base)


def get_period_str(months_count: float) -> str:
    years = months_count // MONTHS_IN_YEAR
    months = months_count % MONTHS_IN_YEAR
    result = "You need "
    if years != 0:
        result += str(years)
        result += " year" if years == 1 else " years"
    if years != 0 and months != 0:
        result += " and "
    if months != 0:
        result += str(months)
        result += " month" if months == 1 else " months"
    result += " to repay this credit!"
    return result


def print_overpayment(principal: float, payment: float, periods: float):
    overpayment = round(periods * payment - principal)
    print("Overpayment =", overpayment)


def calculate_annuity(principal: int,
                      periods: int,
                      nominal_interest: float):
    coefficient = calculate_coefficient(periods, nominal_interest)
    annuity = ceil(principal * coefficient)
    print(f"Your annuity payment = {annuity}!")
    print_overpayment(principal, annuity, periods)


def calculate_coefficient(periods: int, nominal_interest: float) -> float:
    divisible = nominal_interest * (1 + nominal_interest) ** periods
    divisor = (1 + nominal_interest) ** periods - 1
    coefficient = divisible / divisor
    return coefficient


def calculate_principal(payment: float,
                        periods: int,
                        nominal_interest: float):
    coefficient = calculate_coefficient(periods, nominal_interest)
    principal = floor(payment / coefficient)
    print(f"Your credit principal = {principal}!")
    print_overpayment(principal, payment, periods)


def calculate_diff_payment(i: int,
                           periods: int,
                           principal: int,
                           nominal_interest: float) -> int:
    principal_part = principal / periods
    divisible = principal * (i - 1)
    multiplier = principal - divisible / periods
    diff_part = nominal_interest * multiplier
    return ceil(principal_part + diff_part)
