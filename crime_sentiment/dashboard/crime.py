'''
Dash application
'''

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import os.path as path
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZ25vZ3VlZGEiLCJhIjoiY2wwa2Q4ZW1xMGZyaTNlbmVnMDJydHRvcCJ9.d17UBC8JGh_xhi29OHym0w'

#path.abspath(path.join(__file__ ,"../../.."))
#------------------------------------------------------------------------------
def go_crime():
    # Import and clean data
    drr = path.abspath(path.join(__file__ ,"../.."))
    df = pd.read_csv(drr + "/data/fbi_twitter_merge/crime_data.csv")
    df = df[df.large_city == 1]
    crime_cols = ['violentcrime',
        'murderandnonnegligentmanslaug', 'rape', 'robbery', 'aggravatedassault',
        'propertycrime', 'burglary', 'larcenytheft', 'motorvehicletheft',
        'arson']
    df['All crimes'] = df[crime_cols].sum(axis=1)
    df = df.melt(id_vars =['state', 'city', 'population', 'year', 'state_city',
                        'lat', 'lng', 'population_sm', 'density', 'large_city'])
    df = df.rename(columns = {"variable": "type_crime", "value": "number_crimes"})
    df = df.replace({'violentcrime': 'Violent crime',
                'murderandnonnegligentmanslaug': 'Murder',
                'rape': 'Rape',
                'robbery': 'Robbery',
                'aggravatedassault': 'Aggravated assault',
                'propertycrime': 'Property crime',
                'burglary': 'Burglary',
                'larcenytheft': 'Larceny theft',
                'motorvehicletheft': 'Motor vehicle theft',
                'arson': 'Arson'})

    df['year'] = df['year'].astype(str)
    df['crimes_display'] = 100000 * df['number_crimes'] / df['population']
    df = df.sort_values(['year', 'number_crimes'])

    title={'color':'black', 
        'font-weight': 'bold', 
        'font-family':'Arial', 
        'font-size': '250%',
        'text-align': 'center'}

    #------------------------------------------------------------------------------
    # Application layout

    app = Dash(
        __name__,
        external_stylesheets=[
            "https://codepen.io/chriddyp/pen/bWLwgP.css"
        ]
    )

    app.layout = html.Div([

        # Header
        html.Div(
            children=[
                html.H1("Crime in the 10 major cities of USA, 2005-2019",
                        style=title),
                html.P('''This dashboard shows the prevalence of crime in the 10 major cities of
                    USA from 2005 to 2019. It also shows an index that reflects upon a sentiment
                    analysis from twitter during this period.''',
                    style={'font-size': '120%', 'font-family':'Arial'})]

        ),

        # Dropdowns
        html.Div([
            html.Div([
                dcc.Dropdown(id='crime_dropdown',
                    options=[{'label':str(b),'value':b} for b in sorted(df['type_crime'].unique())],
                    placeholder="Select a type of crime/Twitter index",
                    multi=False,
                    value='All crimes')

                ], className="three columns"),

            html.Div([
                dcc.Dropdown(id='year_dropdown',
                    options=[{'label':str(b),'value':b} for b in sorted(df['year'].unique())],
                    placeholder="Select a year",
                    multi=False,
                    value='2019')

                ], className="three columns"),

            html.Div([
                dcc.Dropdown(id='crimes_unit',
                    options=[{'label':'Number of crimes','value':'number'}, 
                            {'label':'Crimes per 100,000 habitants','value':'100k'}],
                    placeholder="Select a crime unit",
                    multi=False,
                    value='100k')

                ], className="three columns"),

            html.Div([
                dcc.Dropdown(id='selected_cities',
                    options=[{'label':'10 major cities','value':'top10'}, 
                            {'label':'All cities','value':'all'}],
                    placeholder="Select cities",
                    multi=False,
                    value='top10')

                ], className="three columns"),


        ], className="row"),

        # Graphs
        html.Div([
            html.Div([
                dcc.Graph(id="graph_output", 
                        figure={},
                        style={'height':'90vh'})
            ], className="eight columns"),
            html.Div([dcc.Graph(id="graph_types_output", 
                                figure={}, style={'height':'45vh', 'color': 'black'})], 
                    className="four columns"),
            html.Div([dcc.Graph(id="graph_time_output", 
                                figure={}, style={'height':'45vh'})], 
                    className="four columns"),



        ], className="row")

    ])


    #------------------------------------------------------------------------------
    # Display and update map according to selected year and type of crime

    @app.callback(
        Output("graph_output", "figure"),
        [Input("crime_dropdown", "value"),
        Input("year_dropdown", "value"),
        Input("crimes_unit", "value"),
        Input("selected_cities", "value")
        ]
    )

    def update_map(selected_crime, selected_year, crime_unit, selected_cities):

        print(f"Value user chose crime: {selected_crime}")
        print(f"Value user chose year: {selected_year}")
        print(f"Value user chose crime: {crime_unit}")
        print(f"Value user chose crime: {selected_cities}")

        df_map = df.copy()
        df_map = df_map.loc[df_map["type_crime"].isin([selected_crime]) &
                            df_map["year"].isin([selected_year])
                            ]

        if crime_unit == 'number':
            df_map['crimes_display'] = df_map['number_crimes']
        if selected_cities == 'top10':
            df_map = df_map[df_map.large_city == 1]

        fig = px.scatter_mapbox(df_map,
                                lat = "lat",
                                lon = "lng",
                                color = df_map['crimes_display'],
                                labels={"crimes_display": "Number of crimes/<br>Twitter index"},
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                size_max = 70,
                                zoom = 15,
                                hover_name = 'city',
                                size = 'population',
                                hover_data = ['year', 'city', 'population'],
                                title = "<b>Map of crimes<b>"
                                )

        fig.update_layout(
            title_font_color = "#06184d",
            font_family='Arial',
            hovermode='closest',
            mapbox=dict(
                accesstoken=MAPBOX_ACCESS_TOKEN,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=39,
                    lon=-98
                ),
                pitch=0,
                zoom=3.2
            )
        )
        return fig



    @app.callback(
        Output("graph_types_output", "figure"),
        Output("graph_time_output", "figure"),
        [Input("graph_output", "hoverData"),
        Input("graph_output", "clickData"),
        Input("graph_output", "selectedData"),
        Input("crime_dropdown", "value")
        ]
    )

    def update_figure(hover_data, click_data, select_data, selected_crime):
        print(f'hover data: {hover_data}')

        hover_year = hover_data['points'][0]['customdata'][0]
        hover_city = hover_data['points'][0]['customdata'][1]

        # Types of crime figure
        df_type_crime = df.copy()
        df_type_crime = df_type_crime.loc[df_type_crime["year"].isin([hover_year]) &
                            df_type_crime["city"].isin([hover_city])]
        df_type_crime = df_type_crime.loc[df_type_crime["type_crime"] != "All crimes"]

        for c in df_type_crime.city.unique():
            display_c = c
            
        fig_crime_types = px.bar(df_type_crime,
                                x='crimes_display', 
                                y='type_crime', 
                                orientation='h',
                                hover_name="year",
                                title= f'<b>Crime by type and year in {display_c}<b>')

        # Time series figure
        df_time = df.copy()
        df_time = df_time.loc[df_time["type_crime"].isin([selected_crime]) &
                            df_time["city"].isin([hover_city])]

        fig_time = px.line(df_time, 
                        x='year', 
                        y='crimes_display',
                        markers=True)
        
        fig_crime_types.update_layout(
            title_font_color = "#06184d",
            yaxis_title=None,
            xaxis_title=None,
            font_family='Arial',
            margin=dict(l=120, b=1),
            template='none')
        
        fig_time.update_layout(
            yaxis_title=None,
            xaxis_title=None,
            font_family='Arial',
            showlegend=False,
            template='none')
        
        fig_crime_types.update_traces(marker_color='#46434d')
        fig_time.update_traces(line_color='#46434d')
        
        return [fig_crime_types, fig_time]

    app.run_server(host = "127.0.0.1", port =8051, debug=False)
    #app.run_server(debug=False)
    #------------------------------------------------------------------------------
    #if __name__ == '__main__':
     #   app.run_server(host = "127.0.0.1", port =888, debug=False)
