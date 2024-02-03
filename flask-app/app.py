import os
import fastf1
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from flask_caching import Cache
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from dash import html
from collections import defaultdict

# Get working directory
cwd = os.getcwd()

#Set cache using relative path
cache_dir = os.path.join(cwd, 'Cache')

# Set the cache directory
fastf1.Cache.enable_cache(cache_dir)

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN]) #Change theme "darkmode"

cache = Cache(app.server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': cache_dir})


server = app.server

#GP Dictionary
gp_data = {
    2019: [
        'australia', 'bahrain', 'china', 'azerbaijan', 'spain',
        'monaco', 'canada', 'france', 'austria', 'britain',
        'germany', 'hungary', 'belgium', 'italy', 'singapore',
        'russia', 'japan', 'mexico', 'usa', 'brazil', 'abu_dhabi'
    ],
    2020: [
        'austria', 'austria_2', 'hungary', 'britain', 'britain_2',
        'spain', 'belgium', 'italy', 'italy_2', 'russia',
        'germany', 'portugal', 'italy_3', 'turkey', 'bahrain',
        'bahrain_2', 'abu_dhabi'
    ],
    2021: [
        'bahrain', 'italy', 'portugal', 'spain', 'monaco',
        'azerbaijan', 'france', 'austria', 'austria_2', 'britain',
        'hungary', 'belgium', 'netherlands', 'italy_2', 'russia',
        'turkey', 'usa', 'mexico', 'brazil', 'qatar', 'saudi_arabia', 'abu_dhabi'
    ],
    2022: [
        'bahrain', 'saudi_arabia', 'australia', 'italy', 'miami',
        'spain', 'monaco', 'azerbaijan', 'canada', 'britain',
        'austria', 'france', 'hungary', 'belgium', 'netherlands',
        'italy_2', 'russia', 'singapore', 'japan', 'usa',
        'mexico', 'brazil', 'abu_dhabi'
    ],
    2023: [
        'bahrain', 'saudi_arabia', 'australia'
    ]
}




# Define the layout
app.layout = html.Div([
    html.H1('Historical F1 Telemetry Dashboard'),
    html.Div(
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in range(2019, 2024)],  # Add more years if needed
            value='2023', #set default drop down
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
                # Add more drivers here
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
            max=10,  # Will be updated by the callback
            step=1,
            value=1,
            marks={i: f"Lap {i}" for i in range(1, 10)},  # Will be updated by the callback
        ),
        style={'width': '50%', 'margin': '10px auto 0 auto'}  # Added 10px top margin
    ),
    dcc.Graph(id='lap-graph'),
],
style={
    'display': 'flex',
    'flex-direction': 'column',
    'align-items': 'center',
    'justify-content': 'center'
})

# Define a color mapping dictionary
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
    # Add more drivers here
}




# Define a new callback function (slider)
@app.callback(
    [Output('lap-slider', 'max'),
     Output('lap-slider', 'value'),
     Output('lap-slider', 'marks')],
    [Input('year-dropdown', 'value'),
     Input('gp-dropdown', 'value'),
     Input('session-dropdown', 'value')])
@cache.memoize(timeout=180)  # Cache for 3 minutes
def update_lap_slider(year, gp, session):
    year = int(year)  # Convert year to int
    session_data = fastf1.get_session(year, gp, session)
    session_data.load()  # new way to load the session data in fastf1 3.0.7
    laps_data = session_data.laps  # Access laps directly

    # Get the maximum lap number
    max_laps = int(laps_data['LapNumber'].max())  # Convert max_laps to int

    # Set initial slider value and create marks
    value = 1
    marks = {i: f" {i}" for i in range(1, max_laps + 1)}

    return max_laps, value, marks


# Callback to GP dictionary for dropdown
@cache.memoize(timeout=180)  # Cache for 3 minutes
@app.callback(
    Output('gp-dropdown', 'options'),
    [Input('year-dropdown', 'value')]
)
def update_gp_dropdown(year):
    year = int(year)
    return [{'label': gp.capitalize(), 'value': gp.lower()} for gp in gp_data[year]]

# Callback to update driver dropdown
@cache.memoize(timeout=180)  # Cache for 3 minutes
@app.callback(
    [Output('driver1-dropdown', 'options'),
     Output('driver2-dropdown', 'options')],
    [Input('year-dropdown', 'value'),
     Input('gp-dropdown', 'value'),
     Input('session-dropdown', 'value')])
def update_driver_dropdown(year, gp, session):
    year = int(year)
    session_data = fastf1.get_session(year, gp, session)
    session_data.load()  # updated line to match the new version of fastf1 3.0.7
    laps_data = session_data.laps  # changed line
    drivers = laps_data['Driver'].unique()
    driver_options = [{'label': driver, 'value': driver} for driver in drivers]
    return driver_options, driver_options


# Define the callback
@cache.memoize(timeout=180)  # Cache for 3 minutes
@app.callback(Output('lap-graph', 'figure'),
              [Input('year-dropdown', 'value'),
               Input('gp-dropdown', 'value'),
               Input('session-dropdown', 'value'),
               Input('driver1-dropdown', 'value'),
               Input('driver2-dropdown', 'value'),
               Input('lap-slider', 'value')])  # Add lap-slider as an input
def update_graph(year, gp, session, driver1, driver2, lap_number):
    try:
        year = int(year)  # Convert year to int
        session_data = fastf1.get_session(year, gp, session)
        session_data.load()  # load the session data with updated fastf1 3.0.7
        laps = session_data.laps  # aqccess laps directly

        print(f"Year: {year}, GP: {gp}, Session: {session}, Driver1: {driver1}, Driver2: {driver2}, LapNumber: {lap_number}")

        #Update callback function to get colors using driver codes
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
    # app.run_server(debug=True)
    app.run(threaded=True, host='0.0.0.0', port=int(os.getenv('APP_PORT')))
