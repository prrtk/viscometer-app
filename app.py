import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import compute_velocity, find_terminal_velocity, calculate_viscosity

st.set_page_config(page_title="Viscometer Analyzer", layout="centered")

st.title("🧪 Viscometer Terminal Velocity & Viscosity Calculator")
st.markdown(
    "Upload your time-position CSV, enter ball & fluid data, and let physics + code do the rest.")

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload time-position CSV file", type=['csv'])

# Parameter inputs
radius = st.number_input("Radius of ball (in meters)",
                         value=0.01, format="%.4f")
density_sphere = st.number_input("Density of ball (kg/m³)", value=7850)
density_fluid = st.number_input("Density of fluid (kg/m³)", value=1000)
threshold = st.slider(
    "Terminal velocity detection threshold (m/s)", 0.001, 0.1, 0.01, step=0.001)
stable_duration = st.slider(
    "Stable duration for terminal velocity (seconds)", 0.1, 5.0, 0.5, step=0.1)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        time = df['time'].values
        position = df['position'].values

        # Velocity calculation
        velocity = compute_velocity(time, position)

        # Terminal velocity
        Vt, t_terminal = find_terminal_velocity(
            time, velocity, threshold, stable_duration)

        # Viscosity
        viscosity = calculate_viscosity(
            radius, density_sphere, density_fluid, Vt)

        # Plotting
        st.subheader("📈 Position vs Time")
        fig1, ax1 = plt.subplots()
        ax1.plot(time, position, label='Position (m)')
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Position (m)")
        ax1.grid()
        st.pyplot(fig1)

        st.subheader("📈 Velocity vs Time")
        fig2, ax2 = plt.subplots()
        ax2.plot(time, velocity, label='Velocity (m/s)', color='orange')
        ax2.axvline(t_terminal, color='red', linestyle='--',
                    label='Terminal Velocity Detected')
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Velocity (m/s)")
        ax2.legend()
        ax2.grid()
        st.pyplot(fig2)

        # Results
        st.success("✅ Results:")
        st.write(
            f"**Terminal Velocity:** {Vt:.4f} m/s (at {t_terminal:.2f} s)")
        st.write(f"**Viscosity of fluid:** {viscosity:.4e} Pa·s")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
