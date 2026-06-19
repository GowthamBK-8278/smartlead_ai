import streamlit as st
from data.sample_data import get_sample_data
from database.dashboard import get_dashboard_data
from analysis.lead_scoring import (
    calculate_interest_score,
    get_sentiment
)
from excel.exporter import export_to_excel

st.set_page_config(
    page_title="SmartLead AI",
    page_icon="📊",
    layout="wide"
)
from database.db_manager import (
    create_database,
    save_leads
)
create_database()
st.title("🚀 SmartLead AI")
st.subheader("Multi Domain Market Research Platform")

domains = [
    "Aviation",
    "Laptops",
    "Colleges"
]

selected_domain = st.selectbox(
    "Select Domain",
    domains
)
stats = get_dashboard_data()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Leads",
    stats["total_leads"]
)

col2.metric(
    "High Interest",
    stats["high_interest"]
)

col3.metric(
    "Domains",
    stats["domains"]
)

col4.metric(
    "Platforms",
    stats["platforms"]
)

if st.button("Fetch Leads"):

    try:

        # Fetch Data
        df = get_sample_data(selected_domain)

        # Interest Score
        df["Interest Score"] = df["Comment"].apply(
            calculate_interest_score
        )

        # Sentiment
        df["Sentiment"] = df["Interest Score"].apply(
            get_sentiment
        )

        # Display Table
        st.subheader("Lead Analysis")
        st.dataframe(df)

        save_leads(
            df,
            selected_domain
        )

        st.success(
            "✅ Data Saved To Database"
        )

        # Export Excel
        file_path = export_to_excel(
            df,
            selected_domain
        )

        st.success("✅ Excel Saved Successfully!")

        st.write("📁 File Location:")
        st.code(file_path)

    except Exception as e:

        st.error(
            f"❌ Error: {e}"
        )