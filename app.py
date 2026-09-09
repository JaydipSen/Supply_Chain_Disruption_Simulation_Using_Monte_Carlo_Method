import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Supply Chain Monte Carlo Simulator",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📦 Supply Chain Disruption Monte Carlo Simulator")

st.markdown(
    """
    This interactive application uses **Monte Carlo simulation** to evaluate
    supply-chain disruption risk.

    Change the input parameters in the sidebar and click **Run Simulation**
    to observe the impact on inventory, shortages, stockouts, and total cost.
    """
)


# ============================================================
# SIDEBAR — INPUT PARAMETERS
# ============================================================

st.sidebar.header("⚙️ Simulation Parameters")

initial_inventory = st.sidebar.number_input(
    "Initial Inventory",
    min_value=0,
    max_value=100000,
    value=600,
    step=50
)

weekly_demand = st.sidebar.number_input(
    "Weekly Demand",
    min_value=1,
    max_value=100000,
    value=450,
    step=50
)

normal_supply = st.sidebar.number_input(
    "Normal Weekly Supply",
    min_value=0,
    max_value=100000,
    value=500,
    step=50
)

disruption_supply = st.sidebar.number_input(
    "Supply During Disruption",
    min_value=0,
    max_value=100000,
    value=100,
    step=50
)

disruption_probability = st.sidebar.slider(
    "Disruption Probability",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.01,
    format="%.2f"
)

disruption_duration = st.sidebar.number_input(
    "Disruption Duration (Weeks)",
    min_value=1,
    max_value=20,
    value=2,
    step=1
)

holding_cost = st.sidebar.number_input(
    "Holding Cost ($/unit/week)",
    min_value=0.0,
    max_value=1000.0,
    value=2.0,
    step=0.50
)

shortage_cost = st.sidebar.number_input(
    "Shortage Cost ($/unit)",
    min_value=0.0,
    max_value=10000.0,
    value=15.0,
    step=1.0
)

weeks = st.sidebar.number_input(
    "Simulation Period (Weeks)",
    min_value=1,
    max_value=100,
    value=12,
    step=1
)

simulations = st.sidebar.number_input(
    "Number of Monte Carlo Simulations",
    min_value=100,
    max_value=100000,
    value=10000,
    step=1000
)

random_seed = st.sidebar.number_input(
    "Random Seed",
    min_value=0,
    max_value=100000,
    value=42,
    step=1
)


# ============================================================
# RUN BUTTON
# ============================================================

run_simulation_button = st.sidebar.button(
    "🚀 Run Simulation",
    type="primary",
    use_container_width=True
)


# ============================================================
# SIMULATION FUNCTION
# ============================================================

def run_simulation(
    weeks,
    simulations,
    initial_inventory,
    weekly_demand,
    normal_supply,
    disruption_supply,
    disruption_probability,
    disruption_duration,
    holding_cost,
    shortage_cost,
    random_seed
):

    np.random.seed(random_seed)

    # --------------------------------------------------------
    # SIMULATION-LEVEL RESULTS
    # --------------------------------------------------------

    total_costs = []
    total_shortages = []
    minimum_inventories = []
    stockout_occurs = []

    number_of_disruptions = []
    final_inventories = []

    total_holding_costs = []
    total_shortage_costs = []

    # --------------------------------------------------------
    # WEEKLY RESULTS
    # --------------------------------------------------------

    weekly_inventory = np.zeros(
        (simulations, weeks)
    )

    weekly_supply = np.zeros(
        (simulations, weeks)
    )

    weekly_shortage = np.zeros(
        (simulations, weeks)
    )

    weekly_stockout = np.zeros(
        (simulations, weeks)
    )

    weekly_disruption = np.zeros(
        (simulations, weeks)
    )

    # --------------------------------------------------------
    # SAMPLE SIMULATION
    # --------------------------------------------------------

    sample_inventory = None
    sample_supply = None
    sample_shortage = None
    sample_disruption = None

    # --------------------------------------------------------
    # MONTE CARLO LOOP
    # --------------------------------------------------------

    for sim in range(simulations):

        inventory = initial_inventory

        total_holding_cost = 0
        total_shortage_cost = 0
        total_shortage = 0

        min_inventory = inventory

        disruption_remaining = 0
        disruptions_this_simulation = 0

        simulation_inventory = []
        simulation_supply = []
        simulation_shortage = []
        simulation_disruption = []

        for week in range(weeks):

            # ------------------------------------------------
            # DETERMINE SUPPLY
            # ------------------------------------------------

            if disruption_remaining > 0:

                supply = disruption_supply

                disruption_remaining -= 1

                disruption = 1

            else:

                random_number = np.random.random()

                if random_number < disruption_probability:

                    supply = disruption_supply

                    disruption_remaining = (
                        disruption_duration - 1
                    )

                    disruption = 1

                    disruptions_this_simulation += 1

                else:

                    supply = normal_supply

                    disruption = 0

            # ------------------------------------------------
            # INVENTORY UPDATE
            # ------------------------------------------------

            inventory += supply

            inventory -= weekly_demand

            shortage = 0

            # ------------------------------------------------
            # SHORTAGE
            # ------------------------------------------------

            if inventory < 0:

                shortage = -inventory

                total_shortage += shortage

                total_shortage_cost += (
                    shortage * shortage_cost
                )

                # Lost sales / shortage reset
                inventory = 0

            else:

                total_holding_cost += (
                    inventory * holding_cost
                )

            # ------------------------------------------------
            # RECORD WEEKLY RESULTS
            # ------------------------------------------------

            min_inventory = min(
                min_inventory,
                inventory
            )

            weekly_inventory[
                sim, week
            ] = inventory

            weekly_supply[
                sim, week
            ] = supply

            weekly_shortage[
                sim, week
            ] = shortage

            weekly_stockout[
                sim, week
            ] = 1 if shortage > 0 else 0

            weekly_disruption[
                sim, week
            ] = disruption

            simulation_inventory.append(
                inventory
            )

            simulation_supply.append(
                supply
            )

            simulation_shortage.append(
                shortage
            )

            simulation_disruption.append(
                disruption
            )

        # ----------------------------------------------------
        # TOTAL COST
        # ----------------------------------------------------

        total_cost = (
            total_holding_cost
            + total_shortage_cost
        )

        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        total_costs.append(total_cost)

        total_shortages.append(
            total_shortage
        )

        minimum_inventories.append(
            min_inventory
        )

        final_inventories.append(
            inventory
        )

        number_of_disruptions.append(
            disruptions_this_simulation
        )

        total_holding_costs.append(
            total_holding_cost
        )

        total_shortage_costs.append(
            total_shortage_cost
        )

        if total_shortage > 0:

            stockout_occurs.append(1)

        else:

            stockout_occurs.append(0)

        # ----------------------------------------------------
        # STORE FIRST SIMULATION
        # ----------------------------------------------------

        if sim == 0:

            sample_inventory = simulation_inventory
            sample_supply = simulation_supply
            sample_shortage = simulation_shortage
            sample_disruption = simulation_disruption

    # --------------------------------------------------------
    # CONVERT TO NUMPY ARRAYS
    # --------------------------------------------------------

    total_costs = np.array(total_costs)

    total_shortages = np.array(
        total_shortages
    )

    minimum_inventories = np.array(
        minimum_inventories
    )

    stockout_occurs = np.array(
        stockout_occurs
    )

    final_inventories = np.array(
        final_inventories
    )

    number_of_disruptions = np.array(
        number_of_disruptions
    )

    total_holding_costs = np.array(
        total_holding_costs
    )

    total_shortage_costs = np.array(
        total_shortage_costs
    )

    # --------------------------------------------------------
    # RETURN RESULTS
    # --------------------------------------------------------

    return {
        "total_costs": total_costs,
        "total_shortages": total_shortages,
        "minimum_inventories": minimum_inventories,
        "stockout_occurs": stockout_occurs,
        "final_inventories": final_inventories,
        "number_of_disruptions": number_of_disruptions,
        "total_holding_costs": total_holding_costs,
        "total_shortage_costs": total_shortage_costs,
        "weekly_inventory": weekly_inventory,
        "weekly_supply": weekly_supply,
        "weekly_shortage": weekly_shortage,
        "weekly_stockout": weekly_stockout,
        "weekly_disruption": weekly_disruption,
        "sample_inventory": sample_inventory,
        "sample_supply": sample_supply,
        "sample_shortage": sample_shortage,
        "sample_disruption": sample_disruption
    }


# ============================================================
# RUN SIMULATION
# ============================================================

if run_simulation_button:

    with st.spinner("Running Monte Carlo simulation..."):

        results = run_simulation(
            weeks=weeks,
            simulations=simulations,
            initial_inventory=initial_inventory,
            weekly_demand=weekly_demand,
            normal_supply=normal_supply,
            disruption_supply=disruption_supply,
            disruption_probability=disruption_probability,
            disruption_duration=disruption_duration,
            holding_cost=holding_cost,
            shortage_cost=shortage_cost,
            random_seed=random_seed
        )

    st.session_state["results"] = results
    st.session_state["parameters"] = {
        "weeks": weeks,
        "simulations": simulations,
        "initial_inventory": initial_inventory,
        "weekly_demand": weekly_demand,
        "normal_supply": normal_supply,
        "disruption_supply": disruption_supply,
        "disruption_probability": disruption_probability,
        "disruption_duration": disruption_duration,
        "holding_cost": holding_cost,
        "shortage_cost": shortage_cost
    }


# ============================================================
# CHECK WHETHER SIMULATION HAS BEEN RUN
# ============================================================

if "results" not in st.session_state:

    st.info(
        "👈 Adjust the parameters in the sidebar and "
        "click **Run Simulation** to begin."
    )

    st.stop()


# ============================================================
# LOAD RESULTS
# ============================================================

results = st.session_state["results"]

params = st.session_state["parameters"]

total_costs = results["total_costs"]
total_shortages = results["total_shortages"]

minimum_inventories = (
    results["minimum_inventories"]
)

stockout_occurs = (
    results["stockout_occurs"]
)

final_inventories = (
    results["final_inventories"]
)

number_of_disruptions = (
    results["number_of_disruptions"]
)

total_holding_costs = (
    results["total_holding_costs"]
)

total_shortage_costs = (
    results["total_shortage_costs"]
)

weekly_inventory = (
    results["weekly_inventory"]
)

weekly_supply = (
    results["weekly_supply"]
)

weekly_shortage = (
    results["weekly_shortage"]
)

weekly_stockout = (
    results["weekly_stockout"]
)

weekly_disruption = (
    results["weekly_disruption"]
)


# ============================================================
# CALCULATE STATISTICS
# ============================================================

expected_cost = np.mean(
    total_costs
)

expected_shortage = np.mean(
    total_shortages
)

probability_stockout = np.mean(
    stockout_occurs
)

average_min_inventory = np.mean(
    minimum_inventories
)

average_final_inventory = np.mean(
    final_inventories
)

expected_holding_cost = np.mean(
    total_holding_costs
)

expected_shortage_cost = np.mean(
    total_shortage_costs
)

average_disruptions = np.mean(
    number_of_disruptions
)


# ============================================================
# SECTION 1 — INPUT SUMMARY
# ============================================================

st.header("📋 Simulation Scenario")

input_col1, input_col2, input_col3, input_col4 = st.columns(4)

with input_col1:

    st.metric(
        "Initial Inventory",
        f"{params['initial_inventory']:,}"
    )

with input_col2:

    st.metric(
        "Weekly Demand",
        f"{params['weekly_demand']:,}"
    )

with input_col3:

    st.metric(
        "Normal Supply",
        f"{params['normal_supply']:,}"
    )

with input_col4:

    st.metric(
        "Disruption Supply",
        f"{params['disruption_supply']:,}"
    )


# ============================================================
# SECTION 2 — KEY PERFORMANCE INDICATORS
# ============================================================

st.header("📊 Key Simulation Results")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Expected Total Cost",
        f"${expected_cost:,.2f}"
    )

with col2:

    st.metric(
        "Expected Shortage",
        f"{expected_shortage:,.2f}"
    )

with col3:

    st.metric(
        "Stockout Probability",
        f"{probability_stockout * 100:.2f}%"
    )

with col4:

    st.metric(
        "Average Minimum Inventory",
        f"{average_min_inventory:,.2f}"
    )


col5, col6, col7, col8 = st.columns(4)

with col5:

    st.metric(
        "Average Final Inventory",
        f"{average_final_inventory:,.2f}"
    )

with col6:

    st.metric(
        "Expected Holding Cost",
        f"${expected_holding_cost:,.2f}"
    )

with col7:

    st.metric(
        "Expected Shortage Cost",
        f"${expected_shortage_cost:,.2f}"
    )

with col8:

    st.metric(
        "Average Disruptions",
        f"{average_disruptions:.2f}"
    )


# ============================================================
# SECTION 3 — SAMPLE SIMULATION
# ============================================================

st.header("🔎 One Possible Supply-Chain Scenario")

weeks_axis = np.arange(
    1,
    params["weeks"] + 1
)


# ------------------------------------------------------------
# Inventory
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    weeks_axis,
    results["sample_inventory"],
    marker="o",
    linewidth=2
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5
)

ax.set_xlabel("Week")
ax.set_ylabel("Inventory Units")
ax.set_title(
    "Sample Simulation: Inventory Trajectory"
)

ax.grid(alpha=0.3)

st.pyplot(fig)


# ------------------------------------------------------------
# Supply vs Demand
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    weeks_axis,
    results["sample_supply"],
    marker="o",
    linewidth=2,
    label="Supply"
)

ax.axhline(
    params["weekly_demand"],
    linestyle="--",
    linewidth=2,
    label="Demand"
)

ax.set_xlabel("Week")
ax.set_ylabel("Units")
ax.set_title(
    "Sample Simulation: Supply vs Demand"
)

ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 4 — DISRUPTION VISUALIZATION
# ============================================================

st.header("⚠️ Supplier Disruption Pattern")

fig, ax = plt.subplots(
    figsize=(12, 4)
)

ax.bar(
    weeks_axis,
    results["sample_disruption"]
)

ax.set_xlabel("Week")
ax.set_ylabel("Disruption")
ax.set_title(
    "Supplier Disruptions in Sample Simulation"
)

ax.set_xticks(weeks_axis)

st.pyplot(fig)


# ============================================================
# SECTION 5 — MULTIPLE INVENTORY TRAJECTORIES
# ============================================================

st.header("📈 Inventory Uncertainty")

fig, ax = plt.subplots(
    figsize=(12, 6)
)

number_of_paths = min(
    100,
    params["simulations"]
)

for i in range(number_of_paths):

    ax.plot(
        weeks_axis,
        weekly_inventory[i],
        alpha=0.08
    )

average_inventory = np.mean(
    weekly_inventory,
    axis=0
)

ax.plot(
    weeks_axis,
    average_inventory,
    linewidth=3,
    label="Average Inventory"
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=2,
    label="Stockout Level"
)

ax.set_xlabel("Week")
ax.set_ylabel("Inventory")
ax.set_title(
    "Inventory Trajectories Across Monte Carlo Simulations"
)

ax.set_xticks(weeks_axis)
ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 6 — INVENTORY PERCENTILE BAND
# ============================================================

st.subheader(
    "Inventory Risk Band"
)

inventory_5 = np.percentile(
    weekly_inventory,
    5,
    axis=0
)

inventory_50 = np.percentile(
    weekly_inventory,
    50,
    axis=0
)

inventory_95 = np.percentile(
    weekly_inventory,
    95,
    axis=0
)

fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    weeks_axis,
    inventory_50,
    linewidth=3,
    label="Median"
)

ax.fill_between(
    weeks_axis,
    inventory_5,
    inventory_95,
    alpha=0.25,
    label="5th–95th percentile"
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=2
)

ax.set_xlabel("Week")
ax.set_ylabel("Inventory")
ax.set_title(
    "Inventory Uncertainty Band"
)

ax.set_xticks(weeks_axis)
ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 7 — WEEKLY STOCKOUT PROBABILITY
# ============================================================

st.header("🚨 Weekly Stockout Risk")

weekly_stockout_probability = (
    np.mean(
        weekly_stockout,
        axis=0
    ) * 100
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    weeks_axis,
    weekly_stockout_probability,
    marker="o",
    linewidth=3
)

ax.set_xlabel("Week")
ax.set_ylabel(
    "Stockout Probability (%)"
)

ax.set_title(
    "Probability of Stockout by Week"
)

ax.set_xticks(weeks_axis)
ax.grid(alpha=0.3)

st.pyplot(fig)


# ============================================================
# SECTION 8 — AVERAGE SUPPLY VS DEMAND
# ============================================================

st.header("📦 Average Weekly Supply")

average_weekly_supply = np.mean(
    weekly_supply,
    axis=0
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    weeks_axis,
    average_weekly_supply,
    marker="o",
    linewidth=3,
    label="Average Supply"
)

ax.axhline(
    params["weekly_demand"],
    linestyle="--",
    linewidth=2,
    label="Demand"
)

ax.set_xlabel("Week")
ax.set_ylabel("Units")
ax.set_title(
    "Average Weekly Supply vs Demand"
)

ax.set_xticks(weeks_axis)
ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 9 — WEEKLY SHORTAGE
# ============================================================

st.header("📉 Weekly Shortage")

average_weekly_shortage = np.mean(
    weekly_shortage,
    axis=0
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.bar(
    weeks_axis,
    average_weekly_shortage
)

ax.set_xlabel("Week")
ax.set_ylabel(
    "Average Shortage"
)

ax.set_title(
    "Average Weekly Shortage"
)

ax.set_xticks(weeks_axis)

st.pyplot(fig)


# ============================================================
# SECTION 10 — COST DISTRIBUTION
# ============================================================

st.header("💰 Cost Risk Analysis")

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.hist(
    total_costs,
    bins=50,
    edgecolor="black"
)

ax.axvline(
    expected_cost,
    linestyle="--",
    linewidth=2,
    label=(
        f"Mean = ${expected_cost:,.0f}"
    )
)

ax.set_xlabel("Total Cost ($)")
ax.set_ylabel("Number of Simulations")

ax.set_title(
    "Distribution of Total Supply-Chain Cost"
)

ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 11 — SHORTAGE DISTRIBUTION
# ============================================================

st.header("📉 Shortage Risk Distribution")

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.hist(
    total_shortages,
    bins=50,
    edgecolor="black"
)

ax.axvline(
    expected_shortage,
    linestyle="--",
    linewidth=2,
    label=(
        f"Mean = {expected_shortage:.1f}"
    )
)

ax.set_xlabel("Total Shortage (Units)")
ax.set_ylabel("Number of Simulations")

ax.set_title(
    "Distribution of Total Shortage"
)

ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 12 — MINIMUM INVENTORY DISTRIBUTION
# ============================================================

st.header("📦 Minimum Inventory Distribution")

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.hist(
    minimum_inventories,
    bins=50,
    edgecolor="black"
)

ax.axvline(
    average_min_inventory,
    linestyle="--",
    linewidth=2,
    label=(
        f"Mean = {average_min_inventory:.1f}"
    )
)

ax.set_xlabel("Minimum Inventory")
ax.set_ylabel("Number of Simulations")

ax.set_title(
    "Distribution of Minimum Inventory"
)

ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 13 — FINAL INVENTORY
# ============================================================

st.header("📦 Final Inventory Distribution")

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.hist(
    final_inventories,
    bins=50,
    edgecolor="black"
)

ax.axvline(
    average_final_inventory,
    linestyle="--",
    linewidth=2,
    label=(
        f"Mean = {average_final_inventory:.1f}"
    )
)

ax.set_xlabel("Final Inventory")
ax.set_ylabel("Number of Simulations")

ax.set_title(
    "Distribution of Final Inventory"
)

ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 14 — DISRUPTION FREQUENCY
# ============================================================

st.header("⚠️ Number of Disruptions")

unique, counts = np.unique(
    number_of_disruptions,
    return_counts=True
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    unique,
    counts
)

ax.set_xlabel(
    "Number of Disruption Events"
)

ax.set_ylabel(
    "Number of Simulations"
)

ax.set_title(
    "Distribution of Disruption Events"
)

st.pyplot(fig)


# ============================================================
# SECTION 15 — STOCKOUT VS NO STOCKOUT
# ============================================================

st.header("🚨 Stockout Risk")

stockout_count = np.sum(
    stockout_occurs
)

no_stockout_count = (
    params["simulations"]
    - stockout_count
)

fig, ax = plt.subplots(
    figsize=(8, 5)
)

ax.bar(
    ["No Stockout", "Stockout"],
    [
        no_stockout_count,
        stockout_count
    ]
)

ax.set_ylabel(
    "Number of Simulations"
)

ax.set_title(
    "Stockout vs No-Stockout Outcomes"
)

st.pyplot(fig)


# ============================================================
# SECTION 16 — COST DECOMPOSITION
# ============================================================

st.header("💵 Cost Decomposition")

fig, ax = plt.subplots(
    figsize=(8, 5)
)

ax.bar(
    [
        "Holding Cost",
        "Shortage Cost"
    ],
    [
        expected_holding_cost,
        expected_shortage_cost
    ]
)

ax.set_ylabel(
    "Expected Cost ($)"
)

ax.set_title(
    "Expected Cost Decomposition"
)

st.pyplot(fig)


# ============================================================
# SECTION 17 — BOX PLOT
# ============================================================

st.header("📊 Distribution of Major Outcomes")

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.boxplot(
    [
        total_costs,
        total_shortages,
        minimum_inventories,
        final_inventories
    ],
    tick_labels=[
        "Total Cost",
        "Total Shortage",
        "Min Inventory",
        "Final Inventory"
    ]
)

ax.set_title(
    "Monte Carlo Outcome Distributions"
)

ax.grid(alpha=0.3)

st.pyplot(fig)


# ============================================================
# SECTION 18 — COST CDF
# ============================================================

st.header("📈 Cumulative Cost Probability")

sorted_costs = np.sort(
    total_costs
)

cumulative_probability = (
    np.arange(
        1,
        len(sorted_costs) + 1
    )
    / len(sorted_costs)
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    sorted_costs,
    cumulative_probability * 100,
    linewidth=2
)

median_cost = np.percentile(
    total_costs,
    50
)

p95_cost = np.percentile(
    total_costs,
    95
)

ax.axvline(
    median_cost,
    linestyle="--",
    linewidth=2,
    label="Median"
)

ax.axvline(
    p95_cost,
    linestyle="--",
    linewidth=2,
    label="95th Percentile"
)

ax.set_xlabel(
    "Total Cost ($)"
)

ax.set_ylabel(
    "Cumulative Probability (%)"
)

ax.set_title(
    "Cumulative Distribution of Total Cost"
)

ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 19 — SHORTAGE VS COST
# ============================================================

st.header("🔗 Shortage vs Total Cost")

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.scatter(
    total_shortages,
    total_costs,
    alpha=0.15
)

ax.set_xlabel(
    "Total Shortage (Units)"
)

ax.set_ylabel(
    "Total Cost ($)"
)

ax.set_title(
    "Relationship Between Shortage and Total Cost"
)

ax.grid(alpha=0.3)

st.pyplot(fig)


# ============================================================
# SECTION 20 — MINIMUM INVENTORY VS COST
# ============================================================

st.header("🔗 Minimum Inventory vs Total Cost")

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.scatter(
    minimum_inventories,
    total_costs,
    alpha=0.15
)

ax.set_xlabel(
    "Minimum Inventory"
)

ax.set_ylabel(
    "Total Cost ($)"
)

ax.set_title(
    "Relationship Between Minimum Inventory and Total Cost"
)

ax.grid(alpha=0.3)

st.pyplot(fig)


# ============================================================
# SECTION 21 — WEEKLY DISRUPTION PROBABILITY
# ============================================================

st.header("⚠️ Weekly Disruption Probability")

weekly_disruption_probability = (
    np.mean(
        weekly_disruption,
        axis=0
    ) * 100
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.bar(
    weeks_axis,
    weekly_disruption_probability
)

ax.axhline(
    params["disruption_probability"] * 100,
    linestyle="--",
    linewidth=2,
    label="Input Probability"
)

ax.set_xlabel("Week")
ax.set_ylabel(
    "Disruption Probability (%)"
)

ax.set_title(
    "Observed Weekly Supplier Disruption Probability"
)

ax.set_xticks(weeks_axis)

ax.legend()

st.pyplot(fig)


# ============================================================
# SECTION 22 — WEEKLY INVENTORY BOXPLOT
# ============================================================

st.header("📦 Weekly Inventory Distribution")

fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.boxplot(
    [
        weekly_inventory[:, i]
        for i in range(params["weeks"])
    ],
    tick_labels=[
        f"W{i}"
        for i in weeks_axis
    ]
)

ax.set_xlabel("Week")
ax.set_ylabel("Inventory")

ax.set_title(
    "Weekly Inventory Distribution Across Simulations"
)

ax.grid(alpha=0.3)

st.pyplot(fig)


# ============================================================
# SECTION 23 — CORRELATION ANALYSIS
# ============================================================

st.header("🔗 Correlation Analysis")

correlation_df = pd.DataFrame({

    "Total Cost":
        total_costs,

    "Total Shortage":
        total_shortages,

    "Minimum Inventory":
        minimum_inventories,

    "Final Inventory":
        final_inventories,

    "Disruptions":
        number_of_disruptions,

    "Holding Cost":
        total_holding_costs,

    "Shortage Cost":
        total_shortage_costs
})

correlation_matrix = (
    correlation_df.corr()
)

fig, ax = plt.subplots(
    figsize=(10, 8)
)

im = ax.imshow(
    correlation_matrix,
    interpolation="nearest"
)

plt.colorbar(im)

ax.set_xticks(
    range(
        len(correlation_matrix.columns)
    )
)

ax.set_yticks(
    range(
        len(correlation_matrix.columns)
    )
)

ax.set_xticklabels(
    correlation_matrix.columns,
    rotation=45,
    ha="right"
)

ax.set_yticklabels(
    correlation_matrix.columns
)

ax.set_title(
    "Correlation Between Simulation Outcomes"
)

for i in range(
    len(correlation_matrix.columns)
):

    for j in range(
        len(correlation_matrix.columns)
    ):

        ax.text(
            j,
            i,
            f"{correlation_matrix.iloc[i, j]:.2f}",
            ha="center",
            va="center"
        )

plt.tight_layout()

st.pyplot(fig)


# ============================================================
# SECTION 24 — PERCENTILE TABLE
# ============================================================

st.header("📋 Risk Percentiles")

percentile_table = pd.DataFrame({

    "Percentile": [
        "5th",
        "25th",
        "50th (Median)",
        "75th",
        "95th"
    ],

    "Total Cost ($)": [
        np.percentile(total_costs, 5),
        np.percentile(total_costs, 25),
        np.percentile(total_costs, 50),
        np.percentile(total_costs, 75),
        np.percentile(total_costs, 95)
    ],

    "Total Shortage": [
        np.percentile(total_shortages, 5),
        np.percentile(total_shortages, 25),
        np.percentile(total_shortages, 50),
        np.percentile(total_shortages, 75),
        np.percentile(total_shortages, 95)
    ],

    "Minimum Inventory": [
        np.percentile(minimum_inventories, 5),
        np.percentile(minimum_inventories, 25),
        np.percentile(minimum_inventories, 50),
        np.percentile(minimum_inventories, 75),
        np.percentile(minimum_inventories, 95)
    ]
})

st.dataframe(
    percentile_table.style.format({
        "Total Cost ($)": "${:,.2f}",
        "Total Shortage": "{:,.2f}",
        "Minimum Inventory": "{:,.2f}"
    }),
    use_container_width=True
)


# ============================================================
# SECTION 25 — MANAGERIAL INTERPRETATION
# ============================================================

st.header("🎯 Managerial Interpretation")

st.markdown(
    f"""
### What does the simulation tell us?

- **Expected total cost:** ${expected_cost:,.2f}
- **Expected shortage:** {expected_shortage:,.2f} units
- **Probability of stockout:** {probability_stockout * 100:.2f}%
- **Average minimum inventory:** {average_min_inventory:,.2f} units
- **Expected holding cost:** ${expected_holding_cost:,.2f}
- **Expected shortage cost:** ${expected_shortage_cost:,.2f}

### Supply-chain insight

The simulation demonstrates the trade-off between **inventory cost and disruption risk**.

Increasing initial inventory generally provides greater protection against supplier
disruptions, but it also increases the amount of inventory that may have to be held.

Reducing inventory lowers holding cost, but may increase:

- Stockout probability
- Shortage quantity
- Shortage cost
- Supply-chain service risk

Therefore, the objective is not necessarily to minimize inventory.

> **The managerial objective is to find an appropriate balance between inventory cost and supply-chain resilience.**
"""
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Developed by Prof. Jaydip Sen, Praxis Business School, Kolkata | "
    "Monte Carlo Supply Chain Disruption Simulator"
)

st.caption(
    "© 2026 Jaydip Sen. All rights reserved."
)

st.caption(
    "For academic, educational, and research purposes."
)
