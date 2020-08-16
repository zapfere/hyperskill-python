from argparse import ArgumentParser, Namespace
from impl.calculators import AnnuityCalculator, DifferentiatedCalculator


class IncorrectParametersError(Exception):
    pass


def main():
    try:
        args = get_args()
        verify_args(args)
        calculate(args)
    except IncorrectParametersError as err:
        print(err)
        print("Incorrect parameters")


def get_args():
    parser = ArgumentParser(description="""A simple credit calculator. 
    Supported features: calculation of differentiated monthly payment;
    calculation of months to repay, monthly payment or credit principal 
    for annuity payments.""")
    parser.add_argument("--type",
                        type=str,
                        choices=["annuity", "diff"],
                        help="type of calculation",
                        required=True)
    parser.add_argument("--payment",
                        help="monthly payment, only for type=annuity",
                        type=float)
    parser.add_argument("--principal",
                        help="credit principal",
                        type=int)
    parser.add_argument("--periods",
                        help="number of months to repay the credit",
                        type=int)
    parser.add_argument("--interest",
                        help="annual interest, percent",
                        type=float)
    args = parser.parse_args()
    return args


def verify_args(args: Namespace):
    if args.interest is None:
        raise IncorrectParametersError(
            "Calculation of interest is not supported, "
            + "so the 'interest' argument should be set"
        )
    if args.type == "diff" and args.payment:
        raise IncorrectParametersError(
            "Parameter 'payment' is incompatible with 'type=diff'"
        )
    args_values = list(filter(lambda x: x is not None, args.__dict__.values()))
    if len(args_values) != 4:
        raise IncorrectParametersError(
            "Wrong number of arguments (4 expected)"
        )
    for arg in args_values:
        if type(arg) != str and arg < 0:
            raise IncorrectParametersError("Negative value detected")


def calculate(args: Namespace):
    if args.type == "diff":
        calculator = DifferentiatedCalculator(args)
    else:
        calculator = AnnuityCalculator(args)
    calculator.calculate()


if __name__ == '__main__':
    main()
