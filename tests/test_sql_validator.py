import pytest

from app.services.sql_validator import UnsafeSQLError, validate_sql


@pytest.mark.parametrize("sql", [
    "SELECT SUM(amount) FROM transactions",
    "SELECT merchant, SUM(amount) FROM transactions GROUP BY merchant",
    "SELECT * FROM transactions WHERE EXTRACT(MONTH FROM date) = 9",
])
def test_allows_safe_select(sql):
    assert validate_sql(sql).startswith("SELECT")


@pytest.mark.parametrize("sql", [
    "DELETE FROM transactions",
    "DROP TABLE transactions",
    "UPDATE transactions SET amount = 0",
    "SELECT 1; DROP TABLE transactions",
    "SELECT * FROM pg_user",
    "WITH d AS (DELETE FROM transactions RETURNING *) SELECT * FROM d",
    "not even sql",
])
def test_blocks_unsafe_sql(sql):
    with pytest.raises(UnsafeSQLError):
        validate_sql(sql)


def test_adds_limit_when_missing():
    assert validate_sql("SELECT * FROM transactions").endswith("LIMIT 100")
