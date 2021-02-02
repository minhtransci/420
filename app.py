import dash
import base64
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import random
import dash_daq as daq
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

image_filename = 'a1.jpg' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])

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

@app.callback(Output('citySelector', 'options'),
              Input('stateSelector2', 'value'))
def updateCity(value):
    if value == 'TX':
        return [{'label': 'Dallas', 'value': 0},{'label': 'Austin', 'value': 1},{'label': 'Houston', 'value': 2},
            {'label': 'San Antonio', 'value': 3}]
    else:
        return [{'label': 'Los Angeles', 'value': 4},{'label': 'San Diego', 'value': 5},{'label': 'San Jose', 'value': 6},
            {'label': 'San Francisco', 'value': 7}]



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

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '16px'}
    lon = random.randint(0, 10000000000)
    lat = random.randint(0, 10000000000)
    alt = random.randint(0, 10000000000)
    return [
        html.Span('Longitude: {0:.2f}'.format(lon), style=style),
        html.Span('Latitude: {0:.2f}'.format(lat), style=style),
        html.Span('Altitude: {0:0.2f}'.format(alt), style=style)
    ]

def randomNum():
    random.seed(datetime.now())
    retVal = random.randint(0, 10000000000)
    return retVal

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

@app.callback(Output('pieGraph', 'figure'),
              [Input('pieSelector1', 'value'),
               Input('pieSelector2', 'value')])
def update_pieGraph(selected_pie1_value, selected_pie2_value):
    random.seed(selected_pie1_value + selected_pie2_value)
    a = random.randint(50, 100)
    b = random.randint(75, 125)
    c = random.randint(25, 75)
    random_xPie = [a, b, c]
    namesPie = ['Random Positive', 'Random Negative', 'Random Neutral']

    figPie = px.pie(values=random_xPie, names=namesPie)
    return figPie

@app.callback(Output('timeTweet', 'figure'),
              [Input('pieSelector1', 'value'),
               Input('pieSelector2', 'value')])
def update_timeTweet(selected_pie1_value, selected_pie2_value):
    random.seed(selected_pie1_value + selected_pie2_value)
    x = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    random.seed(selected_pie1_value + selected_pie2_value)
    aList = []
    bList = []
    cList = []
    fig = go.Figure(layout={'paper_bgcolor':'rgb(233,233,233)'})
    fig.update_layout(xaxis_title="Days", yaxis_title='Percentage', title="Tweet", legend_title="Reaction")
    for i in range(len(x)):
        a = random.randint(30, 40)
        b = random.randint(40, 50)
        c = 100 - a - b
        aList.append(a/100.0)
        bList.append(b/100.0)
        cList.append(c/100.0)
    fig.add_trace(go.Scatter(x=x, y=aList, mode='lines', name='Positive'))
    fig.add_trace(go.Scatter(x=x, y=bList, mode='lines', name='Negative'))
    fig.add_trace(go.Scatter(x=x, y=cList, mode='lines', name='Neutral'))
    return fig


@app.callback(Output('statePlot', 'figure'),
              [Input('StatePick', 'value'),
               Input('PlotPick', 'value')])
def update_statePlot(state_value, type_value):
    global aTime
    a = datetime.datetime.now()
    fig6 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig6.update_layout(xaxis_title="Days", yaxis_title='Count', title=type_value, legend_title="States")
    for j in range(len(state_value)):
        if state_value[j] not in stateDictionary:
            if state_value[j] != 'us':
                r = requests.get('https://api.covidtracking.com/v1/states/'+state_value[j]+'/daily.json')
            else:
                r = requests.get('https://api.covidtracking.com/v1/us/daily.json')
            date = []
            numbers1 = []
            numbers2 = []
            numbers3 = []
            numbers4 = []
            numbers5 = []
            b = r.json()
            for days in range(len(b)-1, -1, -1):
                f = str(b[days]['date'])
                date.append(f[0:4] + '-' + f[4:6] + '-' + f[6:8])
                numbers1.append(b[days]['positive'])
                numbers2.append(b[days]['positiveIncrease'])
                numbers3.append(b[days]['hospitalizedCurrently'])
                numbers4.append(b[days]['death'])
                numbers5.append(b[days]['deathIncrease'])

            stateDictionary[state_value[j]] = date
            stateDictionary[state_value[j]+'-positive'] = numbers1
            stateDictionary[state_value[j] + '-positiveIncrease'] = numbers2
            stateDictionary[state_value[j] + '-hospitalizedCurrently'] = numbers3
            stateDictionary[state_value[j] + '-death'] = numbers4
            stateDictionary[state_value[j] + '-deathIncrease'] = numbers5

        fig6.add_trace(go.Scatter(x=stateDictionary[state_value[j]], y=stateDictionary[state_value[j] + '-' + type_value], mode='lines', name=state_value[j]))
    fig6.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    print(datetime.datetime.now() - a)
    return fig6


@app.callback(Output('MultiPlots', 'children'),
              [Input('stateMultiPick', 'value')])
def MultiStepPlot(state):
    fig11 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig11.update_layout(xaxis_title="Days", yaxis_title='Count', title=state + '-positive')
    fig12 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig12.update_layout(xaxis_title="Days", yaxis_title='Count', title=state + '-positiveIncrease')
    fig13 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig13.update_layout(xaxis_title="Days", yaxis_title='Count', title=state + '-death')
    fig14 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig14.update_layout(xaxis_title="Days", yaxis_title='Count', title=state + '-deathIncrease')
    fig15 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig15.update_layout(xaxis_title="Days", yaxis_title='Count', title=state + '-hospitalizedCurrently')
    a = datetime.datetime.now()
    if state not in stateDictionary:
        a = datetime.datetime.now()
        if state != 'us':
            r = requests.get('https://api.covidtracking.com/v1/states/'+state+'/daily.json')
        else:
            r = requests.get('https://api.covidtracking.com/v1/us/daily.json')
        date = []
        numbers1 = []
        numbers2 = []
        numbers3 = []
        numbers4 = []
        numbers5 = []
        b = r.json()
        for days in range(len(b)-1, -1, -1):
            f = str(b[days]['date'])
            date.append(f[0:4] + '-' + f[4:6] + '-' + f[6:8])
            numbers1.append(b[days]['positive'])
            numbers2.append(b[days]['positiveIncrease'])
            numbers3.append(b[days]['hospitalizedCurrently'])
            numbers4.append(b[days]['death'])
            numbers5.append(b[days]['deathIncrease'])

        stateDictionary[state] = date
        stateDictionary[state+'-positive'] = numbers1
        stateDictionary[state + '-positiveIncrease'] = numbers2
        stateDictionary[state + '-hospitalizedCurrently'] = numbers3
        stateDictionary[state + '-death'] = numbers4
        stateDictionary[state+ '-deathIncrease'] = numbers5

    new1List = stateDictionary[state + '-positiveIncrease']
    new2List = stateDictionary[state + '-deathIncrease']

    mva1 = [0] * 7
    mva2 = [0] * 7
    var1 = 0
    var2 = 0
    for day in range(0,7):
        var1 = var1 + new1List[day]
        var2 = var2 + new2List[day]
    for day in range(7,len(stateDictionary[state])):
        mva1.append(var1/7.0)
        mva2.append(var2/7.0)
        var1 = var1 + new1List[day]
        var2 = var2 + new2List[day]
        var1 = var1 - new1List[day - 7]
        var2 = var2 - new2List[day - 7]

    fig11.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-positive'], mode='lines', name=state))
    fig11.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig12.add_trace(go.Bar(x=stateDictionary[state], y=stateDictionary[state + '-positiveIncrease']))
    fig12.add_trace(go.Scatter(x=stateDictionary[state], y=mva1))
    fig12.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig13.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-death'], mode='lines', name=state))
    fig13.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig14.add_trace(go.Bar(x=stateDictionary[state], y=stateDictionary[state + '-deathIncrease']))
    fig14.add_trace(go.Scatter(x=stateDictionary[state], y=mva2))
    fig14.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig15.add_trace(go.Bar(x=stateDictionary[state], y=stateDictionary[state + '-hospitalizedCurrently']))
    fig15.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig12.update_layout(
        updatemenus=[go.layout.Updatemenu(
            type="buttons",
            active=1,
            buttons=list(
                [dict(label='None',
                      method='update',
                      args=[{'visible': [True, False]},
                            {'title': 'None',
                             'showlegend': True}]),
                 dict(label='LineDaily',
                      method='update',
                      args=[{'visible': [True, True]},
                            # the index of True aligns with the indices of plot traces
                            {'title': 'LineDaily',
                             'showlegend': True}]),
                 ])
        )
        ])
    fig14.update_layout(
        updatemenus=[go.layout.Updatemenu(
            type="buttons",
            active=1,
            buttons=list(
                [dict(label='None',
                      method='update',
                      args=[{'visible': [True, False]},
                            {'title': 'None',
                             'showlegend': True}]),
                 dict(label='LineDaily',
                      method='update',
                      args=[{'visible': [True, True]},
                            # the index of True aligns with the indices of plot traces
                            {'title': 'LineDaily',
                             'showlegend': True}]),
                 ])
        )
        ])
    print('TimeA', datetime.datetime.now() - a)
    return html.Div(
        children=[
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=fig11
                      ),
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=fig12
                      ),

            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=fig13
                      ),
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=fig14
                      ),
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=fig15
                      ),

    ]
    )

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

    elif tab == 'tab-3':
        return html.Div(
            children=[
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.Img(
                                              className="logo", src=app.get_asset_url("dash-logo-new.png")
                                          ),
                                          html.H2('Dash - Twitter Covid Sentiment'),
                                          html.P('''Pick a subject'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='pieSelector1',
                                                           options=[
                                                               {'label': 'Covid', 'value': 0},
                                                               {'label': 'Trump', 'value': 1},
                                                               {'label': 'Whitmer', 'value': 2},
                                                               {'label': 'Fauci', 'value': 3},
                                                               {'label': 'Moderna', 'value': 4},
                                                               {'label': 'Schools', 'value': 5},
                                                           ],
                                                           value=0,
                                                           searchable=False,
                                                           clearable=False,
                                                           className='pieSelect1'
                                                       )
                                                   ]),
                                          html.P('''Pick a measurement'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='pieSelector2',
                                                           options=[
                                                               {'label': 'Tweets', 'value': 0},
                                                               {'label': 'Engagement', 'value': 1},
                                                           ],
                                                           value=0,
                                                           searchable=False,
                                                           clearable=False,
                                                           className='pieSelect2'
                                                       )
                                                   ]),
                                      ]
                                      ),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dcc.Graph(id='pieGraph',
                                                    config={'displayModeBar': False},
                                                    figure=figPie
                                                    ),
                                          dcc.Graph(id='timeTweet',
                                                    config={'displayModeBar': False},
                                                    figure=fig
                                                    ),
                                      ])
                         ])
            ]
        )
    elif tab == 'tab-4':
        return html.Div(
            children=[
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.Img(
                                              className="logo", src=app.get_asset_url("dash-logo-new.png")
                                          ),
                                          html.H2('Dash - Updated Covid Data'),
                                          html.P('''Compare and Pick the States'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='StatePick',
                                                           options=[
                                                               {'label': 'National', 'value': 'us'},
                                                               {'label': 'Alabama', 'value': 'al'},
                                                               {'label': 'Alaska', 'value': 'ak'},
                                                               {'label': 'Arizona', 'value': 'az'},
                                                               {'label': 'Arkansas', 'value': 'ar'},
                                                               {'label': 'California', 'value': 'ca'},
                                                               {'label': 'Colorado', 'value': 'co'},
                                                               {'label': 'Connecticut', 'value': 'ct'},
                                                               {'label': 'Delaware', 'value': 'de'},
                                                               {'label': 'Florida', 'value': 'fl'},
                                                               {'label': 'Georgia', 'value': 'ga'},
                                                               {'label': 'Hawaii', 'value': 'hi'},
                                                               {'label': 'Idaho', 'value': 'id'},
                                                               {'label': 'Illinois', 'value': 'il'},
                                                               {'label': 'Indiana', 'value': 'in'},
                                                               {'label': 'Iowa', 'value': 'ia'},
                                                               {'label': 'Kansas', 'value': 'ks'},
                                                               {'label': 'Kentucky', 'value': 'ky'},
                                                               {'label': 'Louisiana', 'value': 'la'},
                                                               {'label': 'Maine', 'value': 'me'},
                                                               {'label': 'Maryland', 'value': 'md'},
                                                               {'label': 'Massachusetts', 'value': 'ma'},
                                                               {'label': 'Michigan', 'value': 'mi'},
                                                               {'label': 'Minnesota', 'value': 'mn'},
                                                               {'label': 'Mississippi', 'value': 'ms'},
                                                               {'label': 'Missouri', 'value': 'mo'},
                                                               {'label': 'Montana', 'value': 'mt'},
                                                               {'label': 'Nebraska', 'value': 'ne'},
                                                               {'label': 'Nevada', 'value': 'nv'},
                                                               {'label': 'New Hampshire', 'value': 'nh'},
                                                               {'label': 'New Jersey', 'value': 'nj'},
                                                               {'label': 'New Mexico', 'value': 'nm'},
                                                               {'label': 'New York', 'value': 'ny'},
                                                               {'label': 'North Carolina', 'value': 'nc'},
                                                               {'label': 'North Dakota', 'value': 'nd'},
                                                               {'label': 'Ohio', 'value': 'oh'},
                                                               {'label': 'Oklahoma', 'value': 'ok'},
                                                               {'label': 'Oregon', 'value': 'or'},
                                                               {'label': 'Pennsylvania', 'value': 'pa'},
                                                               {'label': 'Rhode Island', 'value': 'ri'},
                                                               {'label': 'South Carolina', 'value': 'sc'},
                                                               {'label': 'South Dakota', 'value': 'sd'},
                                                               {'label': 'Tennessee', 'value': 'tn'},
                                                               {'label': 'Texas', 'value': 'tx'},
                                                               {'label': 'Utah', 'value': 'ut'},
                                                               {'label': 'Vermont', 'value': 'vt'},
                                                               {'label': 'Virginia', 'value': 'va'},
                                                               {'label': 'Washington', 'value': 'wa'},
                                                               {'label': 'West Virginia', 'value': 'wv'},
                                                               {'label': 'Wisconsin', 'value': 'wi'},
                                                               {'label': 'Wyoming', 'value': 'wy'},
                                                           ],
                                                           value=['tx'],
                                                           placeholder='Select a State',
                                                           multi=True,
                                                           searchable=True,
                                                           className='fuck'
                                                       )
                                                   ]),
                                          html.P('Covid Measurement Metrics to compare'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='PlotPick',
                                                           options=[
                                                               {'label': 'Total Positive', 'value': 'positive'},
                                                               {'label': 'Positive Increase', 'value': 'positiveIncrease'},
                                                               {'label': 'Total Death', 'value': 'death'},
                                                               {'label': 'Death Increase', 'value': 'deathIncrease'},
                                                               {'label': 'Hospitalized Currently', 'value': 'hospitalizedCurrently'}
                                                           ],
                                                           value='positiveIncrease',
                                                           searchable=False,
                                                           clearable=False,
                                                           className='fuck'
                                                       )
                                                   ],
                                                   style={'color': '#1E1E1E'}),
                                      ]
                                      ),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dcc.Loading(
                                              children= [dcc.Graph(id='statePlot',
                                                        config={'displayModeBar': False},
                                                        figure=fig
                                                        )
                                                     ])
                                      ])
                         ])
            ]
        )
    elif tab == 'tab-5':
        return html.Div(
            children=[
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.Img(
                                              className="logo", src=app.get_asset_url("dash-logo-new.png")
                                          ),
                                          html.H2('Dash - State Covid Data'),
                                          html.P('''Pick a state'''),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='stateMultiPick',
                                                           options=[
                                                               {'label': 'National', 'value': 'us'},
                                                               {'label': 'Alabama', 'value': 'al'},
                                                               {'label': 'Alaska', 'value': 'ak'},
                                                               {'label': 'Arizona', 'value': 'az'},
                                                               {'label': 'Arkansas', 'value': 'ar'},
                                                               {'label': 'California', 'value': 'ca'},
                                                               {'label': 'Colorado', 'value': 'co'},
                                                               {'label': 'Connecticut', 'value': 'ct'},
                                                               {'label': 'Delaware', 'value': 'de'},
                                                               {'label': 'Florida', 'value': 'fl'},
                                                               {'label': 'Georgia', 'value': 'ga'},
                                                               {'label': 'Hawaii', 'value': 'hi'},
                                                               {'label': 'Idaho', 'value': 'id'},
                                                               {'label': 'Illinois', 'value': 'il'},
                                                               {'label': 'Indiana', 'value': 'in'},
                                                               {'label': 'Iowa', 'value': 'ia'},
                                                               {'label': 'Kansas', 'value': 'ks'},
                                                               {'label': 'Kentucky', 'value': 'ky'},
                                                               {'label': 'Louisiana', 'value': 'la'},
                                                               {'label': 'Maine', 'value': 'me'},
                                                               {'label': 'Maryland', 'value': 'md'},
                                                               {'label': 'Massachusetts', 'value': 'ma'},
                                                               {'label': 'Michigan', 'value': 'mi'},
                                                               {'label': 'Minnesota', 'value': 'mn'},
                                                               {'label': 'Mississippi', 'value': 'ms'},
                                                               {'label': 'Missouri', 'value': 'mo'},
                                                               {'label': 'Montana', 'value': 'mt'},
                                                               {'label': 'Nebraska', 'value': 'ne'},
                                                               {'label': 'Nevada', 'value': 'nv'},
                                                               {'label': 'New Hampshire', 'value': 'nh'},
                                                               {'label': 'New Jersey', 'value': 'nj'},
                                                               {'label': 'New Mexico', 'value': 'nm'},
                                                               {'label': 'New York', 'value': 'ny'},
                                                               {'label': 'North Carolina', 'value': 'nc'},
                                                               {'label': 'North Dakota', 'value': 'nd'},
                                                               {'label': 'Ohio', 'value': 'oh'},
                                                               {'label': 'Oklahoma', 'value': 'ok'},
                                                               {'label': 'Oregon', 'value': 'or'},
                                                               {'label': 'Pennsylvania', 'value': 'pa'},
                                                               {'label': 'Rhode Island', 'value': 'ri'},
                                                               {'label': 'South Carolina', 'value': 'sc'},
                                                               {'label': 'South Dakota', 'value': 'sd'},
                                                               {'label': 'Tennessee', 'value': 'tn'},
                                                               {'label': 'Texas', 'value': 'tx'},
                                                               {'label': 'Utah', 'value': 'ut'},
                                                               {'label': 'Vermont', 'value': 'vt'},
                                                               {'label': 'Virginia', 'value': 'va'},
                                                               {'label': 'Washington', 'value': 'wa'},
                                                               {'label': 'West Virginia', 'value': 'wv'},
                                                               {'label': 'Wisconsin', 'value': 'wi'},
                                                               {'label': 'Wyoming', 'value': 'wy'},
                                                           ],
                                                           value='us',
                                                           searchable=False,
                                                           className='fuck'
                                                       )
                                                   ]),
                                          html.P('''Visualising time series with Plotly - Dash'''),
                                          html.P('''Pick one or more states from the dropdown below.'''),
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
                                              className="mb-4", justify="center", align="center", style={'text-align': 'center'}
                                          ),
                                          dcc.Loading(
                                          html.Div(id='MultiPlots',
                                                   )
                                          )
                                            ])
                         ])
            ]
        )

if __name__ == '__main__':
    app.config['suppress_callback_exceptions'] = True
    app.run_server(debug=True)