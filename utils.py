import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def compute_velocity(time, position, smooth=True, window=11, poly=3):
    if smooth and len(position) > window:
        position = savgol_filter(position, window_length=window, polyorder=poly)
    velocity = np.gradient(position, time)
    return velocity

def find_terminal_velocity(time, velocity, threshold=0.01, stable_duration=0.5):
    N = len(time)
    for i in range(N):
        end_idx = np.searchsorted(time, time[i] + stable_duration)
        if end_idx >= N:
            break
        segment = velocity[i:end_idx]
        if np.max(segment) - np.min(segment) < threshold:
            return np.mean(segment), time[i]
    return velocity[-1], time[-1]

def calculate_viscosity(radius, density_sphere, density_fluid, terminal_velocity, g=9.81):
    eta = (2 * radius**2 * g * (density_sphere - density_fluid)) / (9 * terminal_velocity)
    return eta
