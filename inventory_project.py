import pandas as pd

df = pd.read_csv("supply_chain_project_ready (1).csv")

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nFirst 5 rows:")
print(df.head())

print("\nColumn names:")
print(df.columns.tolist())

print("INVENTORY STATUS SUMMARY")
print("------------------------")

print(df["Inventory_Status"].value_counts())

transfer_opportunities = (df["Suggested_Transfer_Qty"] > 0).sum()

print("\nTransfer opportunities:", transfer_opportunities)

print("\nSAMPLE TRANSFER RECOMMENDATIONS")
print("-------------------------------")

sample_transfers = df[df["Suggested_Transfer_Qty"] > 0][[
    "SKU_ID",
    "Warehouse_ID",
    "Suggested_Donor_Warehouse",
    "Suggested_Transfer_Qty",
    "Minimum_Replenishment_After_Transfer"
]].head(10)

print(sample_transfers.to_string(index=False))

print("\nBEFORE VS AFTER OPTIMIZATION")
print("-----------------------------")

low_stock = df[df["Inventory_Status"] == "LOW"]

total_shortage_before = low_stock["Shortage_To_Reorder_Point"].sum()
total_transfer = low_stock["Suggested_Transfer_Qty"].sum()
remaining_replenishment = low_stock["Minimum_Replenishment_After_Transfer"].sum()

resolved_percent = (total_transfer / total_shortage_before) * 100

print("Total shortage before transfers:", total_shortage_before)
print("Units resolved through warehouse transfers:", total_transfer)
print("Remaining supplier replenishment required:", remaining_replenishment)
print("Percentage of shortage resolved internally:", round(resolved_percent, 2), "%")

print("\nSUPPLY CHAIN STRESS TEST")
print("------------------------")

base_risk = (df["Model_Stockout_Flag"] == 1).sum()

# Scenario 1: Demand increases by 20%
demand_shock = (
    df["Future_Demand_Over_Lead_Time"] * 1.20 > df["Inventory_Level"]
).sum()

# Scenario 2: Inventory falls by 20%
inventory_shock = (
    df["Future_Demand_Over_Lead_Time"] > df["Inventory_Level"] * 0.80
).sum()

# Scenario 3: Supplier lead time increases by 3 days
extra_daily_demand = df["Rolling_7D_Avg_Demand"] * 3

lead_time_shock = (
    df["Future_Demand_Over_Lead_Time"] + extra_daily_demand
    > df["Inventory_Level"]
).sum()

print("Current risky positions:", base_risk)
print("Risky positions with 20% demand increase:", demand_shock)
print("Risky positions with 20% inventory reduction:", inventory_shock)
print("Risky positions with supplier lead time +3 days:", lead_time_shock)

print("\nPRIORITY & ACTION ENGINE")
print("------------------------")

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

print("\nPriority summary:")
print(df["Priority"].value_counts())

print("\nRecommended action summary:")
print(df["Recommended_Action"].value_counts())

print("\nTOP CRITICAL INVENTORY CASES")
print("----------------------------")

critical_cases = df[df["Priority"] == "CRITICAL"][[
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

print(critical_cases.to_string(index=False))

print("\nNETWORK HEALTH SCORE")
print("--------------------")

# -------------------------
# BEFORE OPTIMIZATION
# -------------------------

eligible = df[df["Model_Eligible"] == 1]

stockout_rate_before = eligible["Model_Stockout_Flag"].mean()
low_inventory_rate_before = (df["Inventory_Status"] == "LOW").mean()

unresolved_shortage_rate_before = 1.0

health_before = 100 - (
    50 * stockout_rate_before
    + 30 * low_inventory_rate_before
    + 20 * unresolved_shortage_rate_before
)

# -------------------------
# AFTER INTERNAL TRANSFERS
# -------------------------

df["Inventory_After_Transfer"] = (
    df["Inventory_Level"] + df["Suggested_Transfer_Qty"]
)

df["Simulated_Stockout_After_Transfer"] = (
    df["Future_Demand_Over_Lead_Time"] > df["Inventory_After_Transfer"]
).astype(int)

eligible_after = df[df["Model_Eligible"] == 1]

stockout_rate_after = eligible_after[
    "Simulated_Stockout_After_Transfer"
].mean()

low_inventory_rate_after = (
    df["Inventory_After_Transfer"] < df["Reorder_Point"]
).mean()

unresolved_shortage_rate_after = (
    remaining_replenishment / total_shortage_before
)

health_after = 100 - (
    50 * stockout_rate_after
    + 30 * low_inventory_rate_after
    + 20 * unresolved_shortage_rate_after
)

print("Network Health Score BEFORE optimization:",
      round(health_before, 2), "/ 100")

print("Network Health Score AFTER internal rebalancing:",
      round(health_after, 2), "/ 100")

print("Improvement:",
      round(health_after - health_before, 2), "points")