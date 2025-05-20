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

# Disclaimer
st.markdown("""
<div style='font-size: 0.9em; color: gray;'>
<b>Disclaimer:</b> This application is intended for educational and experimentation purposes only. The results presented are based on estimations and may not reflect actual electricity bills or solar performance.
</div>
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
    st.write("Simulate the solar, grid, and export energy flows through a typical Indian day.")

    st.markdown("**🏠 Choose Consumer Type:**")
    user_type = st.radio("Tariff Category", ["Residential", "Commercial"], horizontal=True)

    st.markdown("**🔧 Input your solar setup & daily profile:**")
    load_units = st.slider("Estimated Daily Load (Units)", 5, 50, 15)
    solar_capacity = st.slider("Installed Solar PV Capacity (kW)", 1, 20, 5)

    hours = np.arange(0, 24)

    # Load profile (Indian trend)
    load_profile = np.array([
        0.8, 0.6, 0.4, 0.4, 0.6, 1.2, 2.0, 2.0, 1.5, 1.2, 1.2, 1.0,
        0.8, 0.8, 1.0, 1.2, 2.2, 2.5, 2.0, 1.6, 1.4, 1.0, 0.8, 0.6
    ])
    load_profile = (load_profile / load_profile.sum()) * load_units

    # Solar generation (bell curve between 6am–6pm)
    solar_generation = np.where(
        (hours >= 6) & (hours <= 18),
        solar_capacity * np.clip(np.sin((np.pi / 12) * (hours - 6)), 0, 1),
        0
    )

    # Energy flows
    export_to_grid = np.maximum(solar_generation - load_profile, 0)
    grid_use = np.maximum(load_profile - solar_generation, 0)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(hours, load_profile, label="Load Demand (Units)", color="#444", linewidth=2)
    ax.plot(hours, solar_generation, label="Solar Generation (Units)", color="#f9a825", linewidth=2)
    ax.fill_between(hours, 0, export_to_grid, label="Export to Grid", color="#c0f52f", alpha=0.4)
    ax.fill_between(hours, 0, grid_use, label="Grid Usage", color="#1976d2", alpha=0.3)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Units")
    ax.set_title("Energy Profile: Load vs. Solar vs. Grid")
    ax.legend(loc="upper right")
    st.pyplot(fig)

    # Estimated cost calculation
    def calculate_cost(units, category):
        if category == "Residential":
            if units <= 100:
                return units * 3.5
            elif units <= 300:
                return 100 * 3.5 + (units - 100) * 5.5
            else:
                return 100 * 3.5 + 200 * 5.5 + (units - 300) * 7.5
        else:
            return units * 9.0

    daily_grid_units = grid_use.sum()
    daily_cost = calculate_cost(daily_grid_units, user_type)
    st.metric("Estimated Daily Grid Consumption", f"{daily_grid_units:.2f} Units")
    st.metric("Estimated Daily Cost (₹)", f"₹{daily_cost:.2f}")

    # Quiz element based on export
    st.markdown("### 🤔 Bonus Question")
    guess_export = st.slider("How much power (Units) was exported at 12 PM?", 0.0, float(solar_capacity), 0.0, step=0.1)
    actual_export = round(export_to_grid[12], 2)
    if st.button("🎯 Submit Guess"):
        if abs(guess_export - actual_export) <= 0.5:
            st.success(f"🎉 Spot on! Export at 12 PM was {actual_export} Units.")
        else:
            st.error(f"❌ Not quite. Export at 12 PM was {actual_export} Units.")

    # Always show Learn More CTA
    st.markdown("""
    ---
    ✅ Want to understand how hybrid solar works in real life?
    [👉 Click here to explore ProstarM Solar Hybrid Inverters](https://prostarm.com/product-range/hybrid-solar-inverter/)
    """)
