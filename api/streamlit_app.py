import requests
import streamlit as st
import plotly.graph_objects as go
import os

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000",
)

st.set_page_config(
    page_title="Battery Asset Optimization",
    page_icon="🔋",
    layout="wide",
)

st.title("🔋 Battery Asset Optimization")
st.caption(
    "Interactive battery dispatch optimization for electricity trading"
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Battery Parameters")

capacity = st.sidebar.number_input(
    "Capacity (MWh)",
    min_value=1.0,
    value=100.0,
)

initial_soc = st.sidebar.number_input(
    "Initial SOC (MWh)",
    min_value=0.0,
    value=50.0,
)

min_soc = st.sidebar.number_input(
    "Minimum SOC (MWh)",
    min_value=0.0,
    value=10.0,
)

max_soc = st.sidebar.number_input(
    "Maximum SOC (MWh)",
    min_value=1.0,
    value=90.0,
)

max_charge = st.sidebar.number_input(
    "Maximum charge (MW)",
    min_value=0.0,
    value=25.0,
)

max_discharge = st.sidebar.number_input(
    "Maximum discharge (MW)",
    min_value=0.0,
    value=25.0,
)

charge_efficiency = st.sidebar.number_input(
    "Charge efficiency",
    min_value=0.01,
    max_value=1.0,
    value=0.95,
)

discharge_efficiency = st.sidebar.number_input(
    "Discharge efficiency",
    min_value=0.01,
    max_value=1.0,
    value=0.95,
)

degradation_cost = st.sidebar.number_input(
    "Degradation cost (€/MWh)",
    min_value=0.0,
    value=5.0,
    help="Estimated cost of battery wear caused by charging and discharging. It discourages unnecessary cycling and represents the economic value of battery lifetime.",
)

run = st.sidebar.button(
    "Run Optimization",
    type="primary",
    use_container_width=True,
)

# ---------------------------------------------------------
# Optimization
# ---------------------------------------------------------

if run:

    payload = {
        "capacity_mwh": capacity,
        "initial_soc_mwh": initial_soc,
        "min_soc_mwh": min_soc,
        "max_soc_mwh": max_soc,
        "max_charge_mw": max_charge,
        "max_discharge_mw": max_discharge,
        "charge_efficiency": charge_efficiency,
        "discharge_efficiency": discharge_efficiency,
        "degradation_cost_eur_mwh": degradation_cost,
    }

    with st.spinner("Running optimization..."):

        response = requests.post(
            f"{API_URL}/optimize",
            json=payload,
            timeout=60,
        )

    if response.status_code != 200:

        st.error(
            f"Optimization failed: {response.text}"
        )

    else:

        result = response.json()

        # -------------------------------------------------
        # KPI cards
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Expected Profit",
            f"€{result['expected_profit_eur']:,.2f}",
        )

        col2.metric(
            "Realized Profit",
            f"€{result['realized_profit_eur']:,.2f}",
        )

        col3.metric(
            "Realized Uplift",
            f"€{result['realized_uplift_eur']:,.2f}",
        )

        # -------------------------------------------------
        # Dispatch dataframe
        # -------------------------------------------------

        dispatch = result["dispatch"]

        timestamps = [
            row["timestamp"]
            for row in dispatch
        ]

        prices = [
            row["price_eur_mwh"]
            for row in dispatch
        ]

        charge = [
            row["charge_mwh"]
            for row in dispatch
        ]

        discharge = [
            row["discharge_mwh"]
            for row in dispatch
        ]

        soc = [
            row["soc_mwh"]
            for row in dispatch
        ]

        # -------------------------------------------------
        # Dispatch chart
        # -------------------------------------------------

        st.subheader("Market Price & Battery Dispatch")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=prices,
                name="Price",
                yaxis="y1",
                mode="lines+markers",
            )
        )

        fig.add_trace(
            go.Bar(
                x=timestamps,
                y=charge,
                name="Charge",
                yaxis="y2",
            )
        )

        fig.add_trace(
            go.Bar(
                x=timestamps,
                y=[-x for x in discharge],
                name="Discharge",
                yaxis="y2",
            )
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis=dict(
                title="Price (€/MWh)",
            ),
            yaxis2=dict(
                title="Power (MW)",
                overlaying="y",
                side="right",
            ),
            hovermode="x unified",
            height=500,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        # -------------------------------------------------
        # SOC chart
        # -------------------------------------------------

        st.subheader("Battery State of Charge")

        soc_fig = go.Figure()

        soc_fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=soc,
                mode="lines+markers",
                name="SOC",
            )
        )

        soc_fig.update_layout(
            xaxis_title="Time",
            yaxis_title="SOC (MWh)",
            yaxis_range=[0, capacity],
            height=400,
        )

        st.plotly_chart(
            soc_fig,
            use_container_width=True,
        )

        # -------------------------------------------------
        # Diagnostics
        # -------------------------------------------------

        st.subheader("Optimization Diagnostics")

        diagnostics = result["validation"]

        d1, d2, d3 = st.columns(3)

        d1.metric(
            "Minimum SOC",
            f"{min(soc):.2f} MWh",
        )

        d2.metric(
            "Maximum SOC",
            f"{max(soc):.2f} MWh",
        )

        d3.metric(
            "Constraint Violations",
            str(len(diagnostics.get("violations", []))),
        )

        # -------------------------------------------------
        # Dispatch table
        # -------------------------------------------------

        with st.expander("View dispatch data"):
            st.dataframe(
                dispatch,
                use_container_width=True,
            )