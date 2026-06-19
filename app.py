import streamlit as st
import plotly.express as px

from data.sample_data import get_sample_data
from analysis.lead_scoring import calculate_interest_score, get_sentiment
from excel.exporter import export_to_excel
from database.db_manager import create_database, save_leads
from database.dashboard import get_dashboard_data
from database.view_leads import get_all_leads


st.set_page_config(
    page_title="SmartLead AI",
    page_icon="📊",
    layout="wide"
)

create_database()

st.title("🚀 SmartLead AI")
st.subheader("Multi Domain Market Research Platform")


# ---------------- DASHBOARD CARDS ----------------

stats = get_dashboard_data()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Leads", stats["total_leads"])
col2.metric("High Interest", stats["high_interest"])
col3.metric("Domains", stats["domains"])
col4.metric("Platforms", stats["platforms"])


# ---------------- FETCH LEADS ----------------

st.divider()
st.subheader("🔍 Fetch New Leads")

domains = [
    "Aviation",
    "Laptops",
    "Colleges"
]

selected_domain = st.selectbox(
    "Select Domain",
    domains
)

if st.button("Fetch Leads"):

    try:
        df = get_sample_data(selected_domain)

        df["Interest Score"] = df["Comment"].apply(
            calculate_interest_score
        )

        df["Sentiment"] = df["Interest Score"].apply(
            get_sentiment
        )

        st.subheader("Lead Analysis")
        st.dataframe(df, use_container_width=True)

        save_leads(df, selected_domain)
        st.success("✅ Data Saved To Database")

        file_path = export_to_excel(df, selected_domain)
        st.success("✅ Excel Saved Successfully")

        st.write("📁 File Location:")
        st.code(file_path)

    except Exception as e:
        st.error(f"❌ Error: {e}")


# ---------------- LEAD EXPLORER ----------------

st.divider()
st.subheader("📋 Lead Explorer")

leads_df = get_all_leads()

if not leads_df.empty:

    selected_domain_filter = st.selectbox(
        "Filter By Domain",
        ["All"] + list(leads_df["domain"].unique())
    )

    if selected_domain_filter != "All":
        leads_df = leads_df[
            leads_df["domain"] == selected_domain_filter
        ]

    selected_platform_filter = st.selectbox(
        "Filter By Platform",
        ["All"] + list(leads_df["platform"].unique())
    )

    if selected_platform_filter != "All":
        leads_df = leads_df[
            leads_df["platform"] == selected_platform_filter
        ]

    search_username = st.text_input("Search Username")

    if search_username:
        leads_df = leads_df[
            leads_df["username"].str.contains(
                search_username,
                case=False,
                na=False
            )
        ]

    st.dataframe(leads_df, use_container_width=True)


    # ---------------- ANALYTICS CHARTS ----------------

    st.divider()
    st.subheader("📊 Analytics Dashboard")

    sentiment_counts = leads_df["sentiment"].value_counts()

    fig1 = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Sentiment Distribution"
    )

    st.plotly_chart(fig1, use_container_width=True)


    domain_counts = leads_df["domain"].value_counts()

    fig2 = px.bar(
        x=domain_counts.index,
        y=domain_counts.values,
        title="Domain Wise Leads",
        labels={
            "x": "Domain",
            "y": "Lead Count"
        }
    )

    st.plotly_chart(fig2, use_container_width=True)


    platform_counts = leads_df["platform"].value_counts()

    fig3 = px.bar(
        x=platform_counts.index,
        y=platform_counts.values,
        title="Platform Wise Leads",
        labels={
            "x": "Platform",
            "y": "Lead Count"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("No Leads Found")