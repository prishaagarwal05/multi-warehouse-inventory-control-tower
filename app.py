import streamlit as st

st.set_page_config(
    page_title="Supply Chain Control Tower",
    layout="wide"
)

st.title("Supply Chain Control Tower")
st.subheader("Predictive Multi-Warehouse Inventory Optimization & Stockout Risk")

st.write(
    "This dashboard presents stockout risk, inventory rebalancing, "
    "replenishment recommendations, and supply chain stress-test results."
)

st.success("Dashboard loaded successfully!")

import pandas as pd

df = pd.read_csv("supply_chain_project_ready (1).csv")

total_risky = (df["Model_Stockout_Flag"] == 1).sum()
transfer_opportunities = (df["Suggested_Transfer_Qty"] > 0).sum()
critical_cases = 277
health_before = 76.61
health_after = 98.03

st.markdown("## Executive Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Stockout Risk Cases", f"{total_risky:,}")
col2.metric("Transfer Opportunities", f"{transfer_opportunities:,}")
col3.metric("Critical Cases", f"{critical_cases:,}")
col4.metric(
    "Network Health Score",
    f"{health_after:.2f}/100",
    f"+{health_after - health_before:.2f} pts"
)
# Create priority and action fields

def assign_priority(row):
    if row["Model_Stockout_Flag"] == 1 and row["Shortage_To_Reorder_Point"] > 20:
        return "CRITICAL"
    elif row["Model_Stockout_Flag"] == 1:
        return "HIGH"
    elif row["Below_Reorder_Point"] == 1:
        return "MEDIUM"
    else:
        return "HEALTHY"


def recommend_action(row):
    shortage = row["Shortage_To_Reorder_Point"]
    transfer = row["Suggested_Transfer_Qty"]
    remaining = row["Minimum_Replenishment_After_Transfer"]

    if shortage == 0:
        return "NO ACTION"
    elif transfer >= shortage:
        return "TRANSFER"
    elif transfer > 0 and remaining > 0:
        return "TRANSFER + REORDER"
    else:
        return "REORDER"


df["Priority"] = df.apply(assign_priority, axis=1)
df["Recommended_Action"] = df.apply(recommend_action, axis=1)

st.markdown("## Critical Inventory Cases")

critical_table = df[df["Priority"] == "CRITICAL"][[
    "SKU_ID",
    "Warehouse_ID",
    "Shortage_To_Reorder_Point",
    "Suggested_Donor_Warehouse",
    "Suggested_Transfer_Qty",
    "Minimum_Replenishment_After_Transfer",
    "Recommended_Action"
]].sort_values(
    by="Shortage_To_Reorder_Point",
    ascending=False
).head(10)

st.dataframe(
    critical_table,
    use_container_width=True,
    hide_index=True
)
st.markdown("## Inventory Rebalancing Impact")

low_stock = df[df["Inventory_Status"] == "LOW"]

total_shortage = low_stock["Shortage_To_Reorder_Point"].sum()
total_transfer = low_stock["Suggested_Transfer_Qty"].sum()
remaining_replenishment = low_stock[
    "Minimum_Replenishment_After_Transfer"
].sum()

resolved_percent = (total_transfer / total_shortage) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Initial Shortage", f"{total_shortage:,.0f} units")
col2.metric("Resolved via Transfers", f"{total_transfer:,.0f} units")
col3.metric("Supplier Replenishment", f"{remaining_replenishment:,.0f} units")
col4.metric("Resolved Internally", f"{resolved_percent:.2f}%")
st.markdown("## Supply Chain Stress Test")

demand_increase = st.slider(
    "Demand increase (%)",
    min_value=0,
    max_value=50,
    value=20,
    step=5
)

inventory_reduction = st.slider(
    "Inventory reduction (%)",
    min_value=0,
    max_value=50,
    value=20,
    step=5
)

lead_time_increase = st.slider(
    "Supplier lead-time increase (days)",
    min_value=0,
    max_value=10,
    value=3,
    step=1
)

base_risk = (df["Model_Stockout_Flag"] == 1).sum()

demand_shock = (
    df["Future_Demand_Over_Lead_Time"] * (1 + demand_increase / 100)
    > df["Inventory_Level"]
).sum()

inventory_shock = (
    df["Future_Demand_Over_Lead_Time"]
    > df["Inventory_Level"] * (1 - inventory_reduction / 100)
).sum()

lead_time_shock = (
    df["Future_Demand_Over_Lead_Time"]
    + df["Rolling_7D_Avg_Demand"] * lead_time_increase
    > df["Inventory_Level"]
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Risky Positions", f"{base_risk:,}")
col2.metric("Demand Shock", f"{demand_shock:,}")
col3.metric("Inventory Shock", f"{inventory_shock:,}")
col4.metric("Lead-Time Shock", f"{lead_time_shock:,}")
st.markdown("## Inventory Decision Lookup")

selected_warehouse = st.selectbox(
    "Select Warehouse",
    sorted(df["Warehouse_ID"].unique())
)

warehouse_data = df[df["Warehouse_ID"] == selected_warehouse]

selected_sku = st.selectbox(
    "Select SKU",
    sorted(warehouse_data["SKU_ID"].unique())
)

selected_case = warehouse_data[
    warehouse_data["SKU_ID"] == selected_sku
].sort_values("Date").iloc[-1]

st.markdown("### Current Inventory Position")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Inventory Level",
    f"{selected_case['Inventory_Level']:,.0f}"
)

col2.metric(
    "Reorder Point",
    f"{selected_case['Reorder_Point']:,.0f}"
)

col3.metric(
    "Shortage",
    f"{selected_case['Shortage_To_Reorder_Point']:,.0f}"
)

col4.metric(
    "Stockout Risk",
    "YES" if selected_case["Model_Stockout_Flag"] == 1 else "NO"
)

st.markdown("### Recommended Action")

action = selected_case["Recommended_Action"]

if action == "TRANSFER":
    st.success(
        f"Transfer {selected_case['Suggested_Transfer_Qty']:.0f} units "
        f"from {selected_case['Suggested_Donor_Warehouse']}."
    )

elif action == "TRANSFER + REORDER":
    st.warning(
        f"Transfer {selected_case['Suggested_Transfer_Qty']:.0f} units "
        f"from {selected_case['Suggested_Donor_Warehouse']} and reorder "
        f"{selected_case['Minimum_Replenishment_After_Transfer']:.0f} units "
        f"from the supplier."
    )

elif action == "REORDER":
    st.error(
        f"Reorder {selected_case['Minimum_Replenishment_After_Transfer']:.0f} "
        f"units from the supplier."
    )

else:
    st.info("No immediate inventory action required.")

print("\nFINANCIAL IMPACT OF INVENTORY REBALANCING")
print("------------------------------------------")

low_stock = df[df["Inventory_Status"] == "LOW"].copy()

low_stock["Shortage_Value"] = (
    low_stock["Shortage_To_Reorder_Point"] * low_stock["Unit_Cost"]
)

low_stock["Transfer_Value"] = (
    low_stock["Suggested_Transfer_Qty"] * low_stock["Unit_Cost"]
)

low_stock["Remaining_Replenishment_Value"] = (
    low_stock["Minimum_Replenishment_After_Transfer"]
    * low_stock["Unit_Cost"]
)

total_shortage_value = low_stock["Shortage_Value"].sum()
total_transfer_value = low_stock["Transfer_Value"].sum()
remaining_replenishment_value = low_stock[
    "Remaining_Replenishment_Value"
].sum()

internal_value_percent = (
    total_transfer_value / total_shortage_value
) * 100

print("Total shortage value before rebalancing:",
      round(total_shortage_value, 2))

print("Inventory value covered through internal transfers:",
      round(total_transfer_value, 2))

print("Remaining value requiring supplier replenishment:",
      round(remaining_replenishment_value, 2))

print("Percentage of shortage value covered internally:",
      round(internal_value_percent, 2), "%")