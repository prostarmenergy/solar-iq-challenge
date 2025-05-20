import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import webbrowser

# App Config
st.set_page_config(page_title="Solar IQ Challenge", page_icon="☀️", layout="centered")

# Shared Styles
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        .main {background-color: #f9f9f9;}
        h1, h2 {color: #FF9B21; font-family: 'Poppins', sans-serif;}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🔆 Navigate")
page = st.sidebar.radio("Go to", ["Round 1: Solar Basics", "Round 2: Impact Estimator"])

# Session state for score and navigation
if "round1_passed" not in st.session_state:
    st.session_state.round1_passed = False
if "go_to_round2" not in st.session_state:
    st.session_state.go_to_round2 = False

# ROUND 1
if page == "Round 1: Solar Basics":
    st.title("🌞 Round 1: Know Your Solar Basics")
    st.write("Test your knowledge of solar energy fundamentals.")

    score = 0

    q1 = st.radio("1️⃣ Which device converts sunlight into electricity?",
                  ["Diesel Generator", "Battery", "Solar Panel", "Inverter"],
                  index=None)
    if q1 == "Solar Panel":
        score += 25

    q2 = st.radio("2️⃣ What is a key advantage of hybrid solar inverters?",
                  ["They only work at night", "They combine solar and grid power", "They store diesel", "They are used in cars"],
                  index=None)
    if q2 == "They combine solar and grid power":
        score += 25

    q3 = st.radio("3️⃣ Which type of energy is renewable?",
                  ["Diesel", "Petrol", "Coal", "Solar"],
                  index=None)
    if q3 == "Solar":
        score += 25

    q4 = st.radio("4️⃣ What’s the typical life of a solar panel in years?",
                  ["2", "5", "25", "50"],
                  index=None)
    if q4 == "25":
        score += 25

    if st.button("✅ Submit Round 1"):
        st.success(f"🏆 You scored {score}/100!")
        if score == 100:
            st.balloons()
            st.session_state.round1_passed = True
        elif score >= 50:
            st.info("Good! You have a solid foundation in solar.")
            st.session_state.round1_passed = True
        else:
            st.warning("Keep learning — solar is the future!")
            st.session_state.round1_passed = False

    if st.session_state.round1_passed:
        if st.button("➡️ Proceed to Round 2"):
            st.session_state.go_to_round2 = True
            st.rerun()

# ROUND 2
if page == "Round 2: Impact Estimator" or st.session_state.go_to_round2:
    st.title("⚡ Round 2: Your Energy Impact")
    st.write("Simulate the solar, grid, and battery energy flow through your day.")

    st.markdown("**🔧 Input your solar setup & daily profile:**")
    battery_capacity = st.slider("Battery Capacity (kWh)", 1, 20, 5)
    load_demand = st.slider("Daily Load Demand (kWh)", 1, 50, 20)
    solar_capacity = st.slider("Installed Solar (kW)", 1, 20, 5)

    hours = np.arange(0, 24)
    sunlight_hours = np.logical_and(hours >= 6, hours <= 18)
    solar_generation = np.where(sunlight_hours, solar_capacity * np.sin((np.pi / 12) * (hours - 6)), 0)
    load_profile = np.where((hours >= 6) & (hours < 22), load_demand / 16, load_demand / 8)

    battery_state = []
    battery_level = 0
    battery_use = []
    grid_use = []
    export_to_grid = []

    for s_gen, l_use in zip(solar_generation, load_profile):
        surplus = s_gen - l_use
        if surplus >= 0:
            charge = min(surplus, battery_capacity - battery_level)
            battery_level += charge
            export = surplus - charge
            battery_use.append(0)
            grid_use.append(0)
            export_to_grid.append(export)
        else:
            needed = abs(surplus)
            discharge = min(needed, battery_level)
            battery_level -= discharge
            battery_use.append(discharge)
            grid_use.append(needed - discharge)
            export_to_grid.append(0)
        battery_state.append(battery_level)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.stackplot(hours, load_profile, solar_generation, battery_use, grid_use, export_to_grid,
                 labels=["Load Demand", "Solar Generation", "Battery Discharge", "Grid Usage", "Export to Grid"],
                 colors=["#444", "#f9a825", "#43a047", "#1976d2", "#c0f52f"])
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Power (kW)")
    ax.set_title("Solar - Grid - Battery (Hybrid) Energy Flow")
    ax.legend(loc="upper right")
    st.pyplot(fig)

    # Quiz element based on graph
    st.markdown("### 🤔 Bonus Question")
    guess_export = st.slider("Based on your setup, how much power (kW) do you think was exported to the grid at peak solar hour (12 PM)?", 0.0, float(solar_capacity), 0.0, step=0.1)
    actual_export = round(export_to_grid[12], 2)
    if st.button("🎯 Submit Guess"):
        if abs(guess_export - actual_export) <= 0.5:
            st.success(f"🎉 Spot on! Actual export at 12 PM was {actual_export} kW.")
        else:
            st.error(f"❌ Close, but not quite. Actual export at 12 PM was {actual_export} kW.")

    # Always show Learn More CTA
    st.markdown("""
    ---
    ✅ Want to understand how hybrid solar works in real life?
    [👉 Click here to explore ProstarM Solar Hybrid Inverters](https://prostarm.com/product-range/hybrid-solar-inverter/)
    """)
