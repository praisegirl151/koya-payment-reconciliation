
#!/usr/bin/env python3

"""Payment reconciliation."""

import json
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def main():
    latest_attempts = {}

    payments_file = BASE_DIR / "payments.jsonl"

    with payments_file.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(event, dict):
                continue

            txn_id = event.get("txn_id")
            if not txn_id:
                continue

            timestamp = event.get("ts")
            if not timestamp:
                continue

            previous = latest_attempts.get(txn_id)

            # Keep only the latest attempt for each transaction.
            # If timestamps tie, keep the later line in the file.
            if previous is None or timestamp >= previous["ts"]:
                latest_attempts[txn_id] = event

    total = Decimal("0")
    count = 0

    for event in latest_attempts.values():
        if event.get("status") == "success":
            amount = str(event["amount"]).replace(",", "")
            total += Decimal(amount)
            count += 1

    expected_file = BASE_DIR / "expected.txt"
    expected = int(expected_file.read_text(encoding="utf-8").strip())

    if count != expected:
        print(
            f"Check failed: counted {count} successful payments, "
            f"expected {expected}."
        )
        print("Something in the data isn't being handled as expected.")
        return

    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")


if __name__ == "__main__":
    main()
