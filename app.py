import dash
import base64
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
#import plotly.graph_objects as go
import pandas as pd
#import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import random
#import dash_daq as daq
from datetime import datetime
from plotly.subplots import make_subplots
import datetime
import requests

# Load data
df = pd.read_csv('data/stockdata2.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])

# Load data
cc = pd.read_csv('data/cumulative_cases.csv', skiprows=3)
cd = pd.read_csv('data/cumulative_deaths.csv', skiprows=3)
rc = pd.read_csv('data/sevenday_rolling_average_of_new_cases.csv', skiprows=3)
rd = pd.read_csv('data/sevenday_rolling_average_of_new_deaths.csv', skiprows=3)

stateDictionary = {}

dataVal = [cc, cd, rc, rd]

aTime = 67

random_xPie = [100, 2000, 550]
namesPie = ['A', 'B', 'C']

figPie = px.pie(values=random_xPie, names=namesPie)

labels = ["Male", "Female"]

fig3 = make_subplots(1, 2, specs=[[{"type": "xy"}, {'type':'domain'} ]])

fig3.add_trace(go.Bar(y=[2, 3, 1]),
              row=1, col=1)
fig3.add_trace(go.Pie(labels=labels, values=[48,52], scalegroup='one'), 1, 2)

fig = go.Figure()
fig.add_trace(go.Scatter(x=rd['Day'], y=rd['TX'], mode='lines', name='TX', ))
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
fig.update_layout(xaxis_title="Days", yaxis_title='Count', title="States Count Over Time", legend_title="States")


fig2 = go.Figure(go.Scattermapbox(), )

latCity = ['32.7767', '30.2672', '29.7604', '29.4241', '34.0522', '32.7157', '37.3382', '37.7749']
lonCity = ['-96.7970', '-97.7431', '-95.3698', '-98.4936', '-118.2437', '-117.1611', '-121.8863', '-122.4194']
cityName = ['Dallas', 'Austin', 'Houston', 'San Antonio', 'Los Angeles', 'San Diego', 'San Jose', 'San Francisco']
stateCityIn = ['TX', 'TX', 'TX', 'TX', 'CA', 'CA', 'CA', 'CA']

countyName = ['Harris County', 'Dallas County', 'Tarrant County', 'El Paso County', 'Bexar County', 'Hidalgo County',
              'Travis County']
countyCases = [166545, 101282, 65426, 63161, 54572, 36686, 33016]
countyDeaths = [2866, 1319, 878, 697, 1429, 1741, 455]
countyRecovery = [135980, 89343, 56715, 35858, 50087, 32783, 31377]
countyActive = [27699, 10620, 7833, 26606, 3056, 2163, 1184]


fig4 = go.Figure(data=[go.Table(header=dict(values=['CountyName','CountyCases', 'CountyDeaths', 'CountyRecovery',
                                                    'CountyActive']),
                 cells=dict(values=[countyName, countyCases, countyDeaths, countyRecovery, countyActive]))
                     ])

fig2 = go.Figure(go.Scattermapbox(
        lat=latCity,
        lon=lonCity,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=[56, 20, 25, 24, 60, 29, 40, 20]
        ),
        text=['Dallas', 'Austin', 'Houston', 'San Antonio', 'Los Angeles', 'San Diego', 'San Jose', 'San Francisco'],
    ))
fig2.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken="pk.eyJ1IjoibWluaHRyYW4yMSIsImEiOiJja2dlNG53YmYwZHhqMnJsN2tpNHUwZXR1In0.VOD0SAfL2ZQgAtZ0W6Vg0g",
        bearing=0,
        center=dict(
            lat=30,
            lon=-97,
        ),
        pitch=0,
        zoom=4,
    ),
    margin=dict(t=0, b=0, l=0, r=0)
)

fig2.update_layout(mapbox_style="dark", mapbox_accesstoken="pk.eyJ1IjoibWluaHRyYW4yMSIsImEiOiJja2dlNG53YmYwZHhqMnJsN2tpNHUwZXR1In0.VOD0SAfL2ZQgAtZ0W6Vg0g")

image_filename = 'a1.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

# Creates a list of dictionaries, which have the keys 'label' and 'value'.
def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list

# Initialize the app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('Dash - STOCK PRICES'),
                                 html.P('''Visualising time series with Plotly - Dash'''),
                                 html.P('''Pick one or more stocks from the dropdown below.'''),
                                 html.Div(className='div-for-dropdown',
                                          children=[
                                              dcc.Dropdown(id='stockselector',
                                                           options=get_options(df['stock'].unique()),
                                                           multi=True,
                                                           value=[df['stock'].sort_values()[0]],
                                                           style={'backgroundColor': '#1E1E1E'},
                                                           className='stockselector')
                                          ],
                                          style={'color': '#1E1E1E'})
                             ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='timeseries',
                                           config={'displayModeBar': False},
                                           animate=True
                                           ),
                                dcc.Graph(id='change', config={'displayModeBar': False}, animate=True)
                             ])
                              ])
        ]

)

@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_timeseries(selected_dropdown_value):
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''
    # STEP 1
    trace = []
    df_sub = df
    # STEP 2
    # Draw and append traces for each stock
    for stock in selected_dropdown_value:
        trace.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['value'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    # STEP 3
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    # Define Figure
    # STEP 4
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),

              }

    return figure

@app.callback(Output('change', 'figure'),
              [Input('stockselector', 'value')])
def update_change(selected_dropdown_value):
    ''' Draw traces of the feature 'change' based one the currently selected stocks '''
    trace = []
    df_sub = df
    # Draw and append traces for each stock
    for stock in selected_dropdown_value:
        trace.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['change'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    # Define Figure
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'t': 50},
                  height=250,
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Daily Change', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'showticklabels': False, 'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }

    return figure



if __name__ == '__main__':
    app.run_server(debug=True)
