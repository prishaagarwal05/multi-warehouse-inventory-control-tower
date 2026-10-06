# Predictive Multi-Warehouse Inventory Optimization & Stockout Risk Control Tower

An end-to-end business analytics project for identifying stockout risk, predicting vulnerable SKU-warehouse positions, recommending inventory transfers or replenishment actions, stress testing the supply chain, and presenting decisions through an interactive Streamlit dashboard.

## Business Problem

In a multi-warehouse supply chain, the same SKU may be understocked in one warehouse while excess inventory exists in another. Instead of immediately placing a new supplier order, this project evaluates whether inventory can first be rebalanced across warehouses and whether future stockout risk can be predicted early enough for preventive action.

## Project Workflow

**Jamovi → Diagnostic Analytics**  
**Orange → Predictive Analytics**  
**Python → Prescriptive & Scenario Analytics**  
**Streamlit → Decision Support**

## Tools Used

- Jamovi
- Orange
- Python
- Pandas
- Streamlit
- Logistic Regression
- Random Forest
- Decision Tree

## Key Features

- Stockout driver analysis
- Logistic regression interpretation
- Classification model comparison
- 10-fold cross-validation
- Prediction on new unseen inventory observations
- Inter-warehouse transfer recommendations
- Supplier replenishment recommendations
- Priority and action engine
- Supply-chain stress testing
- Network Health Score
- Financial impact analysis
- Interactive Streamlit control tower

## Predictive Analytics

Logistic Regression, Random Forest, and Decision Tree models were compared in Orange. Logistic Regression was retained as the preferred model and was then applied to new inventory observations to demonstrate how stockout risk could be predicted on incoming data.

## Prescriptive Analytics

Python converts inventory risk into operational actions:

- No Action
- Transfer
- Reorder
- Transfer + Reorder

The rebalancing logic checks for excess inventory in other warehouses before recommending additional supplier replenishment.

## Stress Testing

The project evaluates how stockout exposure changes under:

- higher demand
- lower available inventory
- longer supplier lead times

## Streamlit Dashboard

The dashboard provides:

- Executive inventory KPIs
- Critical inventory cases
- Inventory rebalancing impact
- Interactive stress testing
- SKU and warehouse lookup
- Recommended inventory actions

## Limitations

- The dataset represents a modeled/simulated supply-chain environment.
- Transfer and handling costs are not included.
- The rebalancing logic is rule-based rather than a full mathematical optimization model.
- The Network Health Score is a project-specific KPI.
