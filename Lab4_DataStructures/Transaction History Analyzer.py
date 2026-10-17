"""Generate and summarize an individualized transaction dataset."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal


# Student-specific inputs
LAST_NAME = "COPON"
STUDENT_ID = "TUPM-26-1942"
SEED_NUM = 2
FAVORITE_ARTIST = "LEVERFALL"

PRODUCT_PRICES = {
    "NOTEBOOK": Decimal("30.00"),
    "PEN": Decimal("10.00"),
    "USB": Decimal("250.00"),
    "HEADPHONES": Decimal("700.00"),
    "CALCULATOR": Decimal("500.00"),
}


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    customer: str
    product: str
    quantity: int
    unit_price: Decimal

    @property
    def total_value(self) -> Decimal:
        return self.quantity * self.unit_price


def customer_names() -> list[str]:
    return [f"C{number}-{LAST_NAME}" for number in range(1, 6)]


def quantity_for(
    transaction_index: int,
    customer_index: int,
    product_index: int,
) -> int:
    artist_letters = [character.upper() for character in FAVORITE_ARTIST if character.isalpha()]
    if not artist_letters:
        raise ValueError("FAVORITE_ARTIST must contain at least one letter.")

    artist_index = (transaction_index + SEED_NUM) % len(artist_letters)
    artist_position = artist_index + 1
    artist_letter_value = ord(artist_letters[artist_index]) - ord("A") + 1
    return (
        SEED_NUM + transaction_index + artist_position + artist_letter_value
        + customer_index + product_index
    ) % 10 + 1


def generate_transactions() -> list[Transaction]:
    customers = customer_names()
    products = list(PRODUCT_PRICES)
    transactions: list[Transaction] = []

    for customer_index, customer in enumerate(customers):
        for product_index, product in enumerate(products):
            transaction_index = len(transactions)
            transactions.append(
                Transaction(
                    transaction_id=f"T{transaction_index + 1:03d}",
                    customer=customer,
                    product=product,
                    quantity=quantity_for(
                        transaction_index,
                        customer_index,
                        product_index,
                    ),
                    unit_price=PRODUCT_PRICES[product],
                )
            )

    # Record a second purchase of the first customer-product pair.
    repeated = transactions[0]
    transaction_index = len(transactions)
    transactions.append(
        Transaction(
            transaction_id=f"T{transaction_index + 1:03d}",
            customer=repeated.customer,
            product=repeated.product,
            quantity=quantity_for(transaction_index, 0, 0),
            unit_price=repeated.unit_price,
        )
    )
    return transactions


def summarize(
    transactions: list[Transaction],
) -> tuple[
    dict[str, dict[str, object]],
    dict[str, dict[str, object]],
    Counter[tuple[str, str]],
]:
    customer_summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {"transactions": 0, "units": 0, "value": Decimal("0.00")}
    )
    product_summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {"transactions": 0, "units": 0, "value": Decimal("0.00")}
    )
    purchase_counts = Counter(
        (transaction.customer, transaction.product)
        for transaction in transactions
    )

    for transaction in transactions:
        for summary, key in (
            (customer_summary, transaction.customer),
            (product_summary, transaction.product),
        ):
            summary[key]["transactions"] = int(summary[key]["transactions"]) + 1
            summary[key]["units"] = int(summary[key]["units"]) + transaction.quantity
            summary[key]["value"] = (
                Decimal(summary[key]["value"]) + transaction.total_value
            )

    return customer_summary, product_summary, purchase_counts


def main() -> None:
    transactions = generate_transactions()
    customer_summary, product_summary, purchase_counts = summarize(transactions)
    total_units = sum(transaction.quantity for transaction in transactions)
    total_value = sum(
        (transaction.total_value for transaction in transactions),
        Decimal("0.00"),
    )
    repeated_purchases = sorted(
        (pair, count) for pair, count in purchase_counts.items() if count > 1
    )

    print("FINAL CONSOLIDATED TRANSACTION REPORT")
    print("=" * 100)
    print(
        f"Student: {LAST_NAME} | ID: {STUDENT_ID} | "
        f"SEED_NUM: {SEED_NUM} | Favorite artist: {FAVORITE_ARTIST}"
    )
    print(
        "Quantity rule: combine SEED_NUM, transaction index, customer/product "
        "indexes, and the selected artist letter's 1-based position and A1Z26 value; "
        "map the result to 1-10."
    )
    print("Fixed product prices: " + ", ".join(
        f"{product} PHP {price:.2f}" for product, price in PRODUCT_PRICES.items()
    ))

    print("\nGENERATED TRANSACTIONS (ordered by transaction ID)")
    print(
        f"{'ID':<6} {'CUSTOMER':<15} {'PRODUCT':<15} "
        f"{'QUANTITY':>8} {'UNIT PRICE (PHP)':>18} {'TOTAL VALUE (PHP)':>19}"
    )
    print("-" * 88)
    for transaction in transactions:
        print(
            f"{transaction.transaction_id:<6} {transaction.customer:<15} "
            f"{transaction.product:<15} {transaction.quantity:>8} "
            f"{transaction.unit_price:>18.2f} "
            f"{transaction.total_value:>19.2f}"
        )

    print("\nREPEATED PURCHASES AND DISTINCT RECORDS")
    for (customer, product), count in repeated_purchases:
        print(f"Repeated purchase: {customer} bought {product} {count} times.")
    print(f"Distinct customers: {len({transaction.customer for transaction in transactions})}")
    print(f"Distinct products: {len({transaction.product for transaction in transactions})}")
    print(f"Distinct customer-product pairs: {len(purchase_counts)}")
    print(f"Repeated customer-product pairs: {len(repeated_purchases)}")

    print("\nCUSTOMER SUMMARIES (ordered by transaction value, highest first)")
    print(f"{'CUSTOMER':<15} {'ORDERS':>8} {'UNITS':>8} {'TOTAL VALUE (PHP)':>19}")
    print("-" * 54)
    for customer in sorted(
        customer_summary,
        key=lambda name: (-Decimal(customer_summary[name]["value"]), name),
    ):
        summary = customer_summary[customer]
        print(
            f"{customer:<15} {summary['transactions']:>8} "
            f"{summary['units']:>8} {Decimal(summary['value']):>19.2f}"
        )

    print("\nPRODUCT SUMMARIES (ordered by transaction value, highest first)")
    print(f"{'PRODUCT':<15} {'ORDERS':>8} {'UNITS':>8} {'TOTAL VALUE (PHP)':>19}")
    print("-" * 54)
    for product in sorted(
        product_summary,
        key=lambda name: (-Decimal(product_summary[name]["value"]), name),
    ):
        summary = product_summary[product]
        print(
            f"{product:<15} {summary['transactions']:>8} "
            f"{summary['units']:>8} {Decimal(summary['value']):>19.2f}"
        )

    print("\nOVERALL TRANSACTION SUMMARY")
    print(f"Transaction records: {len(transactions)}")
    print(f"Total units sold: {total_units}")
    print(f"Distinct customers: {len(customer_summary)}")
    print(f"Distinct products: {len(product_summary)}")
    print(f"Distinct customer-product pairs: {len(purchase_counts)}")
    print(f"Repeated customer-product pairs: {len(repeated_purchases)}")
    print(f"Overall transaction value: PHP {total_value:.2f}")


if __name__ == "__main__":
    main()
