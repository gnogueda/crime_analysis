'''
Dash application
'''

# This token could be in another file and call it 
mapbox_access_token = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

# This should be in the virtual environment
import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.offline as py 
import plotly.graph_objs as go
import plotly.express as px

df = pd.read_csv("crime_data.csv")
app = dash.Dash(__name__)
px.set_mapbox_access_token(mapbox_access_token)

# Create map
fig = px.scatter_mapbox(df, 
                        lat="lat", 
                        lon="lon", 
                        color_continuous_scale=px.colors.cyclical.IceFire, 
                        size_max=15, 
                        zoom=10,
                        hover_name='city',
                        hover_data=['population', 'Rape1'])

fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=37,
            lon=-100
        ),
        pitch=0,
        zoom=3
    )
)

# Layout of the application
app.layout = html.Div(children=[
    html.H1(children='Crime in the major cities of USA, 2019'),

    html.Div(children='This dashboard shows the prevalence of crimes...'),
    html.Div([dcc.Graph(figure=fig, 
                        style={'padding-bottom':'2px','padding-left':'2px','height':'90vh'})
              ])
    ])

if __name__ == '__main__':
    app.run_server(debug=False)