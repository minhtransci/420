import dash
import base64
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
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

# Load data
df = pd.read_csv('data/stockdata2.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])
# Creates a list of dictionaries, which have the keys 'label' and 'value'.
def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})
    return dict_list
# Initialize the app
app = dash.Dash(__name__)
server = app.server
card_content = [
    dbc.CardHeader("Card header"),
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text",
            ),
        ]
    ),
]

app.layout = html.Div([
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Tab 1', value='tab-1'),
        dcc.Tab(label='Tab 2', value='tab-2'),
        dcc.Tab(label='Tab 3', value='tab-3'),
        dcc.Tab(label='Tab 4', value='tab-4'),
        dcc.Tab(label='Tab 5', value='tab-5'),
    ], ),
    html.Div(id='tabs-content-inline')
])
dictCity = {}
for i in range(len(latCity)):
    dictCity[cityName[i]] = [(latCity[i], lonCity[i])]

def randomNum():
    random.seed(datetime.now())
    retVal = random.randint(0, 10000000000)
    return retVal

@app.callback(Output('darkMap', 'figure'),
              Input('citySelector', 'value'))
def update_map(val):
    if(val == 999):
        return fig2
    fig2.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken="pk.eyJ1IjoibWluaHRyYW4yMSIsImEiOiJja2dlNG53YmYwZHhqMnJsN2tpNHUwZXR1In0.VOD0SAfL2ZQgAtZ0W6Vg0g",
            center=dict(
                lat=float(latCity[val]),
                lon=float(lonCity[val]),
            ),
            pitch=0,
            zoom=8,
        )
    )
    zoomVal = fig2['layout']['mapbox']['zoom']
    print(zoomVal)
    return fig2

@app.callback(Output('timeseries', 'figure'),
              [Input('stateSelector', 'value'),
               Input('plotSelector', 'value')])
def update_timeseries(selected_dropdown_value, selected_plot_value):
    selectedData = dataVal[selected_plot_value]

    fig = go.Figure(layout={'paper_bgcolor':'rgb(233,233,233)'})
    fig.update_layout(xaxis_title="Days", yaxis_title='Count', title="States Count Over Time", legend_title="States")
    print("Update state", selected_dropdown_value)
    print("Update plot", selected_plot_value)
    if len(selected_dropdown_value) > 0:
        for i in range(len(selected_dropdown_value)):
            stateVal = selected_dropdown_value[i]
            fig.add_trace(go.Scatter(x=selectedData['Day'], y=selectedData[stateVal], mode='lines', name=stateVal))
    else:
        fig.add_trace(go.Scatter(x=selectedData['Day'], y=selectedData['TX'], mode='lines', name='TX'))
    fig.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    return fig

@app.callback(Output('tabs-content-inline', 'children'),
              [Input('tabs-styled-with-inline', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
            children=[
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.Img(
                                              className="logo", src=app.get_asset_url("dash-logo-new.png")
                                          ),
                                          html.H2('Dash - Covid Template'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='plotSelector',
                                                           options=[
                                                               {'label': 'Cumulative Cases', 'value': 0},
                                                               {'label': 'Cumulative Deaths', 'value': 1},
                                                               {'label': '7-Day Rolling Cases', 'value': 2},
                                                               {'label': '7-Day Rolling Deaths', 'value': 3}
                                                           ],
                                                           value=3,
                                                           searchable=False,
                                                           clearable=False,
                                                           className='fuck'
                                                       )
                                                   ]),
                                          html.P('''Visualising time series with Plotly - Dash'''),
                                          html.P('''Pick one or more states from the dropdown below.'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='stateSelector',
                                                           options=[
                                                               {'label': 'California', 'value': 'CA'},
                                                               {'label': 'Florida', 'value': 'FL'},
                                                               {'label': 'Illionis', 'value': 'IL'},
                                                               {'label': 'North Carolina', 'value': 'NC'},
                                                               {'label': 'Texas', 'value': 'TX'},
                                                               {'label': 'Wisconsin', 'value': 'WI'}
                                                           ],
                                                           value=['TX'],
                                                           multi=True,
                                                           clearable=False,
                                                           className='stateSelector'
                                                       ),
                                                   ],
                                                   style={'color': '#1E1E1E'}),
                                          dbc.Col(html.Div([
                                              dbc.Card(dbc.CardBody(
                                                  [
                                                      dbc.CardLink("Get Tested Now",
                                                                   href="https://publichealth.harriscountytx.gov/Resources/2019-Novel-Coronavirus/COVID-19-Testing-Information"),
                                                  ]
                                              ), color="dark", inverse=True, body=True),
                                          ])),
                                      ]
                                      ),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dbc.Row(
                                              [
                                                  dbc.Col(dbc.Card(
                                                      [
                                                          dbc.CardHeader(
                                                              [
                                                                  html.H5("United States")
                                                              ]
                                                          ),
                                                          dbc.CardBody(
                                                              [
                                                                  html.I(className="fas fa-notes-medical"),
                                                                  html.H5("Current Infections", className="card-title"),
                                                                  html.H5(
                                                                      "123,456,789",
                                                                      className="card-title",
                                                                  ),
                                                              ]
                                                          ),
                                                      ], color="warning", inverse=True)),
                                                  dbc.Col(dbc.Card(
                                                      [
                                                          dbc.CardHeader(
                                                              [
                                                                  html.H5("United States")
                                                              ]
                                                          ),
                                                          dbc.CardBody(
                                                              [
                                                                  html.I(className="fas fa-heart-broken"),
                                                                  html.H5("Deaths", className="card-title"),
                                                                  html.H5(
                                                                      "123,456,789",
                                                                      className="card-title",
                                                                  ),
                                                              ]
                                                          ),
                                                      ], color="danger", inverse=True)),
                                                  dbc.Col(dbc.Card(
                                                      [
                                                          dbc.CardHeader(
                                                              [
                                                                  html.H5("United States")
                                                              ]
                                                          ),
                                                          dbc.CardBody(
                                                              [
                                                                  html.I(className="fas fa-heart"),
                                                                  html.H5("Recovered", className="card-title"),
                                                                  html.H5(
                                                                      "123,456,789",
                                                                      className="card-title",
                                                                  ),
                                                              ]
                                                          ),
                                                      ], color="success", inverse=True)),
                                              ],
                                              className="mb-4", justify="center", align="center"
                                          ),
                                          dcc.Graph(id='timeseries',
                                                    config={'displayModeBar': False},
                                                    figure=fig
                                                    ),
                                      ], style={'text-align': 'center'})
                         ])
            ]
        )
    elif tab == 'tab-2':
        return html.Div(
            children=[
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.Img(
                                              className="logo", src=app.get_asset_url("dash-logo-new.png")
                                          ),
                                          html.H2('Dash - Covid Map'),
                                          html.P('''Move around the map and select a city'''),
                                          html.P('''Pick a city below'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='stateSelector2',
                                                           options=[
                                                               {'label': 'Texas', 'value': 'TX'},
                                                               {'label': 'California', 'value': 'CA'},
                                                           ],
                                                           value='TX',
                                                           searchable=False,
                                                           clearable=False,
                                                           className='fuck'
                                                       ),
                                                       dcc.Dropdown(
                                                           id='citySelector',
                                                           options=[
                                                               {'label': 'Dallas', 'value': 0},
                                                               {'label': 'Austin', 'value': 1},
                                                               {'label': 'Houston', 'value': 2},
                                                               {'label': 'San Antonio', 'value': 3}
                                                           ],
                                                           value=999,
                                                           searchable=False,
                                                           clearable=False,
                                                           className='fuck'
                                                       )
                                                   ]),
                                      ]
                                      ),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dcc.Graph(id='darkMap',
                                                    config={'displayModeBar': False},
                                                    figure=fig2
                                                    ),
                                          dcc.Graph(
                                              id='example-graph-2',
                                              figure=fig4
                                          ),
                                      ])
                         ])
            ]
        )



if __name__ == '__main__':
    app.run_server(debug=True)