import os
import fastf1
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from dash import html
from collections import defaultdict
from fastf1 import get_event_schedule
from datetime import datetime


# Get working directory
cwd = os.getcwd()

#Set cache using relative path
cache_dir = os.path.join(cwd, 'Cache')

# Set the cache directory
fastf1.Cache.enable_cache(cache_dir)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=False)

# Calculate the current year
current_year = datetime.now().year

# Define the layout
app.layout = html.Div([
    html.H1('Historical F1 Telemetry Dashboard'),
    html.Div(
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in range(2018, current_year + 1)],
            value=current_year,  # Set the default value to the current year
            style={'width': '100%'}
        ),
        style={'width': '25%', 'margin': '0 auto'}
    ),
    html.Div(
        dcc.Dropdown(
            id='gp-dropdown',
            options=[
                {'label': 'Bahrain', 'value': 'bahrain'},
                {'label': 'Monaco', 'value': 'monaco'},
                {'label': 'Silverstone', 'value': 'silverstone'},
                {'label': 'Spa', 'value': 'spa'},
                # Add more GPs here
            ],
            value='bahrain',
            style={'width': '100%'}
        ),
        style={'width': '25%', 'margin': '0 auto'}
    ),
    html.Div(
        dcc.Dropdown(
            id='session-dropdown',
            options=[
                {'label': 'FP1', 'value': 'FP1'},
                {'label': 'FP2', 'value': 'FP2'},
                {'label': 'FP3', 'value': 'FP3'},
                {'label': 'Q', 'value': 'Q'},
                {'label': 'R', 'value': 'R'}
            ],
            value='R',
            style={'width': '100%'}
        ),
        style={'width': '25%', 'margin': '0 auto'}
    ),
    html.Div(
        dcc.Dropdown(
            id='driver1-dropdown',
            options=[
                {'label': 'Verstappen', 'value': 'VER'},
                {'label': 'Hamilton', 'value': 'HAM'},
                # Add more
            ],
            value='VER',
            style={'width': '100%'}
        ),
        style={'width': '25%', 'margin': '0 auto'}
    ),
    html.Div(
        dcc.Dropdown(
            id='driver2-dropdown',
            options=[
                {'label': 'Verstappen', 'value': 'VER'},
                {'label': 'Hamilton', 'value': 'HAM'},
            ],
            value='HAM',
            style={'width': '100%'}
        ),
        style={'width': '25%', 'margin': '0 auto'}
    ),
    html.Div(
        dcc.Slider(
            id='lap-slider',
            min=1,
            max=10,
            step=1,
            value=1,
            marks={i: f"Lap {i}" for i in range(1, 10)}, 
        ),
        style={'width': '50%', 'margin': '10px auto 0 auto'} 
    ),
    #  New div to display the currently selected lap
    html.Div(id='current-lap-display', style={'margin-top': '20px', 'fontSize': '20px'}),

    dcc.Graph(id='lap-graph'),

],
style={
    'display': 'flex',
    'flex-direction': 'column',
    'align-items': 'center',
    'justify-content': 'center'
})

# Define a color mapping dictionary, will update this to dynamic color mappin in next commit
driver_colors = {
    'HAM': 'teal',  # Mercedes
    'BOT': 'teal',  # Mercedes
    'VER': 'blue',  # Red Bull Racing
    'PER': 'blue',  # Red Bull Racing
    'NOR': 'orange',  # McLaren
    'RIC': 'orange',  # McLaren
    'DEV': 'orange', # McLaren
    'LEC': 'red',  # Ferrari
    'SAI': 'red',  # Ferrari
    'GAS': 'silver',  # AlphaTauri
    'TSU': 'silver',  # AlphaTauri
    'ALO': 'navy',  # Alpine
    'OCO': 'navy',  # Alpine
    'STR': 'green',  # Aston Martin
    'VET': 'green',  # Aston Martin
    'RUS': 'cyan',  # Williams
    'LAT': 'cyan',  # Williams
    'ALB': 'cyan',  # Williams
    'SAR': 'cyan',  # Williams
    'RAI': 'pink',  # Alfa Romeo
    'ZHO': 'pink',  # Alfa Romeo
    'GIO': 'pink',  # Alfa Romeo
    'SCH': 'magenta',  # Haas
    'MAZ': 'magenta',  # Haas
    # Add more
}


# Updated session dropdown callback
@app.callback(
    Output('session-dropdown', 'options'),
    [Input('year-dropdown', 'value'),
     Input('gp-dropdown', 'value')]
)
def update_session_dropdown(year, round_number):
    if year is None or round_number is None:
        # If there is no year or a GP is not selected, this will return an empty options list
        return []
    
    try:
        year = int(year)
        round_number = int(round_number)
        session_data = fastf1.get_session(year, round_number, 'R')
        session_data.load()
        sessions = ['FP1', 'FP2', 'FP3', 'Q', 'R']
        session_options = [{'label': session, 'value': session} for session in sessions]
        return session_options
    except ValueError:
        print(f"Error converting inputs to int: year={year}, round_number={round_number}")
        return []
    except Exception as e:
        print(f"Error loading session data: {e}")
        return []


# Updated Lap Slider callback with error handling
@app.callback(
    [Output('lap-slider', 'max'),
     Output('lap-slider', 'value'),
     Output('lap-slider', 'marks')],
    [Input('year-dropdown', 'value'),
     Input('gp-dropdown', 'value'),
     Input('session-dropdown', 'value')]
)
def update_lap_slider(year, round_number, session):
    default_max = 1
    default_marks = {1: "Lap 1"}

    if not (year and round_number and session):
        print("Missing input from dropdowns.")
        return default_max, 1, default_marks

    try:
        year = int(year)
        round_number = int(round_number)
        session_data = fastf1.get_session(year, round_number, session)
        session_data.load()
        max_laps = int(session_data.laps['LapNumber'].max())
        # Update the marks dictionary to show every 5th lap and the last lap, can label last lap as 'Final Lap' or 'Lap {max_laps}'
        marks = {1: 'Lap 1', max_laps: f'{max_laps}'}
        marks.update({i: f"{i}" for i in range(2, max_laps) if i % 5 == 0 or i == max_laps})

    except Exception as e:  # Broad exception handling to catch any errors
        print(f"Failed to update lap slider: {e}")
        return default_max, 1, default_marks

    return max_laps, 1, marks

# Lap Slider Counter callback - NEW! -
@app.callback(
    Output('current-lap-display', 'children'),
    [Input('lap-slider', 'value')]
)
def update_current_lap_display(selected_lap):
    return f"Currently Selected: Lap {selected_lap}"

# Updated callback for dynamic GP dictionary for dropdown
@app.callback(
    Output('gp-dropdown', 'options'),
    [Input('year-dropdown', 'value')]
)
def update_gp_dropdown_options(selected_year):
    year = int(selected_year)  # Ensure year is an integer
    schedule = fastf1.get_event_schedule(year=year, include_testing=False)

    # Use 'EventName' or 'OfficialEventName' for dropdown labels and 'RoundNumber' for values
    options = [
        {'label': event['EventName'], 'value': event['RoundNumber']}
        for _, event in schedule.iterrows()
    ]

    return options


#Updated Driver dropdown callback with error handling
@app.callback(
    [Output('driver1-dropdown', 'options'),
     Output('driver2-dropdown', 'options')],
    [Input('year-dropdown', 'value'),
     Input('gp-dropdown', 'value'),
     Input('session-dropdown', 'value')]
)
def update_driver_dropdown(year, round_number, session):
    # If there are no drivers or a driver is not selected, will return an empty options list
    empty_options = []

    try:
        year = int(year)
    except ValueError as e:
        print(f"Error converting year to int: {e}")
        return empty_options, empty_options

    # Attempt to convert round_number to int, handling both integers and potential string inputs
    try:
        round_number = int(round_number)
    except ValueError as e:
        print(f"Error converting round_number to int: {e}")
        return empty_options, empty_options

    # Load session data using fastf1
    try:
        session_data = fastf1.get_session(year, round_number, session)
        session_data.load()  # Load the session data
    except Exception as e:
        print(f"Error loading session data: {e}")
        return empty_options, empty_options

    # Extracting and setting driver options
    try:
        if 'Driver' in session_data.laps.columns:
            drivers = session_data.laps['Driver'].unique()
            driver_options = [{'label': driver, 'value': driver} for driver in drivers]
        else:
            print("Driver column not found in laps data.")
            return empty_options, empty_options
    except Exception as e:
        print(f"Error processing laps data: {e}")
        return empty_options, empty_options

    return driver_options, driver_options



# Plotly graph callback
@app.callback(Output('lap-graph', 'figure'),
              [Input('year-dropdown', 'value'),
               Input('gp-dropdown', 'value'),
               Input('session-dropdown', 'value'),
               Input('driver1-dropdown', 'value'),
               Input('driver2-dropdown', 'value'),
               Input('lap-slider', 'value')])
def update_graph(year, gp, session, driver1, driver2, lap_number):
    try:
        year = int(year)
        session_data = fastf1.get_session(year, gp, session)
        session_data.load()  # load the session data with updated fastf1 3.0.7
        laps = session_data.laps  # access laps directly
    

        print(f"Year: {year}, GP: {gp}, Session: {session}, Driver1: {driver1}, Driver2: {driver2}, LapNumber: {lap_number}")

        #Update callback function to get colors using driver codes - Will update next - 
        driver1_color = driver_colors.get(driver1, 'red')  # default to red if not found in the dictionary
        driver2_color = driver_colors.get(driver2, 'blue')  # default to blue if not found in the dictionary

        lap1 = laps.loc[(laps['Driver'] == driver1) & (laps['LapNumber'] == lap_number)].iloc[0]
        lap2 = laps.loc[(laps['Driver'] == driver2) & (laps['LapNumber'] == lap_number)].iloc[0]

        delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(lap1, lap2)

        print(f"ref_tel: {ref_tel.head()}")
        print(f"compare_tel: {compare_tel.head()}")

        fig = make_subplots(
            rows=7, cols=1,
            #subplot_titles=("Delta Time (s)", "Speed (km/h)", "Throttle", "Brake", "Gear", "RPM", "DRS"),
            vertical_spacing=0.03,
            row_heights=[0.5, 1.5, 1, 0.5, 0.5, 1, 0.5]
        )

      # Set the y-axis titles for each subplot
        subplot_titles = ["Delta Time (s)", "Speed (km/h)", "Throttle", "Brake", "Gear", "RPM", "DRS"]
        for i, title in enumerate(subplot_titles, start=1):
            fig.update_yaxes(title_text=title, row=i, col=1)


        # Delta Time
        fig.add_trace(go.Scatter(x=delta_time.index, y=delta_time, mode='lines', name='Delta Time', line=dict(color='green')), row=1, col=1)

        # Speed
        fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel['Speed'], mode='lines', name=f'{driver1} Speed', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=True), row=2, col=1)
        fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel['Speed'], mode='lines', name=f'{driver2} Speed', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=True), row=2, col=1)


        # Throttle
        fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel['Throttle'], mode='lines', name=f'{driver1} Throttle', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel['Throttle'], mode='lines', name=f'{driver2} Throttle', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=False), row=3, col=1)

        # Brake
        fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel['Brake'], mode='lines', name=f'{driver1} Brake', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel['Brake'], mode='lines', name=f'{driver2} Brake', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=False), row=4, col=1)

        # Gear
        gear_column = 'nGear'
        if gear_column in ref_tel.columns and gear_column in compare_tel.columns:
            fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel[gear_column], mode='lines', name=f'{driver1} Gear', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=False), row=5, col=1)
            fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel[gear_column], mode='lines', name=f'{driver2} Gear', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=False), row=5, col=1)
        else:
            print("Gear data not available")

        # RPM
        rpm_column = 'Rpm' if 'Rpm' in ref_tel.columns and 'Rpm' in compare_tel.columns else 'RPM' if 'RPM' in ref_tel.columns and 'RPM' in compare_tel.columns else None
        if rpm_column:
            fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel[rpm_column], mode='lines', name=f'{driver1} RPM', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=False), row=6, col=1)
            fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel[rpm_column], mode='lines', name=f'{driver2} RPM', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=False), row=6, col=1)
        else:
         print("RPM data not available")

        # DRS
        drs_column = 'Drs' if 'Drs' in ref_tel.columns and 'Drs' in compare_tel.columns else 'DRS' if 'DRS' in ref_tel.columns and 'DRS' in compare_tel.columns else None
        if drs_column:
            fig.add_trace(go.Scatter(x=ref_tel['Distance'], y=ref_tel[drs_column], mode='lines', name=f'{driver1} DRS', line=dict(color=driver1_color), legendgroup='Driver1', showlegend=False), row=7, col=1)
            fig.add_trace(go.Scatter(x=compare_tel['Distance'], y=compare_tel[drs_column], mode='lines', name=f'{driver2} DRS', line=dict(color=driver2_color), legendgroup='Driver2', showlegend=False), row=7, col=1)
        else:
            print("DRS data not available")

        fig.update_layout(
            height=1500, # Adjust the height
            width=1500, # Adjust the width
        )
        
        

        return fig
    except Exception as e:
        print(e)
        return go.Figure()






if __name__ == '__main__':
    app.run_server(debug=True)

