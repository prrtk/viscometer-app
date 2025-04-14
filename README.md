# Advanced Viscometer Analyzer

This application analyzes falling ball viscometer data to calculate fluid viscosity using both Stokes' Law and empirical drag coefficient methods, depending on the flow regime.

## 🧪 Features

- Automatic detection of terminal velocity from time-position data
- Support for both high-viscosity fluids (Stokes' Law) and low-viscosity fluids (empirical drag coefficient)
- Reynolds number calculation to determine appropriate calculation method
- Interactive plots for position and velocity vs. time
- Detailed analysis of flow regime and viscosity calculation

## 📊 Scientific Background

The app implements two main calculation methods:

1. **Stokes' Law Method**:

   - Valid for low Reynolds numbers (Re < 1)
   - Used for high-viscosity fluids
   - Formula: η = (2r²g(ρₛ-ρₗ))/(9v)

2. **Empirical Drag Coefficient Method**:
   - Used for higher Reynolds numbers (Re > 1)
   - Accounts for transitional and turbulent flow
   - Uses iterative solution based on force balance

## 🚀 How to Use

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`
3. Upload a CSV file with `time` and `position` columns
4. Enter physical parameters (ball radius, densities)
5. View results and analysis

## 📁 Sample Data Format

Your CSV file should have at least these columns:

- `time`: Time in seconds
- `position`: Position in meters (or centimeters, which will be auto-converted)

## 📝 Citation

This work is based on experimental findings from a lab report on falling ball viscometry, which demonstrated the limitations of Stokes' Law for low-viscosity fluids and high Reynolds numbers.
