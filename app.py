import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
server = app.server
app.config.suppress_callback_exceptions = True

from pages import home, livetime

livetime.register_callbacks(app) # Added to use data_fetch function in livetime.py 

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/livetime':
        return livetime.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=True)
