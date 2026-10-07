import datetime

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.services.llm import get_llm

SQL_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You write PostgreSQL queries for a personal finance app.\n\n"
     "Table: transactions\n"
     "- id integer\n- date date\n- description text\n- category text\n"
     "- amount numeric(12,2)\n- merchant text\n"
     "- transaction_type text: 'debit' = money spent, 'credit' = money received\n\n"
     "Known categories: {categories}\n"
     "Known merchants: {merchants}\n"
     "Today's date: {today}\n\n"
     "Rules:\n"
     "- Write exactly one SELECT query on the transactions table.\n"
     "- 'Spending' means transaction_type = 'debit'.\n"
     "- For 'how much' or total questions, return an aggregate (SUM, COUNT, AVG), not individual rows.\n"
     "- Use only the columns listed above.\n"
     "- Return only the SQL. No explanation, no markdown."),
    ("human", "{question}"),
])


def _clean_sql(raw: str) -> str:
    return raw.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


def generate_sql(db: Session, question: str) -> str:
    categories = db.scalars(select(Transaction.category).distinct()).all()
    merchants = db.scalars(select(Transaction.merchant).distinct()).all()

    chain = SQL_PROMPT | get_llm()
    response = chain.invoke({
        "categories": ", ".join(categories),
        "merchants": ", ".join(merchants),
        "today": datetime.date.today().isoformat(),
        "question": question,
    })
    return _clean_sql(response.text)
