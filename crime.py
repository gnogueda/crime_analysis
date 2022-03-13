'''
Dash application
'''

mapbox_access_token = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

import pandas as pd
import dash
from dash import dcc 
import dash_core_components as dcc
from dash import html
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

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
            'burglary': 'burglary',
            'larcenytheft': 'Larceny theft',
            'motorvehicletheft': 'Motor vehicle theft',
            'arson': 'Arson'})
blackbold={'color':'black', 'font-weight': 'bold'}

#------------------------------------------------------------------------------
# Application layout
app = dash.Dash(__name__)
app.layout = html.Div([

    html.Div([
        html.Div([

            # Crimes checklist
            html.Label(children=['Type of crime: '], style=blackbold),
            dcc.Checklist(id='crimes',
                    options=[{'label':str(b),'value':b} for b in sorted(df['type_crime'].unique())],
                    value=[b for b in sorted(df['type_crime'].unique())],
            ),

            # Year checklist
            html.Label(children=['Year: '], style=blackbold),
            dcc.Checklist(id='year_id',
                    options=[{'label':str(b),'value':b} for b in sorted(df['year'].unique())],
                    value=[b for b in sorted(df['year'].unique())],
            ),


        ], className='three columns'
        ),

        # Map
        html.Div([
            dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                style={'padding-bottom':'2px','padding-left':'2px','height':'100vh'}
            )
        ], className='nine columns'
        ),

    ], className='row'
    ),

], className='ten columns offset-by-one'
)

#------------------------------------------------------------------------------
# Output of Graph
@app.callback(Output('graph', 'figure'),
              [Input('crimes', 'value'),
               Input('year_id', 'value')])

def update_figure(chosen_crime,chosen_year):
    df_sub = df[(df['type_crime'].isin(chosen_crime)) &
                (df['year'].isin(chosen_year))]

    # Create figure
    locations=[go.Scattermapbox(
                    lon = df_sub['lng'],
                    lat = df_sub['lat'],
                    #color = df_sub['number_crimes'],
                    mode='markers',
                    unselected={'marker' : {'opacity':1, 'size':10}},
                    selected={'marker' : {'opacity':0.5, 'size':40}},
                    hovertext=(df_sub['number_crimes'])

    )]

    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Crime in major cities of USA, 2015-2019",font=dict(size=50, color='black')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                style='light',
                center=dict(
                    lat=37,
                    lon=-100
                ),
                pitch=0,
                zoom=3
            ),
        )
    }

#------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
