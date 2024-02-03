# F1-Dash
Historical F1 Telemetry Data for F1

This is a Python web application using Dash, Plotly, Pandas, and Fast-F1, a library for retrieving Formula 1 data. The dashboard visualizes telemetry data from historical Formula 1 races, allowing users to compare the performance of two drivers for a specific lap during a session. The data is presented using interactive graphs, which are updated based on user inputs.

# Features

- **Select race year, Grand Prix, session (FP1, FP2, FP3, Q, or R), and drivers to compare**:
- **Lap Comparison**: View lap telemetry data for the selected drivers, including:
        Delta Time
        Speed (km/h)
        Throttle
        Brake
        Gear
        RPM
        DRS
- **Interactive Lap Slider**: Navigate through lap data with an interactive slider that dynamically updates visualizations.
- **Caching Mechanism**: Speeds up data retrieval by caching fetched telemetry data locally.

# Dependencies

    Python 3.7+
    Dash
    Fast-F1
    Plotly
    Pandas

# Caching
    
    Caching should almost alwasy be enabled to speed up the runtime and prevent exceeding the rate limit of api servers.
    
    Set the cache directory:

    fastf1.Cache.enable_cache(r'***path//to//cache//directory***')
    
    Please see: https://theoehrly.github.io/Fast-F1/fastf1.html#caching  for additional information.

# Installation

    Install Python 3.7 or higher if not already installed
    Clone this repository
    Install the required dependencies using the following command:
    
    pip install -r requirements.txt

# Usage

    Run the app.py file in the command line:
    
    python app.py

    Open a web browser and navigate to http://127.0.0.1:8050/
    Use the dropdown menus to select race year, Grand Prix, session, and drivers
    Use the lap slider to select the lap number
    Analyze and compare the telemetry data presented in the graphs
    
# Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss new features, bug fixes, or improvements.

# License

This project is licensed under the MIT License.
