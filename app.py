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

statesPC = {'CA':0.002540129,'TX':0.003405907,'FL':0.004601232,'NY':0.005171493,'PA':0.007822734,'IL':0.00794437,
            'OH':0.008551966,'GA':0.009337053,'NC':0.00943323,'MI':0.010033557,'NJ':0.011258255,'GA':0.011640681,
            'WA':0.012997796,'AZ':0.013474545,'MA':0.014506263,'TN':0.01452046,'IN':0.014803952,'MO':0.016256071,
            'MD':0.016513089,'WI':0.017144851,'CO':0.017218464,'MN':0.017676145,'SC':0.019164284,'AL':0.020318876,
            'LA':0.021527052,'KY':0.022335134,'OR':0.023576526,'OK':0.025120686,'CT':0.028113531,'UT':0.030770376,'IA':0.031609948,
            'NV':0.031864801,'AR':0.032997616,'MS':0.033706509,'KS':0.034319387,'NM':0.04747619,'NE':0.051611518,'ID':0.054737144,
            'WV':0.056029095,'HI':0.071072902,'NH':0.073191707,'ME':0.074066338,'MT':0.092543151,'RI':0.094596193,
            'DE':0.101336733,'SD':0.112017582,'ND':0.130666175,'AK':0.136769344,'VT':0.16042429,'WY':0.171724526}

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
                html.P('The percentage of tweets that get categorized as Positive or Negative for the day, the positive and negative value does not sum up to 100%, because the rest of the tweets get categorized as neutral.'),
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
    if type_value == "newCases":
        titleVal = "Daily Cases"
        paraVal = "The daily reporting of new cases from each states. Data collected from Covid Act Now"
    elif type_value == "deaths":
        titleVal = "Cumulative Deaths"
        paraVal = "The cumulative reporting of deaths from each state. Data collected from Covid Act Now"
    elif type_value == "vaccinationsInitiated":
        titleVal = "Cumulative Vaccinations"
        paraVal = "The cumulative reporting of vaccinations done from each state. Data gap is from non reporting days. Data collected from Covid Act Now"
    elif type_value == "newCasesPC":
        titleVal = "Daily New Cases Per 100k people"
        paraVal = "The daily reporting of new cases from each states per 100,000 people. Data collected from Covid Act Now and United States Census Bureau"
    elif type_value == "deathsPC":
        titleVal = "Cumulative Deaths Per 100k people"
        paraVal = "The cumulative reporting of deaths from each state per 100,000 people. Data collected from Covid Act Now and United States Census Bureau"
    else:
        titleVal = "Cumulative Vaccinations Per 100k people"
        paraVal = "The cumulative reporting of vaccinations done from each state. Data gap is from non reporting days. Data collected from Covid Act Now and United States Census Bureau"

    fig6.update_layout(xaxis_title="Days", yaxis_title='Count', title=titleVal, legend_title="States")
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
                    numbers3.append(0)


            stateDictionary[state_value[j]] = date
            stateDictionary[state_value[j] + '-cases'] = numbers4
            stateDictionary[state_value[j]+'-newCases'] = numbers1
            stateDictionary[state_value[j] + '-deaths'] = numbers2
            stateDictionary[state_value[j] + '-vaccinationsInitiated'] = numbers3

        if state_value[j]+'-casesPC' not in stateDictionary:
            blankList1 = []
            for i in stateDictionary[state_value[j] + '-newCases']:
                if i != None:
                    blankList1.append(round(i*statesPC[state_value[j]],2))
                else:
                    blankList1.append(None)
            stateDictionary[state_value[j]+'-newCasesPC'] = blankList1

            blankList2 = []
            for i in stateDictionary[state_value[j] + '-deaths']:
                if i != None:
                    blankList2.append(round(i*statesPC[state_value[j]],2))
                else:
                    blankList2.append(None)
            stateDictionary[state_value[j]+'-deathsPC'] = blankList2

            blankList3 = []
            for i in stateDictionary[state_value[j] + '-vaccinationsInitiated']:
                if i != None:
                    blankList3.append(round(i*statesPC[state_value[j]],2))
                else:
                    blankList3.append(None)
            stateDictionary[state_value[j]+'-vaccinationsInitiatedPC'] = blankList3

        #vaccinationsInitiated
        if type_value == 'vaccinationsInitiated':
            fig6.add_trace(go.Scatter(x=stateDictionary[state_value[j]],y=stateDictionary[state_value[j] + '-' + type_value][330:],mode='lines', name=state_value[j]))
        elif type_value == 'vaccinationsInitiatedPC':
            fig6.add_trace(go.Scatter(x=stateDictionary[state_value[j]],y=stateDictionary[state_value[j] + '-' + type_value][330:], mode='lines',name=state_value[j]))
        else:
            fig6.add_trace(go.Scatter(x=stateDictionary[state_value[j]], y=stateDictionary[state_value[j] + '-' + type_value], mode='lines', name=state_value[j]))

    fig6.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    print(datetime.datetime.now() - a)
    if (5==5):
        return html.Div(
            children=[
                dcc.Graph(id='timeseries',
                          figure=fig6
                          ),
                html.P(paraVal),
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
        go.Scatter(x=xValTotal, y=yValTotal, name="Daily Actual Deaths")
    )
    figC.update_layout(xaxis_title="Date", yaxis_title='Daily Infections Count from COVID-19', title='Forecasted Number of COVID-19 Infections in the US', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    figP.update_layout(xaxis_title="Date", yaxis_title='Cumulative Deaths Count from COVID-19', title='Forecasted Number of Deaths from COVID-19 in the US', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    figH.update_layout(xaxis_title="Date", yaxis_title='Daily Hospitalizations Count from COVID-19', title='Forecasted Number of Hospitalizations due to COVID-19 in the US', showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
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
    if plotPick == "Cases":
        paraVal = "The cumulative cases for the state. Data collected from Covid Act Now"
    elif plotPick == "NewCases":
        paraVal = "The daily reporting of new cases for the state. Data collected from Covid Act Now"
    elif plotPick == "Deaths":
        paraVal = "The cumulative reporting of deaths for the state. Data collected from Covid Act Now"
    else:
        paraVal = "The cumulative reporting of vaccinations done from each state. Data gap is from non reporting days. Data collected from Covid Act Now"
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
                numbers4.append(0)

        stateDictionary[state] = date
        stateDictionary[state+'-cases'] = numbers1
        stateDictionary[state + '-newCases'] = numbers2
        stateDictionary[state + '-deaths'] = numbers3
        stateDictionary[state + '-vaccinationsInitiated'] = numbers4


    new1List = stateDictionary[state + '-newCases']

    # mva1 = [0] * 7
    # mva2 = [0] * 7
    # var1 = 0
    # var2 = 0
    # lastReal = 0
    # lastReal7 = 0
    # for day in range(0,7):
    #     if new1List[day]:
    #         var1 = var1 + new1List[day]
    #         lastReal = new1List[day]
    #     else:
    #         var1 = var1 + lastReal
    #
    # for day in range(7,len(stateDictionary[state])):
    #     mva1.append(var1/7.0)
    #     mva2.append(var2/7.0)
    #     if new1List[day]:
    #         var1 = var1 + new1List[day]
    #         lastReal = new1List[day]
    #         if new1List[day-7]:
    #             var1 = var1 - lastReal7
    #             lastReal7 = new1List[day-7]
    #         else:
    #             var1 = var1 - lastReal7
    #     else:
    #         var1 = var1 + lastReal
    #         if new1List[day-7]:
    #             var1 = var1 - lastReal7
    #             lastReal7 = new1List[day-7]
    #         else:
    #             var1 = var1 - lastReal7

    fig11.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-cases'], mode='lines', name=state))
    fig11.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig12.add_trace(go.Bar(x=stateDictionary[state], y=stateDictionary[state + '-newCases'], name=state+" Daily"))
    #fig12.add_trace(go.Scatter(x=stateDictionary[state], y=mva1, name=state+" 7 Day Average"))
    fig12.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    fig13.add_trace(go.Scatter(x=stateDictionary[state], y=stateDictionary[state + '-deaths'], mode='lines', name=state))
    fig13.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    xOne = stateDictionary[state][330:]
    yOne = stateDictionary[state + '-vaccinationsInitiated'][330:]
    fig14.add_trace(go.Scatter(x=xOne, y=yOne, mode='lines', name=state))
    fig14.update_layout(showlegend=True, xaxis=dict(rangeslider=dict(visible=True)))
    print(stateDictionary[state])
    # fig12.update_layout(
    #     updatemenus=[go.layout.Updatemenu(
    #         type="buttons",
    #         active=1,
    #         buttons=list(
    #             [dict(label='None',
    #                   method='update',
    #                   args=[{'visible': [True, False]},
    #                         {'title': 'None',
    #                          'showlegend': True}]),
    #              dict(label='LineDaily',
    #                   method='update',
    #                   args=[{'visible': [True, True]},
    #                         # the index of True aligns with the indices of plot traces
    #                         {'title': 'LineDaily',
    #                          'showlegend': True}]),
    #              ])
    #     )
    #     ])

    print('TimeA', datetime.datetime.now() - a)
    if(plotPick == "Cases"):
        figPlot = fig11
    elif(plotPick == "NewCases"):
        figPlot = fig12
    elif(plotPick == "Deaths"):
        figPlot = fig13
    else:
        figPlot = fig14

    vac1 = yOne[-2]
    if vac1 == None:
        vac1 = yOne[-3]
    vac2 = yOne[-8]
    if vac2 == None:
        vac2 = yOne[-7]
    vac3 = yOne[-9]
    if vac3 == None:
        vac3 = yOne[-10]
    vac4 = yOne[-15]
    if vac4 == None:
        vac4 = yOne[-16]

    death1 = stateDictionary[state + '-deaths'][-2]
    death2 = stateDictionary[state + '-deaths'][-8]
    death3 = stateDictionary[state + '-deaths'][-9]
    death4 = stateDictionary[state + '-deaths'][-15]
    if death1 == None:
        death1 = stateDictionary[state + '-deaths'][-3]
    if death2 == None:
        death2 = stateDictionary[state + '-deaths'][-7]
    if death3 == None:
        death3 = stateDictionary[state + '-deaths'][-10]
    if death4 == None:
        death4 = stateDictionary[state + '-deaths'][-16]

    sumHH = 0
    for i in stateDictionary[state + '-newCases'][-15:-8]:
        if i != None:
            sumHH = sumHH + i

    sumGG = 0
    for i in stateDictionary[state + '-newCases'][-8:-1]:
        if i != None:
            sumGG = sumGG + i

    caseGG=sumGG/7
    caseHH =sumHH/7

    if caseGG == caseHH:
        caseChangeString = "0%"
    else:
        caseChange = ((caseGG - caseHH) / caseHH) * 100.0
        if caseChange > 0:
            caseChangeString = "+"+str(round(caseChange, 2))+"%"
        else:
            caseChangeString = str(round(caseChange, 2)) + "%"


    deathGG =(death1-death2)/7
    deathHH =(death3-death4)/7
    if deathGG == deathHH or deathGG == 0 or deathHH == 0:
        deathChangeString = "0%"
    else:
        deathChange = ((deathGG - deathHH) / deathHH) * 100.0
        if deathChange > 0:
            deathChangeString = "+"+str(round(deathChange, 2))+"%"
        else:
            deathChangeString = str(round(deathChange, 2)) + "%"

    vacGG =(vac1-vac2)/7
    vacHH =(vac3-vac4)/7

    if vacGG == vacHH:
        vacChangeString = "0%"
    else:
        vacChange = ((vacGG - vacHH) / vacHH) * 100.0
        if vacChange > 0:
            vacChangeString = "+"+str(round(vacChange, 2))+"%"
        else:
            vacChangeString = str(round(vacChange, 2)) + "%"

    return html.Div(
        children=[
            dbc.Row(
                [
                    dbc.Col(dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(state)
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    html.I(className="fas fa-notes-medical"),
                                    html.H6("Daily Infection, Weekly Average", className="card-title"),
                                    html.H6("Change: " + caseChangeString, className="card-title", ),
                                    html.H6("Current: " + str(round(caseGG)), className="card-title", ),
                                    html.H6("Last Week: "+str(round(caseHH)), className="card-title", ),
                                ]
                            ),
                        ], color="warning", inverse=True)),
                    dbc.Col(dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(state)
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    html.I(className="fas fa-heart-broken"),
                                    html.H6("Daily Deaths, Weekly Average", className="card-title"),
                                    html.H6("Change: " + deathChangeString, className="card-title", ),
                                    html.H6("Current: " + str(round(deathGG)), className="card-title", ),
                                    html.H6("Last Week: "+str(round(deathHH)), className="card-title", ),
                                ]
                            ),
                        ], color="danger", inverse=True)),
                    dbc.Col(dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(state)
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    html.I(className="fas fa-heart"),
                                    html.H6("Daily Vaccinations, Weekly Average", className="card-title"),
                                    html.H6("Change: " + vacChangeString, className="card-title", ),
                                    html.H6("Current: " + str(round(vacGG)), className="card-title", ),
                                    html.H6("Last Week: "+str(round(vacHH)), className="card-title", ),
                                ]
                            ),
                        ], color="success", inverse=True)),
                ],
                className="mb-4", justify="center", align="center", style={'text-align': 'center'}
            ),
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                      figure=figPlot
                      ),
            html.P(paraVal),
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
                                                               {'label': 'Daily Cases', 'value': 'newCases'},
                                                               {'label': 'Cumulative Deaths', 'value': 'deaths'},
                                                               {'label': 'Cumulative Vaccinations', 'value': 'vaccinationsInitiated'},
                                                               {'label': 'Daily Cases Per Capita', 'value': 'newCasesPC'},
                                                               {'label': 'Cumulative Deaths Per Capita', 'value': 'deathsPC'},
                                                               {'label': 'Cumulative Vaccinations Per Capita','value': 'vaccinationsInitiatedPC'},

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
                                          dcc.Loading(
                                          html.Div(id='MultiPlots',
                                                   )
                                          ),
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
                                          html.H2('Dash - Covid Model Forecasting'),
                                          html.P('The SEIR mathematical model predicts data for parameters related to the COVID-19 virus. In the graphs displayed, predictive data for the Infections, Deaths, and Hospitalized due to the virus are shown. Recently, the model has been adjusted to account for the rapid distribution of the COVID-19 vaccine beginning in late January/Early February. This has affected the late-stage accuracy of the model, as the vaccine has proven to be more effective than predicted in the US population.'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(
                                                           id='PredictPick',
                                                           options=[
                                                               {'label': 'Forecasted Infections (past and upcoming 2 weeks)', 'value': 'predictedCases'},
                                                               {'label': 'Forecasted Deaths (past and upcoming 2 weeks)', 'value': 'predictedDeaths'},
                                                               {'label': 'Forecasted Hospitlization (past and upcoming 2 weeks)', 'value': 'predictedHospitlization'},
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