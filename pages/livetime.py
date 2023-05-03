import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pages.data_fetcher import start_live_timing_data_saving, stop_live_timing_data_saving

dash.register_page(__name__)

layout = html.Div([
    html.H1('F1 - Live Timing Dash'),
    dcc.Link('Go to Home', href='/'),
    html.Div([
        dbc.Button('Start Live Timing Data Saving', id='start-button', color='success', className='mr-1'),
        dbc.Button('Stop Live Timing Data Saving', id='stop-button', color='danger', className='mr-1'),
    ], style={'margin-top': '20px'}),
    html.Div(id='output')
])

# Add the callbacks for your Page 1 here
def register_callbacks(app):
    global _process

    @app.callback(
        Output('output', 'children'),
        Input('start-button', 'n_clicks'),
        Input('stop-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_output(start_clicks, stop_clicks):
        global _process
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'start-button':
            _process = start_live_timing_data_saving()
            return f"Started live timing data saving at click {start_clicks}"
        elif triggered_id == 'stop-button':
            if _process is not None:
                stop_live_timing_data_saving(_process)
                _process = None
                return f"Stopped live timing data saving at click {stop_clicks}"
            else:
                return "No live timing data saving process to stop."
