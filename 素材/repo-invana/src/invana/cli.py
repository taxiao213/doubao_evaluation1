import argparse
import sys

from .repo import CsvOrderRepository
from .services import OrderService, ReportService
from .utils.text import indent


def main(argv=None):
    parser = argparse.ArgumentParser(prog="invana")
    parser.add_argument("command", choices=["summary", "totals"], help="子命令")
    parser.add_argument("orders_csv", help="订单明细 CSV 路径")
    args = parser.parse_args(argv)

    repo = CsvOrderRepository(args.orders_csv)
    if args.command == "summary":
        print(ReportService(repo).render_text())
    else:
        for oid, total in sorted(OrderService(repo).totals().items()):
            print(f"{oid}\t{total:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
