# -*- coding: utf-8 -*-
"""
"""

import os
import cufflinks

from datapackage import Package

import pandas as pd
import plotly.plotly as py
import plotly.offline as off
import plotly.graph_objs as go
from plotly import tools as tls



p = Package('../angus-datapackages/e-highway/datapackage.json')

types = ['dispatchable-generator', 'volatile-generator',
         'reservoir', 'run-of-river']


l = list()
for t in types:
   l.extend(p.get_resource(t).read(keyed=True))
df = pd.DataFrame.from_dict(l)

df['tech'] = [i[0:-3] for i in df['name']]
buses = [r['name'] for r in p.get_resource('bus').read(keyed=True)]

colors = {
    'pv': 'rgb(255,255,153)',
    'wind': 'rgb(0,191,255)',
    'octg': 'rgb(105,105,105)',
    'biomass': 'rgb(107,142,35)',
    'run-of-river': 'rgb(138,43,226)',
    'reservoir': 'rgb(127,255,212)',
    'demand': 'rgb(51, 51, 0)',
    'import': 'rgb(255, 51, 0)',
    'export': 'rgb(0, 153, 51)',
    'pumped-storage': 'rgb(51, 204, 255)',
    'shortage': 'rgb(255, 0, 102)',
    'excess': 'rgb(51, 102, 153)'}


data= [
    go.Bar(
        marker = {
            'color': colors.get(tech)},
        name=tech,
        x=df.loc[df['tech']==tech, 'bus'],
        y=df.loc[df['tech'] == tech, 'capacity'])
    for tech in df['tech'].unique()]

layout = go.Layout(
    barmode='stack',
    title='Installed capacities',
    yaxis=dict(
        title='Installed capacity in MW',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    )
)

fig = go.Figure(data=data, layout=layout)

off.iplot(fig, filename='e-highway-capacities.html')


###############################################################################

# fig = tools.make_subplots(rows=2, cols=2, subplot_titles=('Plot 1', 'Plot 2',)

p = Package('../angus-datapackages/e-highway/datapackage.json')

connection_names = [r['name'] for r in p.get_resource('transshipment').read(keyed=True)]

# Does only work with bus-centric results
# Plot input and output of buses
path = '../angus-datapackages/e-highway/results/e-highway-X7-simple/sequences/'

data = {}
for f in os.listdir(path):
    idx = pd.IndexSlice
    name = f.strip('.csv')

    prefix = name[:2]

    data[name] = {}
    df = pd.read_csv(
        os.path.join(path, f), sep=';', header=[0,1,2], index_col=0)
    df.index = pd.DatetimeIndex(df.index)

    i = df.loc[:, idx[:, name, 'flow']].copy()
    i.columns = i.columns.droplevel([1, 2])
    i.columns = ['import' if c in connection_names else c[:-3] for c in i.columns]
    i = i.groupby(i.columns, axis=1).sum()

    data[name]['inputs'] = i

    o = df.loc[:, idx[name, :, 'flow']].copy()
    o.columns = o.columns.droplevel([0, 2])
    o.columns = ['export' if c in connection_names else c[:-3] for c in o.columns]
    o = o.groupby(o.columns, axis=1).sum()

    data[name]['outputs'] = o


timeidx = pd.date_range('2050-04-29 00:00:00', '2050-04-29 23:00:00', freq='H')

fig = tls.make_subplots(rows=len(data), cols=2, shared_yaxes=True)
fig['layout'].update(height=5000, width=2000, title='e-highway bus balance')

# Can't set title in subplots, not the way to go, I guess
# https://community.plot.ly/t/different-title-for-different-subplots/4993
row = 1
for name, r in data.items():

    daily_o, daily_i = r['outputs'].loc[timeidx], r['inputs'].loc[timeidx]

    options = {'type': 'scatter', 'fill': 'tonexty', 'showlegend': False,
               'hoverinfo': 'all', 'mode': 'none', 'opacity': 0.5}

    for c in daily_o:
        fig.append_trace(
            {'x': daily_o.index,
             'y': daily_o[c],
             'name': c,
             'fillcolor': colors[c],
             **options}, row, 1)

    for c in r['inputs']:
        fig.append_trace(
            {'x': daily_i.index,
             'y': daily_i[c],
             'name': c,
             'fillcolor': colors[c],
             **options}, row, 2)

    row += 1

off.plot(fig, filename='e-highway-bus-input-output.html')
