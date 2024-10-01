# backend/f1dashboard_api/api/utils.py

import fastf1
from fastf1 import utils as f1utils
import pandas as pd
import os

def initialize_fastf1_cache():
    """
    Initialize the FastF1 cache directory.
    """
    # Set cache directory relative to the project root or another appropriate location
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fastf1_cache')

    # Ensure the cache directory exists
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    fastf1.Cache.enable_cache(cache_dir)

def fetch_telemetry_data(year, grand_prix_id, session_type, drivers, lap):
    """
    Fetches telemetry data for the given parameters using FastF1.

    Args:
        year (int): The year of the event.
        grand_prix_id (int): The round number of the Grand Prix.
        session_type (str): The session type ('FP1', 'FP2', 'FP3', 'Q', 'R').
        drivers (list): List of driver codes.
        lap (int): The lap number.

    Returns:
        list: A list of telemetry data dictionaries for the specified drivers and lap.

    Raises:
        ValueError: If any of the parameters are invalid.
        Exception: For any other errors during data fetching.
    """
    try:
        # Convert parameters to appropriate types
        lap = int(lap)
        year = int(year)
        grand_prix_id = int(grand_prix_id)

        # Load the session with telemetry data
        session = fastf1.get_session(year, grand_prix_id, session_type)
        session.load(telemetry=True)  # Ensure telemetry data is loaded

        # Check if the session uses cached data
        if session.use_cache:
            print("Using cached telemetry data")
        else:
            print("Fetching telemetry data from source")

        data = []

        # Load all telemetry data at once
        all_telemetry = session.laps.get_telemetry()

        # Filter laps for the given drivers and the specific lap
        for driver_code in drivers:
            driver_laps = session.laps.pick_driver(driver_code)
            lap_data = driver_laps[driver_laps['LapNumber'] == lap]

            # Check if data exists for the driver and lap
            if lap_data.empty:
                raise ValueError(f"Lap {lap} not available for driver {driver_code}.")

            # Filter telemetry data for the specific lap and driver
            telemetry = all_telemetry[all_telemetry['LapNumber'] == lap]
            telemetry = telemetry[telemetry['DriverNumber'] == driver_code]

            # Ensure that 'Distance' column is present
            if 'Distance' not in telemetry.columns:
                telemetry = telemetry.add_distance()

            # Select relevant columns
            telemetry = telemetry[['Distance', 'Speed', 'Throttle', 'Brake', 'nGear', 'RPM', 'DRS']]

            # Add driver and lap information to the telemetry data
            telemetry['Driver'] = driver_code
            telemetry['Lap'] = lap

            # Convert DataFrame to list of dictionaries
            telemetry_records = telemetry.to_dict('records')
            data.extend(telemetry_records)

        return data

    except ValueError as ve:
        # Handle specific value errors, such as invalid lap numbers
        raise ValueError(f"Invalid input: {ve}")
    except fastf1.FastF1Error as f1e:
        # Handle FastF1 specific errors
        raise f1e
    except Exception as e:
        # Generic error handling
        raise Exception(f"Unexpected error occurred: {e}")
