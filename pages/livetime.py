import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

dash.register_page(__name__)

layout = html.Div([
    html.H1('Donation Link'),
    dcc.Link('Go to Home', href='/'),
    # Add the rest of your Page 1 components here
])

# Add the callbacks for your Page 1 here
