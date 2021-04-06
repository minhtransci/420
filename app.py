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
import mysql.connector

# Load data
cc = pd.read_csv('data/cumulative_cases.csv', skiprows=3)
cd = pd.read_csv('data/cumulative_deaths.csv', skiprows=3)
rc = pd.read_csv('data/sevenday_rolling_average_of_new_cases.csv', skiprows=3)
rd = pd.read_csv('data/sevenday_rolling_average_of_new_deaths.csv', skiprows=3)
covid_df = pd.read_csv('Covid_Val.csv')
vax_df = pd.read_csv('Vaccine_Val.csv')

covid_pos = covid_df["polarity_positive_percent"]
covid_neg = covid_df["polarity_negative_percent"]
covid_neu = covid_df["polarity_neutral_percent"]
covid_dates = covid_df["CreateDate"]
covid_dates = covid_dates[10:]
covid_pos = covid_pos[10:]
covid_neg = covid_neg[10:]

vax_pos = vax_df["polarity_positive_percent"]
vax_neg = vax_df["polarity_negative_percent"]
vax_neu = vax_df["polarity_neutral_percent"]
vax_dates = vax_df["CreateDate"]

stateDictionary = {}
fig = go.Figure(layout={'paper_bgcolor':'rgb(233,233,233)'})

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
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
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-6', children=[
        dcc.Tab(label='Twitter Sentiment', value='tab-3'),
        dcc.Tab(label='Compare States', value='tab-4'),
        dcc.Tab(label='State Level', value='tab-5'),
        dcc.Tab(label='Forecasting', value='tab-6'),
    ], ),
    html.Div(id='tabs-content-inline')
])
dictCity = {}

@app.callback(Output('pieGraph', 'figure'),
              [Input('pieSelector1', 'value')])
def update_pieGraph(selected_pie1_value):
    if (selected_pie1_value == 0):
        a = covid_pos.iloc[-1]
        b = covid_neg.iloc[-1]
    else:
        a = vax_pos.iloc[-1]
        b = vax_neg.iloc[-1]
    random_xPie = [a, b]
    namesPie = ['Positive', 'Negative']

    figPie = px.pie(values=random_xPie, names=namesPie)
    return figPie

@app.callback(Output('timeTweet', 'children'),
              [Input('pieSelector1', 'value')])
def update_timeTweet(selected_pie1_value):
    fig = go.Figure(layout={'paper_bgcolor':'rgb(233,233,233)'})
    fig.update_layout(xaxis_title="Days", yaxis_title='Percentage', title="Tweet", legend_title="Reaction")
    if(selected_pie1_value == 0):
        fig.add_trace(go.Scatter(x=covid_dates, y=covid_pos, mode='lines', name='Positive'))
        fig.add_trace(go.Scatter(x=covid_dates, y=covid_neg, mode='lines', name='Negative'))
    else:
        fig.add_trace(go.Scatter(x=vax_dates, y=vax_pos, mode='lines', name='Positive'))
        fig.add_trace(go.Scatter(x=vax_dates, y=vax_neg, mode='lines', name='Negative'))
    #fig.add_trace(go.Scatter(y=covid_neu, mode='lines', name='Neutral'))
    if (5==5):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          figure=fig
                          ),
                html.P('.'),
            ]
        )

@app.callback(Output('citySelector', 'options'),
              Input('stateSelector2', 'value'))
def updateCity(value):
    if value == 'TX':
        return [{'label': 'Dallas', 'value': 0},{'label': 'Austin', 'value': 1},{'label': 'Houston', 'value': 2},
            {'label': 'San Antonio', 'value': 3}]
    else:
        return [{'label': 'Los Angeles', 'value': 4},{'label': 'San Diego', 'value': 5},{'label': 'San Jose', 'value': 6},
            {'label': 'San Francisco', 'value': 7}]





@app.callback(Output('statePlot', 'children'),
              [Input('StatePick', 'value'),
               Input('PlotPick', 'value')])
def update_statePlot(state_value, type_value):
    global aTime
    a = datetime.datetime.now()
    fig6 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig6.update_layout(xaxis_title="Days", yaxis_title='Count', title=type_value, legend_title="States")
    for j in range(len(state_value)):
        if state_value[j] not in stateDictionary:
            r = requests.get('https://api.covidactnow.org/v2/state/' + state_value[j] + '.timeseries.json?apiKey=8e215af157c74e9fbf1d77e7e982e23d')
            date = []
            numbers1 = []
            numbers2 = []
            numbers3 = []
            numbers4 = []
            b = r.json()
            c = b['actualsTimeseries']
            for dateS in c:
                date.append(dateS['date'])
                numbers1.append(dateS['newCases'])
                numbers2.append(dateS['deaths'])
                numbers4.append(dateS['cases'])
                if 'vaccinationsInitiated' in dateS:
                    numbers3.append(dateS['vaccinationsInitiated'])
                else:
                    numbers3.append(None)


            stateDictionary[state_value[j]] = date
            stateDictionary[state_value[j] + '-cases'] = numbers4
            stateDictionary[state_value[j]+'-newCases'] = numbers1
            stateDictionary[state_value[j] + '-deaths'] = numbers2
            stateDictionary[state_value[j] + '-vaccinationsInitiated'] = numbers3


        fig6.add_trace(go.Scatter(x=stateDictionary[state_value[j]], y=stateDictionary[state_value[j] + '-' + type_value], mode='lines', name=state_value[j]))
    fig6.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    print(datetime.datetime.now() - a)
    if (5==5):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          figure=fig6
                          ),
                html.P('.'),
            ]
        )

@app.callback(Output('MultiPredict', 'children'),
              [Input('PredictPick', 'value'),])
def update_predictPlot(predict_value):
    global aTime
    a = datetime.datetime.now()
    figP = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    figC = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    figH = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})

    mydb = mysql.connector.connect(
        host='coviddata.cphvsbfyrgxg.us-east-2.rds.amazonaws.com', user='kriramz',
        password='Star3003!!!!', database='simDB'
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM sim")

    myresult = mycursor.fetchall()
    xVals = []
    yVals = []
    yValsC = []
    yValsH = []
    yValsSum = 0
    for x in myresult:
        yValsSum = yValsSum + x[3]
        xVals.append(x[0])
        yVals.append(yValsSum)
        yValsC.append(x[1])
        yValsH.append(x[2])
    figP.add_trace(
        go.Scatter(x=xVals,y=yVals, name="Cumulative Predicted Deaths"),
    )
    figC.add_trace(
        go.Scatter(x=xVals,y=yValsC, name="Daily Predicted Infections"),

    )
    figH.add_trace(
        go.Scatter(x=xVals,y=yValsH, name="Daily Predicted Hospitalizations"),
    )
    ###
    r1 = requests.get('https://minhtransci.github.io/sample.json')
    b1 = r1.json()
    xValTotal = []
    yValTotal = []

    for data in b1:
        xValTotal.append(data)
        yValTotal.append(b1[data])
    del xValTotal[-1]
    del yValTotal[-1]
    figP.add_trace(
        go.Scatter(x=xValTotal, y=yValTotal, name="Daily Actual Infections")
    )
    figC.update_layout(xaxis_title="Date", yaxis_title='Daily Infections Count from COVID-19', title='Modeled COVID-19 Infections in the United States Over Time', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    figP.update_layout(xaxis_title="Date", yaxis_title='Cumulative Deaths Count from COVID-19', title='Modeled Deaths from COVID-19 in the United States Over Time', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    figH.update_layout(xaxis_title="Date", yaxis_title='Daily Hospitalizations Count from COVID-19', title='Modeled Hospitalizations due to COVID-19 in the United States Over Time', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    if(predict_value == "predictedCases"):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=figC
                          ),
                html.P('The model estimates the total number of infections in the US population from the COVID-19 virus, accounting for tested and untested individuals.'),
            ]
        )
    elif(predict_value == "predictedDeaths"):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=figP
                          ),
                html.P('The model estimates the actual total number of deceased in the US population from the COVID-19 virus. The accuracy of the model drops drastically at the beginning of February, as shown by the divergence between the predicted and actual curves. It was assumed that this was caused by the vaccine being more effective than predicted, which resulted in fewer deaths than the model predicted.'),
            ]
        )
    else:
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=figH
                          ),
                html.P('The model estimates the total number of hospitalizations in the US population from the COVID-19 virus. Daily values are calculated using modeled infections and a hospitalization multiplier.'),
            ]
        )


@app.callback(Output('MultiPlots', 'children'),
              [Input('stateMultiPick', 'value'),
               Input('StatePlotPick', 'value')],)
def MultiStepPlot(state, plotPick):

    fig11 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig11.update_layout(xaxis_title="Date", yaxis_title='Cumulative Cases', title=state + '-cases')
    fig12 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig12.update_layout(xaxis_title="Date", yaxis_title='Daily Cases', title=state + '-newCases')
    fig13 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig13.update_layout(xaxis_title="Date", yaxis_title='Cumulative Deaths', title=state + '-deaths')
    fig14 = go.Figure(layout={'paper_bgcolor': 'rgb(233,233,233)'})
    fig14.update_layout(xaxis_title="Date", yaxis_title='Cumulative Vaccinations', title=state + '-vaccinationsInitiated')
    a = datetime.datetime.now()
    if state not in stateDictionary:
        a = datetime.datetime.now()
        r = requests.get('https://api.covidactnow.org/v2/state/' + state + '.timeseries.json?apiKey=8e215af157c74e9fbf1d77e7e982e23d')
        date = []
        numbers1 = []
        numbers2 = []
        numbers3 = []
        numbers4 = []
        b = r.json()
        c = b['actualsTimeseries']
        for days in c:
            date.append(days['date'])
            numbers1.append(days['cases'])
            numbers2.append(days['newCases'])
            numbers3.append(days['deaths'])
            if 'vaccinationsInitiated' in days:
                numbers4.append(days['vaccinationsInitiated'])
            else:
                numbers4.append(None)

        stateDictionary[state] = date
        stateDictionary[state+'-cases'] = numbers1
        stateDictionary[state + '-newCases'] = numbers2
        stateDictionary[state + '-deaths'] = numbers3
        stateDictionary[state + '-vaccinationsInitiated'] = numbers4


    new1List = stateDictionary[state + '-newCases']

    mva1 = [0] * 7
    mva2 = [0] * 7
    var1 = 0
    var2 = 0
    lastReal = 0
    lastReal7 = 0
    for day in range(0,7):
        if new1List[day]:
            var1 = var1 + new1List[day]
            lastReal = new1List[day]
        else:
            var1 = var1 + lastReal

    for day in range(7,len(stateDictionary[state])):
        mva1.append(var1/7.0)
        mva2.append(var2/7.0)
        if new1List[day]:
            var1 = var1 + new1List[day]
            lastReal = new1List[day]
            if new1List[day-7]:
                var1 = var1 - lastReal7
                lastReal7 = new1List[day-7]
            else:
                var1 = var1 - lastReal7
        else:
            var1 = var1 + lastReal
            if new1List[day-7]:
                var1 = var1 - lastReal7
                lastReal7 = new1List[day-7]
            else:
                var1 = var1 - lastReal7

    fig11.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-cases'], mode='lines', name=state))
    fig11.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig12.add_trace(go.Bar(x=stateDictionary[state], y=stateDictionary[state + '-newCases'], name=state+" Daily"))
    fig12.add_trace(go.Scatter(x=stateDictionary[state], y=mva1, name=state+" 7 Day Average"))
    fig12.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig13.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-deaths'], mode='lines', name=state))
    fig13.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    xOne = stateDictionary[state][330:]
    yOne = stateDictionary[state + '-vaccinationsInitiated'][330:]
    fig14.add_trace(go.Scatter(x=xOne, y=yOne, mode='lines', name=state))
    fig14.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
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

    print('TimeA', datetime.datetime.now() - a)
    if(plotPick == "Cases"):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=fig11
                          )
            ]
        )

    elif(plotPick == "NewCases"):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=fig12
                          ),
            ]
        )

    elif(plotPick == "Deaths"):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=fig13
                          ),
            ]
        )

    else:
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          config={'displayModeBar': False},
                          figure=fig14
                          ),
            ]
        )



@app.callback(Output('tabs-content-inline', 'children'),
              [Input('tabs-styled-with-inline', 'value')])
def render_content(tab):
    if tab == 'tab-3':
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
                                                               {'label': 'Vaccine', 'value': 1}
                                                           ],
                                                           value=0,
                                                           searchable=False,
                                                           clearable=False,
                                                           className='pieSelect1'
                                                       )
                                                   ]),
                                      ]
                                      ),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dcc.Loading(
                                          html.Div(id='timeTweet',
                                                   )
                                          )
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
                                                               {'label': 'Alabama', 'value': 'AL'},
                                                               {'label': 'Alaska', 'value': 'AK'},
                                                               {'label': 'Arizona', 'value': 'AZ'},
                                                               {'label': 'Arkansas', 'value': 'AR'},
                                                               {'label': 'California', 'value': 'CA'},
                                                               {'label': 'Colorado', 'value': 'CO'},
                                                               {'label': 'Connecticut', 'value': 'CT'},
                                                               {'label': 'Delaware', 'value': 'DE'},
                                                               {'label': 'Florida', 'value': 'FL'},
                                                               {'label': 'Georgia', 'value': 'GA'},
                                                               {'label': 'Hawaii', 'value': 'HI'},
                                                               {'label': 'Idaho', 'value': 'ID'},
                                                               {'label': 'Illinois', 'value': 'IL'},
                                                               {'label': 'Indiana', 'value': 'IN'},
                                                               {'label': 'Iowa', 'value': 'IA'},
                                                               {'label': 'Kansas', 'value': 'KS'},
                                                               {'label': 'Kentucky', 'value': 'KY'},
                                                               {'label': 'Louisiana', 'value': 'LA'},
                                                               {'label': 'Maine', 'value': 'ME'},
                                                               {'label': 'Maryland', 'value': 'MD'},
                                                               {'label': 'Massachusetts', 'value': 'MA'},
                                                               {'label': 'Michigan', 'value': 'MI'},
                                                               {'label': 'Minnesota', 'value': 'MN'},
                                                               {'label': 'Mississippi', 'value': 'MS'},
                                                               {'label': 'Missouri', 'value': 'MO'},
                                                               {'label': 'Montana', 'value': 'MT'},
                                                               {'label': 'Nebraska', 'value': 'NE'},
                                                               {'label': 'Nevada', 'value': 'NV'},
                                                               {'label': 'New Hampshire', 'value': 'NH'},
                                                               {'label': 'New Jersey', 'value': 'NJ'},
                                                               {'label': 'New Mexico', 'value': 'NM'},
                                                               {'label': 'New York', 'value': 'NY'},
                                                               {'label': 'North Carolina', 'value': 'NC'},
                                                               {'label': 'North Dakota', 'value': 'ND'},
                                                               {'label': 'Ohio', 'value': 'OH'},
                                                               {'label': 'Oklahoma', 'value': 'OK'},
                                                               {'label': 'Oregon', 'value': 'OR'},
                                                               {'label': 'Pennsylvania', 'value': 'PA'},
                                                               {'label': 'Rhode Island', 'value': 'RI'},
                                                               {'label': 'South Carolina', 'value': 'SC'},
                                                               {'label': 'South Dakota', 'value': 'SD'},
                                                               {'label': 'Tennessee', 'value': 'TN'},
                                                               {'label': 'Texas', 'value': 'TX'},
                                                               {'label': 'Utah', 'value': 'UT'},
                                                               {'label': 'Vermont', 'value': 'VT'},
                                                               {'label': 'Virginia', 'value': 'VA'},
                                                               {'label': 'Washington', 'value': 'WA'},
                                                               {'label': 'West Virginia', 'value': 'WV'},
                                                               {'label': 'Wisconsin', 'value': 'WI'},
                                                               {'label': 'Wyoming', 'value': 'WY'},
                                                           ],
                                                           value=['TX'],
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
                                                               {'label': 'newCases', 'value': 'newCases'},
                                                               {'label': 'deaths', 'value': 'deaths'},
                                                               {'label': 'vaccinationsInitiated', 'value': 'vaccinationsInitiated'},

                                                           ],
                                                           value='newCases',
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
                                          html.Div(id='statePlot',
                                                   )
                                          )
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
                                                               {'label': 'Alabama', 'value': 'AL'},
                                                               {'label': 'Alaska', 'value': 'AK'},
                                                               {'label': 'Arizona', 'value': 'AZ'},
                                                               {'label': 'Arkansas', 'value': 'AR'},
                                                               {'label': 'California', 'value': 'CA'},
                                                               {'label': 'Colorado', 'value': 'CO'},
                                                               {'label': 'Connecticut', 'value': 'CT'},
                                                               {'label': 'Delaware', 'value': 'DE'},
                                                               {'label': 'Florida', 'value': 'FL'},
                                                               {'label': 'Georgia', 'value': 'GA'},
                                                               {'label': 'Hawaii', 'value': 'HI'},
                                                               {'label': 'Idaho', 'value': 'ID'},
                                                               {'label': 'Illinois', 'value': 'IL'},
                                                               {'label': 'Indiana', 'value': 'IN'},
                                                               {'label': 'Iowa', 'value': 'IA'},
                                                               {'label': 'Kansas', 'value': 'KS'},
                                                               {'label': 'Kentucky', 'value': 'KY'},
                                                               {'label': 'Louisiana', 'value': 'LA'},
                                                               {'label': 'Maine', 'value': 'ME'},
                                                               {'label': 'Maryland', 'value': 'MD'},
                                                               {'label': 'Massachusetts', 'value': 'MA'},
                                                               {'label': 'Michigan', 'value': 'MI'},
                                                               {'label': 'Minnesota', 'value': 'MN'},
                                                               {'label': 'Mississippi', 'value': 'MS'},
                                                               {'label': 'Missouri', 'value': 'MO'},
                                                               {'label': 'Montana', 'value': 'MT'},
                                                               {'label': 'Nebraska', 'value': 'NE'},
                                                               {'label': 'Nevada', 'value': 'NV'},
                                                               {'label': 'New Hampshire', 'value': 'NH'},
                                                               {'label': 'New Jersey', 'value': 'NJ'},
                                                               {'label': 'New Mexico', 'value': 'NM'},
                                                               {'label': 'New York', 'value': 'NY'},
                                                               {'label': 'North Carolina', 'value': 'NC'},
                                                               {'label': 'North Dakota', 'value': 'ND'},
                                                               {'label': 'Ohio', 'value': 'OH'},
                                                               {'label': 'Oklahoma', 'value': 'OK'},
                                                               {'label': 'Oregon', 'value': 'OR'},
                                                               {'label': 'Pennsylvania', 'value': 'PA'},
                                                               {'label': 'Rhode Island', 'value': 'RI'},
                                                               {'label': 'South Carolina', 'value': 'SC'},
                                                               {'label': 'South Dakota', 'value': 'SD'},
                                                               {'label': 'Tennessee', 'value': 'TN'},
                                                               {'label': 'Texas', 'value': 'TX'},
                                                               {'label': 'Utah', 'value': 'UT'},
                                                               {'label': 'Vermont', 'value': 'VT'},
                                                               {'label': 'Virginia', 'value': 'VA'},
                                                               {'label': 'Washington', 'value': 'WA'},
                                                               {'label': 'West Virginia', 'value': 'WV'},
                                                               {'label': 'Wisconsin', 'value': 'WI'},
                                                               {'label': 'Wyoming', 'value': 'WY'},
                                                           ],
                                                           value='TX',
                                                           searchable=False,
                                                           className='fuck'
                                                       ),
                                                       html.P('Covid Measurement Metrics to compare'),
                                                       html.Div(className='div-for-dropdown',
                                                                children=[
                                                                    dcc.Dropdown(
                                                                        id='StatePlotPick',
                                                                        options=[
                                                                            {'label': 'Cases', 'value': 'Cases'},
                                                                            {'label': 'New Cases', 'value': 'NewCases'},
                                                                            {'label': 'Deaths',
                                                                             'value': 'Deaths'},
                                                                            {'label': 'Vaccinations', 'value':'Vaccinations'}

                                                                        ],
                                                                        value='NewCases',
                                                                        searchable=False,
                                                                        clearable=False,
                                                                        className='fuck'
                                                                    )
                                                                ],
                                                                style={'color': '#1E1E1E'}),
                                                   ]),
                                          html.P('''Visualising time series with Plotly - Dash'''),
                                          html.P('''Pick one or more states from the dropdown below.'''),
                                      ]
                                      ),

                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          dbc.Row(
                                              [
                                                  # dbc.Col(dbc.Card(
                                                  #     [
                                                  #         dbc.CardHeader(
                                                  #             [
                                                  #                 html.H5("United States")
                                                  #             ]
                                                  #         ),
                                                  #         dbc.CardBody(
                                                  #             [
                                                  #                 html.I(className="fas fa-notes-medical"),
                                                  #                 html.H5("Current Infections", className="card-title"),
                                                  #                 html.H5(
                                                  #                     "123,456,789",
                                                  #                     className="card-title",
                                                  #                 ),
                                                  #             ]
                                                  #         ),
                                                  #     ], color="warning", inverse=True)),
                                                  # dbc.Col(dbc.Card(
                                                  #     [
                                                  #         dbc.CardHeader(
                                                  #             [
                                                  #                 html.H5("United States")
                                                  #             ]
                                                  #         ),
                                                  #         dbc.CardBody(
                                                  #             [
                                                  #                 html.I(className="fas fa-heart-broken"),
                                                  #                 html.H5("Deaths", className="card-title"),
                                                  #                 html.H5(
                                                  #                     "123,456,789",
                                                  #                     className="card-title",
                                                  #                 ),
                                                  #             ]
                                                  #         ),
                                                  #     ], color="danger", inverse=True)),
                                                  # dbc.Col(dbc.Card(
                                                  #     [
                                                  #         dbc.CardHeader(
                                                  #             [
                                                  #                 html.H5("United States")
                                                  #             ]
                                                  #         ),
                                                  #         dbc.CardBody(
                                                  #             [
                                                  #                 html.I(className="fas fa-heart"),
                                                  #                 html.H5("Recovered", className="card-title"),
                                                  #                 html.H5(
                                                  #                     "123,456,789",
                                                  #                     className="card-title",
                                                  #                 ),
                                                  #             ]
                                                  #         ),
                                                  #     ], color="success", inverse=True)),
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
    elif tab == 'tab-6':
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
                                          html.P('The SEIR mathematical model predicts data for parameters related to the COVID-19 virus. In the graphs displayed, predictive data for the Infections, Deaths, and Hospitalized due to the virus are shown. Recently, the model has been adjusted to account for the rapid distribution of the COVID-19 vaccine beginning in late January/Early February. This has affected the late-stage accuracy of the model, as the vaccine has proven to be more effective than predicted in the US population.'),
                                          html.P('Covid Measurement Metrics to compare'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='PredictPick',
                                                           options=[
                                                               {'label': 'predictedInfections', 'value': 'predictedCases'},
                                                               {'label': 'predictedDeaths', 'value': 'predictedDeaths'},
                                                               {'label': 'predictedHospitlization', 'value': 'predictedHospitlization'},
                                                           ],
                                                           value='predictedCases',
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
                                              children= [
                                                  dcc.Loading(
                                                        html.Div(id='MultiPredict',))
                                                     ])
                                      ])
                         ])
            ]
        )


if __name__ == '__main__':
    app.run_server(debug=True)