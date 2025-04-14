import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import (compute_velocity, find_terminal_velocity, calculate_viscosity,
                   calculate_reynolds_number, determine_best_method)

st.set_page_config(page_title="Advanced Viscometer Analyzer", layout="wide")

st.title("🧪 Advanced Viscometer Terminal Velocity & Viscosity Calculator")
st.markdown("""
This application implements both Stokes' Law and empirical drag coefficient methods for 
calculating viscosity from falling ball experiments.

**Features:**
- Auto-detects appropriate calculation method based on Reynolds number
- Supports both high-viscosity fluids (Stokes' Law) and low-viscosity fluids (empirical drag)
- Provides detailed insights about flow regime and calculation method
""")

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload time-position CSV file", type=['csv'])

# Parameters column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ball Properties")
    radius = st.number_input(
        "Radius of ball (in meters)", value=0.01, format="%.5f")
    density_sphere = st.number_input("Density of ball (kg/m³)", value=7850.0)

with col2:
    st.subheader("Fluid Properties")
    density_fluid = st.number_input("Density of fluid (kg/m³)", value=1000.0)
    fluid_name = st.text_input(
        "Fluid Name (e.g., 'Water', 'Silicon Solution')", value="Water")

# Advanced settings in an expander
with st.expander("Advanced Settings"):
    col1, col2 = st.columns(2)

    with col1:
        velocity_detection_method = st.selectbox(
            "Terminal Velocity Detection Method",
            ["auto", "average_last"],
            index=0,
            help="'auto' detects stable regions, 'average_last' uses the last 30% of data"
        )

        threshold = st.slider(
            "Terminal velocity stability threshold (m/s)",
            0.001, 0.1, 0.01, step=0.001,
            help="Maximum allowed variation in velocity to be considered stable"
        )

        stable_duration = st.slider(
            "Stable duration for terminal velocity (seconds)",
            0.1, 5.0, 0.5, step=0.1,
            help="Duration velocity must remain stable to be considered terminal"
        )

    with col2:
        calculation_method = st.selectbox(
            "Viscosity Calculation Method",
            ["auto", "stokes", "empirical"],
            index=0,
            help="'auto' chooses based on Reynolds number, 'stokes' uses only Stokes' Law, 'empirical' uses drag coefficient"
        )

        g = st.number_input(
            "Gravitational Acceleration (m/s²)",
            value=9.81,
            format="%.2f"
        )

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Basic validation
        required_columns = ['time', 'position']
        if not all(col in df.columns for col in required_columns):
            st.error(
                f"CSV must contain columns: {', '.join(required_columns)}")
        else:
            time = df['time'].values
            position = df['position'].values

            # Convert position to meters if needed (check for unit conversion)
            if np.max(position) > 100:  # Position likely in cm
                position = position / 100  # Convert cm to m
                st.info(
                    "Position values appear to be in cm - converted to meters for calculations.")

            # Velocity calculation
            velocity = compute_velocity(time, position)

            # Terminal velocity
            Vt, t_terminal = find_terminal_velocity(
                time, velocity, method=velocity_detection_method,
                threshold=threshold, stable_duration=stable_duration
            )

            # Initial viscosity estimate
            initial_viscosity = 0.001  # Pa·s (water)

            # Determine calculation method if auto
            if calculation_method == "auto":
                calculation_method = determine_best_method(
                    radius, density_fluid, Vt, initial_viscosity)

            # Calculate viscosity
            viscosity = calculate_viscosity(
                radius, density_sphere, density_fluid, Vt, g=g, method=calculation_method
            )

            # Calculate Reynolds number
            reynolds = calculate_reynolds_number(
                Vt, 2*radius, density_fluid, viscosity)

            # Display results in multiple columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Position vs Time")
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                ax1.plot(time, position, label='Position (m)')
                ax1.set_xlabel("Time (s)")
                ax1.set_ylabel("Position (m)")
                ax1.grid(True)
                st.pyplot(fig1)

            with col2:
                st.subheader("📈 Velocity vs Time")
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                ax2.plot(time, velocity, label='Velocity (m/s)', color='orange')
                ax2.axhline(y=Vt, color='red', linestyle='--',
                            label=f'Terminal Velocity: {Vt:.4f} m/s')
                ax2.axvline(x=t_terminal, color='green', linestyle='--',
                            label=f'Detection at: {t_terminal:.2f} s')
                ax2.set_xlabel("Time (s)")
                ax2.set_ylabel("Velocity (m/s)")
                ax2.legend()
                ax2.grid(True)
                st.pyplot(fig2)

            # Results
            st.success("✅ Analysis Results:")

            # Results in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Terminal Velocity", f"{Vt:.4f} m/s")
                st.metric("Detection Time", f"{t_terminal:.2f} s")

            with col2:
                st.metric("Reynolds Number", f"{reynolds:.2f}")
                flow_regime = "Laminar (Stokes' Law valid)" if reynolds < 1 else "Transitional/Turbulent"
                st.metric("Flow Regime", flow_regime)

            with col3:
                st.metric("Viscosity", f"{viscosity:.4e} Pa·s")
                st.metric("Viscosity (Poise)", f"{viscosity*10:.4f} Poise")

            # Additional details in an expander
            with st.expander("Detailed Analysis"):
                st.markdown(f"""
                ### Flow Characteristics:
                - **Reynolds Number**: {reynolds:.2f}
                - **Flow Regime**: {flow_regime}
                - **Calculation Method Used**: {"Stokes' Law" if calculation_method == "stokes" else "Empirical Drag Coefficient"}
                
                ### According to your lab report:
                - For **high Reynolds numbers** (Re > 1), Stokes' Law becomes invalid and overestimates viscosity
                - For **silicon solutions** with higher viscosity, Stokes' Law provides accurate results
                - For **water** or low-viscosity fluids, the empirical drag coefficient method is more appropriate
                
                ### Viscosity in Various Units:
                - **SI Units (Pa·s)**: {viscosity:.6f} Pa·s
                - **CGS Units (Poise)**: {viscosity*10:.6f} Poise
                - **Centipoise**: {viscosity*1000:.6f} cP
                """)

                # Comparison with known viscosities
                st.markdown("""
                ### Comparison with Standard Values:
                | Fluid | Standard Viscosity (Pa·s) | Standard Viscosity (cP) |
                |-------|--------------------------|------------------------|
                | Water (20°C) | 0.001 | 1.0 |
                | Silicon Solution (Lab Report) | ~1.8-2.1 | ~1800-2100 |
                """)

    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        st.exception(e)
