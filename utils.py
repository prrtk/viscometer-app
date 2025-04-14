import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def compute_velocity(time, position, smooth=True, window=11, poly=3):
    if smooth and len(position) > window:
        position = savgol_filter(
            position, window_length=window, polyorder=poly)
    velocity = np.gradient(position, time)
    return velocity


def find_terminal_velocity(time, velocity, method="auto", threshold=0.01, stable_duration=0.5):
    """
    Find terminal velocity using either automatic detection or averaging the last N points
    """
    if method == "auto":
        N = len(time)
        for i in range(N):
            end_idx = np.searchsorted(time, time[i] + stable_duration)
            if end_idx >= N:
                break
            segment = velocity[i:end_idx]
            if np.max(segment) - np.min(segment) < threshold:
                return np.mean(segment), time[i]
        return velocity[-1], time[-1]

    elif method == "average_last":
        # Use the last 30% of data points to calculate terminal velocity
        n = len(velocity)
        start_idx = int(n * 0.7)  # Start from 70% of the way through
        return np.mean(velocity[start_idx:]), time[start_idx]


def calculate_reynolds_number(velocity, diameter, density_fluid, viscosity):
    """Calculate Reynolds number"""
    return (density_fluid * velocity * diameter) / viscosity


def calculate_drag_coefficient(reynolds):
    """
    Calculate drag coefficient based on Reynolds number
    Using the empirical relation from the lab report
    """
    if reynolds < 1:
        # Stokes' Law region
        return 24.0 / reynolds
    elif reynolds < 1000:
        # Transitional region
        return 24.0 / reynolds * (1 + 0.15 * reynolds**0.687)
    else:
        # Turbulent region
        return 0.44


def calculate_viscosity(radius, density_sphere, density_fluid, terminal_velocity, g=9.81, method="stokes"):
    """
    Calculate viscosity using either Stokes' Law or the empirical drag coefficient method
    """
    diameter = 2 * radius

    if method == "stokes":
        # Standard Stokes' Law formula
        eta = (2 * radius**2 * g * (density_sphere - density_fluid)) / \
            (9 * terminal_velocity)
        return eta

    elif method == "empirical":
        # Iterative solution using drag coefficient
        # Start with a guess for viscosity (water viscosity at 20°C)
        viscosity_guess = 0.001  # Pa·s

        # Newton-Raphson method to solve for viscosity
        max_iterations = 50
        tolerance = 1e-8

        for i in range(max_iterations):
            # Calculate Reynolds number with current viscosity guess
            re = calculate_reynolds_number(
                terminal_velocity, diameter, density_fluid, viscosity_guess)

            # Calculate drag coefficient
            cd = calculate_drag_coefficient(re)

            # Calculate the force balance equation
            volume = (4/3) * np.pi * radius**3
            mass = density_sphere * volume
            buoyancy = density_fluid * volume * g
            weight = mass * g
            drag_force = 0.5 * cd * density_fluid * terminal_velocity**2 * np.pi * radius**2

            # Force balance: weight - buoyancy - drag = 0
            # Calculate the residual
            residual = weight - buoyancy - drag_force

            # If the residual is small enough, we've found our answer
            if abs(residual) < tolerance:
                break

            # Calculate derivative of residual with respect to viscosity
            # This is complex due to the relationship between Cd and Re
            # Use a numerical approximation
            delta = viscosity_guess * 1e-6
            viscosity_plus = viscosity_guess + delta

            re_plus = calculate_reynolds_number(
                terminal_velocity, diameter, density_fluid, viscosity_plus)
            cd_plus = calculate_drag_coefficient(re_plus)
            drag_force_plus = 0.5 * cd_plus * density_fluid * \
                terminal_velocity**2 * np.pi * radius**2
            residual_plus = weight - buoyancy - drag_force_plus

            derivative = (residual_plus - residual) / delta

            # Update viscosity using Newton-Raphson step
            if abs(derivative) > 1e-10:  # Avoid division by very small numbers
                viscosity_guess -= residual / derivative

                # Ensure viscosity remains positive
                if viscosity_guess <= 0:
                    viscosity_guess = 0.001  # Reset to initial guess
            else:
                # If derivative is too small, use a damped approach
                viscosity_guess *= 0.95

        return viscosity_guess


def determine_best_method(radius, density_fluid, terminal_velocity, viscosity_guess=0.001):
    """
    Determine whether to use Stokes' Law or the empirical method
    based on estimated Reynolds number
    """
    diameter = 2 * radius
    reynolds = calculate_reynolds_number(
        terminal_velocity, diameter, density_fluid, viscosity_guess)

    if reynolds < 1:
        return "stokes"
    else:
        return "empirical"
