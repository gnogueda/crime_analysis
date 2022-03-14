'''
Dash application
'''
mapbox_access_token = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

#------------------------------------------------------------------------------
# Import and clean data
df = pd.read_csv("crime_data.csv")
df = df[df.large_city == 1]
df = df.melt(id_vars =['state', 'city', 'population', 'year', 'state_city', 
                       'lat', 'lng', 'population_sm', 'density', 'large_city']) 
df = df.rename(columns = {"variable": "type_crime", "value": "number_crimes"})
df = df.replace({'violentcrime': 'Violent crime',
            'murderandnonnegligentmanslaug': 'Murder and nonnegligent manslaughter', 
            'rape': 'Rape',
            'robbery': 'Robbery',
            'aggravatedassault': 'Aggravated assault', 
            'propertycrime': 'Property crime',
            'burglary': 'Burglary',
            'larcenytheft': 'Larceny theft',
            'motorvehicletheft': 'Motor vehicle theft',
            'arson': 'Arson'})
df['year'] = df['year'].astype(str)
blackbold={'color':'black', 'font-weight': 'bold'}

#------------------------------------------------------------------------------
# Application layout
app = Dash(__name__)
app.layout = html.Div(
    children=[

    html.H1("Crime in the major cities of USA, 2015-2019", style={'text-align': 'center'}),
   
    dcc.Dropdown(id='crime_dropdown',
                 options=[{'label':str(b),'value':b} for b in sorted(df['type_crime'].unique())],
                 multi=False,
                 value=['Violent crime'],
                 style={'width': "50%"}),

    dcc.Dropdown(id='year_dropdown',
                  options=[{'label':str(b),'value':b} for b in sorted(df['year'].unique())],
                  multi=False,
                  value=['2015'],
                  style={'width': "40%"}),
    
    html.Div([dcc.Graph(id="graph_output", figure={}, 
        style={'padding-bottom':'2px','padding-left':'2px','height':'90vh'})])

])

#------------------------------------------------------------------------------
# Display map

@app.callback(
    Output("graph_output", "figure"),
    [Input("crime_dropdown", "value"), 
     Input("year_dropdown", "value")]
)

def update_figure(selected_crime, selected_year):
    
    print(f"Value user chose crime: {selected_crime}")
    print(f"Value user chose year: {selected_year}")
    
    df_filtered = df.loc[df["type_crime"].isin(selected_crime) & df["year"].isin(selected_year)]

    fig = px.scatter_mapbox(df_filtered,
                            lat = "lat",
                            lon = "lng",
                            color = 'number_crimes',
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max = 40,
                            zoom = 10,
                            hover_name = 'city',
                            size = 'population',
                            hover_data = ['population'])
    
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=37,
                lon=-100
            ),
            pitch=0,
            zoom=3
        )
    )
 
    return fig
#------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
