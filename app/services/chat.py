from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.llm import get_llm
from app.services.sql_generator import generate_sql
from app.services.sql_validator import validate_sql

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You answer questions about the user's personal finances. "
     "Use only the query result provided. Amounts are in Indian Rupees (₹). "
     "If the result is empty, say that no matching transactions were found. "
     "Answer in 1-3 short sentences."),
    ("human", "Question: {question}\nSQL used: {sql}\nQuery result: {rows}"),
])


def run_readonly_query(db: Session, sql: str) -> list[dict]:
    db.rollback()
    try:
        db.execute(text("SET TRANSACTION READ ONLY"))
        db.execute(text("SET LOCAL statement_timeout = '5s'"))
        return [dict(row._mapping) for row in db.execute(text(sql))]
    finally:
        db.rollback()


def answer_question(db: Session, question: str) -> dict:
    sql = validate_sql(generate_sql(db, question))
    rows = run_readonly_query(db, sql)
    chain = ANSWER_PROMPT | get_llm()
    answer = chain.invoke({"question": question, "sql": sql, "rows": rows}).text
    return {"answer": answer, "sql": sql, "rows": rows}
