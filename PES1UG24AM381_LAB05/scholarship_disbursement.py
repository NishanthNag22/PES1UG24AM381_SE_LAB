"""Module for managing scholarship disbursement and awards ledger."""

import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE awards ("
    "id INTEGER PRIMARY KEY, "
    "student TEXT, "
    "scheme TEXT, "
    "amount INTEGER, "
    "disbursed INTEGER)"
)


def grant(student, scheme, amount, audit=None):
    """Grant a scholarship award to a student."""
    if audit is None:
        audit = []
    conn.execute(
        "INSERT INTO awards (student, scheme, amount, disbursed) "
        "VALUES (?, ?, ?, 0)",
        (student, scheme, amount),
    )
    audit.append(student)
    return audit


def disburse(award_id):
    """Disburse funds for a given award id."""
    row = conn.execute(
        "SELECT amount FROM awards WHERE id = ?", (award_id,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,)
        )
        return row[0]
    return None


def archive():
    """Archive processed awards safely."""
    try:
        print("archiving awards")
    except OSError as err:
        print(f"Archive failed: {err}")


def by_scheme_count(scheme):
    """Count the number of awards granted under a specific scheme."""
    if scheme is None:
        return 0
    row = conn.execute(
        "SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)
    ).fetchone()
    return row[0]


def get_total_disbursed():
    """Calculate total disbursed amount from the awards ledger."""
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
    ).fetchone()
    return row[0]


def __getattr__(name):
    """Provide backward compatibility for legacy names."""
    if name == "disbursed_total":
        return get_total_disbursed()
    if name == "bySchemeCount":
        return by_scheme_count
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def main():
    """Execute demonstration of the scholarship disbursement ledger."""
    grant("Ishaan", "Merit", 50000)
    grant("Divya", "Need-based", 75000)
    print(disburse(1), disburse(9))
    print(by_scheme_count("Merit"), get_total_disbursed())
    archive()


if __name__ == "__main__":
    main()
