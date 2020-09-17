# ------------------------------------------------------------------------------
# import dependencies

import os
import pathlib
import re
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import json as j
import cufflinks as cf

# ------------------------------------------------------------------------------
# setup meta

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server


external_stylesheets = [
    'assets/opioid.css'
]

px.set_mapbox_access_token('pk.eyJ1Ijoia2xvdWJyaWVsIiwiYSI6ImNrY3k4ZTNtOTA3Z2MzM3F5dnFqOTczbG4ifQ.IbBDl_jWuZt66vPcX59bxg')

# ------------------------------------------------------------------------------
# enter text here



descript = "This dashboard is created to help the campaign visually understand trends within Pennsylvania Senate District 39 with the hope that this will enable targeted campaign efforts, which might translate to votes."

slider_descript = "Drag the slider to change the year:"

# ------------------------------------------------------------------------------
# load data

df = pd.read_csv('master_df_geotag.csv')
df.GEOID = df.GEOID.astype(float, copy=False)
df = df.dropna()
df.GEOID = df.GEOID.astype(int)
df.GEOID = df.GEOID.astype(str)


# offices = [
#         {'label': 'PA Senate Candidate', 'value': 'PA Senate Candidate'},
#         {'label': 'POTUS Candidate', 'value': 'POTUS Candidate'},
#         {'label': 'US Senate Candidate', 'value': 'US Senate Candidate'}
# ],

pa_senate_options = {
    2008: ['Tony Bompiani', 'Kim Ward'],
    2012: ['Ronald M Gazze', 'Kim L Ward'],
    2016: ['Kim Ward', 'James R Brewster', 'Tony DeLoreto']
}

potus_options = {
    2008: ['Barack Obama', 'John McCain', 'Bob Barr', 'Ralph Nader'],
    2012: ['Mitt Romney','Barack Obama', 'Gary Johnson', 'Jill Stein'],
    2016: ['Donald J Trump', 'Hillary Clinton', 'Darrell L Castle', 'Jill Stein', 'Gary Johnson']
}

us_senate_options = {
    2008: ['none'],
    2012: ['Tom Smith', 'Bob Casey Jr', 'Rayburn Douglas Smith'],
    2016: ['Katie McGinty', 'Pat Toomey', 'Edward T Clifford III']
}

metrics = ['Eligible Voters', 'PA Senate District Prop', 'PA Senate Office Prop', 'PA Senate Office Votes', 'PA Senate Precinct Prop', 'PA Senate Precinct Votes', 'POTUS District Prop', 'POTUS Office Prop', 'POTUS Office Votes', 'POTUS Precinct Prop', 'POTUS Precinct Votes', 'Precinct', 'Total Turnout', 'US Senate District Prop', 'US Senate Office Prop','US Senate Office Votes', 'US Senate Precinct Prop','US Senate Precinct Votes']
other_metrics = ['Eligible Voters', 'Total Turnout']

path = 'converted_.geojson'
file = open(path)
json_file = j.load(file)

# YEARS = df['Election Year'].unique()
YEARS = [2008, 2012, 2016]

def get_candidates(df, year, office='POTUS Candidate'):

    """
    modular function to return candidates for a given year and office. should be useful in the dropdown functionality.
    """

    candidates = df[office].loc[df['Election Year'] == year].unique()

    return candidates


# probably need to put somewhere in the callback area; keeping here for now to avoid confusion and remind
candidates = get_candidates(df, 2012, 'US Senate Candidate')

# ------------------------------------------------------------------------------
# app layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("bbdlogo.png")),
                html.H4(children="Logistics Dashboard: Tay Waltenbaugh Campaign"),
                html.P(
                    id="description",
                    children=descript,
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    step=None,
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                dcc.Dropdown(id='office-selector',
                                             options = [
                                                     {'label': 'PA Senate Candidate', 'value': 'PA Senate Candidate'},
                                                     {'label': 'POTUS Candidate', 'value': 'POTUS Candidate'},
                                                     {'label': 'US Senate Candidate', 'value': 'US Senate Candidate'}
                                             ],
                                             multi=False,
                                             value= "PA Senate Candidate",
                                             style={'width':"50%"}),
                                html.Br(),
                                dcc.Dropdown(id='candidates', multi=False, value=2016,style={'width':"50%"}),
                                html.P(
                                    "Heatmap of metrics within Senate District 39".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure={}
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        dcc.Graph(
                            id="top-values",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                        html.Br(),
                        dcc.Graph(
                            id="bottom-values",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# dropdown for position
# dropdown for person within the position

# ------------------------------------------------------------------------------
# connect plotly graphs wtih dash components

# @app.callback(
#     # Output('candidates', 'options'),
#     Input('years-slider', 'value')
# )
# # def filter_year(year):
# #     df_ = df.loc[df['Election Year'] == int(year)]
# #     return df_

@app.callback(
    Output('candidates', 'options'),
    [Input('years-slider', 'value'),
     Input('office-selector', 'value')]
)
def filter_office(year, office):
    if office == "PA Senate Candidate":
        return [{'label': i, 'value': i} for i in pa_senate_options[year]]
    elif office == "POTUS Candidate":
        return [{'label': i, 'value': i} for i in potus_options[year]]
    elif office == "US Senate Candidate":
        return [{'label': i, 'value': i} for i in us_senate_options[year]]
    return []

# @app.callback(
#     Output('potus_candidates', 'value'),
#     [Input('df')]
# )
# def filter_candidates(options):
#     df_ = df.loc[df[office] == candidate]
#     return df_

# @app.callback(
#     Output(component_id='county-choropleth', component_property='figure'),
#     [Input]
# )
# def ratio(df, col_x, col_y):
#     return df['ToPlot'] = df[col_x]/df[col_y]


@app.callback(
    Output(component_id='county-choropleth', component_property='figure'),
    # [Output(component_id='county-choropleth', component_property='figure'),
    # Output(component_id='top-values', component_property='figure'),
    # Output(component_id='bottom-values', component_property='figure')
    # ],
    [Input(component_id='years-slider', component_property='value'),
     Input(component_id='office-selector', component_property='value'),
     Input(component_id='candidates', component_property='value')
    ]
)
def update_graph(year, office, candidate):

    dff = df.copy()
    dff = dff[dff["Election Year"] == year]
    dff = dff.loc[dff[office] == candidate]
    #dff = dff[dff[columns].str.contains('Precinct Proportions', regex=False)]
    #dff = dff.sort_values([value], ascending=False)

    # fig1 = px.choropleth_mapbox(dff, geojson=json_file,
    #                        locations='GEOID', color="Total Turnout",
    #                        color_continuous_scale="blues",
    #                        range_color=(0, 100),
    #                        featureidkey="properties.GEOID",
    #                        mapbox_style="carto-positron",
    #                        zoom=8.5, center = {"lat": 40.2650, "lon": -79.4129},
    #                        labels={'Precinct':'Loc'},
    #                        title="Proportion of total votes for " + str(candidate) + " in the " + str(year) + " " + str(office) + " election.",
    #                        opacity=0.5)

    # if chart
    # data =


    if office == "PA Senate Candidate":
        data = "PA Senate Precinct Prop"
    elif office == "POTUS Candidate":
        data = "POTUS Precinct Prop"
    elif office == "US Senate Candidate":
        data = "US Senate Precinct Prop"

    fig = px.choropleth_mapbox(dff, geojson=json_file,
                           locations='GEOID',
                           color= data, #dff.columns.str.contains('Precinct Proportions', regex=False),
                           color_continuous_scale="reds",
                           #range_color=(40, 80),
                           featureidkey = 'properties.GEOID',
                           mapbox_style="carto-positron",
                           zoom=9, center = {"lat": 40.2650, "lon": -79.4129},
                           opacity=0.5,
                           hover_data = ['Precinct', 'Total Votes'], title = "Proportion of total votes for " + str(candidate) + " in the " + str(year) + " " + str(office) + " election.")


    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, title={'text': "Republican Obama Voters"})

    fig2 = px.bar(dff, x="Precinct", y=data)

    fig3 = px.bar(dff, x="Precinct", y=data)

    return fig #, fig2, fig3
    
# def ratio(df, col_x, col_y):
# return df['ToPlot'] = df[col_x]/df[col_y]

#def match_words(office, ):
    #office = office.split




# ------------------------------------------------------------------------------
# run the server

if __name__ == '__main__':
    app.run_server(debug=True)
