import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="FinSight AI", page_icon="💰", layout="wide")
st.title("💰 FinSight AI")
st.caption("Intelligent Financial Data Assistant")


def call_api(method: str, path: str, **kwargs):
    try:
        response = httpx.request(method, f"{API_URL}{path}", timeout=120, **kwargs)
    except httpx.ConnectError:
        st.error(f"Cannot reach the API at {API_URL}. Is the FastAPI server running?")
        st.stop()
    if response.is_error:
        detail = response.json().get("detail", response.text)
        st.error(detail[0]["msg"] if isinstance(detail, list) else detail)
        return None
    return response.json()


def totals_chart(rows: list[dict]) -> None:
    if rows:
        st.bar_chart(pd.DataFrame(rows).astype({"total": float}).set_index("name"))
    else:
        st.info("No data yet.")


dashboard_tab, ask_tab, upload_tab, anomalies_tab = st.tabs(
    ["📊 Dashboard", "💬 Ask", "📤 Upload", "🚨 Anomalies"]
)

with dashboard_tab:
    summary = call_api("GET", "/analytics/summary")
    if summary:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total spending", f"₹{float(summary['total_spending']):,.2f}")
        col2.metric("Average transaction", f"₹{float(summary['average_transaction']):,.2f}")
        col3.metric("Highest transaction", f"₹{float(summary['highest_transaction']):,.2f}")

        left, right = st.columns(2)
        with left:
            st.subheader("Spending by category")
            totals_chart(summary["by_category"])
        with right:
            st.subheader("Spending by month")
            totals_chart(summary["by_month"])

        st.subheader("Top merchants")
        totals_chart(summary["top_merchants"])

with ask_tab:
    mode = st.radio(
        "Ask about",
        ["data", "document"],
        format_func=lambda m: "My transactions" if m == "data" else "My documents",
        horizontal=True,
    )
    question = st.text_input("Your question", placeholder="How much did I spend on food?")
    if st.button("Ask", type="primary") and question:
        with st.spinner("Thinking..."):
            result = call_api("POST", "/chat", json={"question": question, "mode": mode})
        if result:
            st.success(result["answer"])
            if result.get("sql"):
                with st.expander("SQL used"):
                    st.code(result["sql"], language="sql")
            if result.get("rows"):
                st.dataframe(result["rows"])
            if result.get("sources"):
                st.caption("Sources: " + ", ".join(result["sources"]))

with upload_tab:
    st.subheader("Transactions (CSV)")
    csv_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if csv_file and st.button("Upload transactions"):
        result = call_api("POST", "/transactions/upload",
                          files={"file": (csv_file.name, csv_file.getvalue(), "text/csv")})
        if result:
            st.success(f"Inserted {result['inserted']} transactions.")

    st.subheader("Documents (PDF or TXT)")
    doc_file = st.file_uploader("Choose a document", type=["pdf", "txt"])
    if doc_file and st.button("Upload document"):
        result = call_api("POST", "/documents/upload",
                          files={"file": (doc_file.name, doc_file.getvalue())})
        if result:
            st.success(f"Indexed {result['filename']} into {result['chunks']} chunks.")

with anomalies_tab:
    st.write("Transactions that look unusual compared to your normal spending (Isolation Forest).")
    flagged = call_api("GET", "/analytics/anomalies")
    if flagged:
        st.dataframe(pd.DataFrame(flagged), hide_index=True)
    elif flagged == []:
        st.info("No unusual transactions found.")
