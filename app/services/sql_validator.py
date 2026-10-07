import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {"transactions"}
MAX_ROWS = 100
FORBIDDEN_NODES = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.Command)


class UnsafeSQLError(ValueError):
    pass


def validate_sql(sql: str) -> str:
    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
    except sqlglot.errors.ParseError:
        raise UnsafeSQLError("Invalid SQL")
    if len(statements) != 1:
        raise UnsafeSQLError("Only a single statement is allowed")

    tree = statements[0]
    if not isinstance(tree, exp.Select) or tree.find(*FORBIDDEN_NODES):
        raise UnsafeSQLError("Only SELECT queries are allowed")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    tables = {t.name.lower() for t in tree.find_all(exp.Table)} - cte_names
    if not tables or not tables <= ALLOWED_TABLES:
        raise UnsafeSQLError(f"Only these tables are allowed: {sorted(ALLOWED_TABLES)}")

    if not tree.args.get("limit"):
        tree = tree.limit(MAX_ROWS)
    return tree.sql(dialect="postgres")
