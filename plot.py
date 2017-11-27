# container for all plotting functions, maybe classes
import plotly.graph_objs as go
import plotly
import pandas as pd
import cufflinks as cf
import numpy as np
from collections import OrderedDict

# =============================================================================
# ToDos:
# 1. dynamische Farben: Es wäre cool den plots automatisch Farben zuzuweisen
# und das nicht zufällig zu machen. WEnn eine Spalte bspw. "biomass" enthält soll
# sie grün geplottet werden.
# 2. der dispatchplot zeigt beim mouseover die gestapelten Werte an. Sprich wenn
# Wind 5 GW und Solar 2 GW hat werden bei Wind 5 GW angezeigt und bei Solar 7 GW. 
# Eine Idee habe ich vom letzten Beispiel von folgendem Link, kann es aber nicht
# auf das Problem umsetzen. https://plot.ly/python/filled-area-plots/#stacked-area-chart-with-original-values
# 3. Die verwendeten Technologien im SQ Szenaro kommen teilweise mehrmals vor
# (lignite_0, lignite_1, etc..). Das sollte man für die plots zu einer Technologie
# zusammenfassen, macht sie sonst sehr unübersichtlich.
# =============================================================================

def plot_prices(results):
    """

    Returns
    -------
    str: Plotly div.
    """

    prices = results.slice_by(bus_label='DE_bus_el', type='other', obj_label='duals')
    data = [go.Scatter(x=prices.index.get_level_values(3), y=prices['val'])]
    div = plotly.offline.plot(data, include_plotlyjs=False, output_type='div')
    return div


def get_countrycodes_techs(results):
    """

    Returns
    -------
    str: countrycodes, techs.
    """
    # get countries used in scenario
    countrycodes = results.index.get_level_values(0).unique().str.split('_', 1)
    countrycodes = set([cc[0] for cc in countrycodes])
    countrycodes.remove('GL')

    # get technologies used in scenario. drop entries with powerlines, resources,
    # and duals
    techs = results.index.get_level_values(2).unique()
    techs = techs[techs.str.contains('powerline') == False]
    techs = techs[techs.str.contains('resource') == False]
    techs = techs[techs.str.contains('duals') == False]
    for cc in countrycodes:
        techs = techs.str.lstrip(cc)
    techs = list(techs.str.lstrip('_').unique())
    return countrycodes, techs

def get_hourly_dispatch(countrycodes, techs, results):
    """

    Returns
    -------
    dict: hourly dispatch for each country
    """

    timelines = {}
    for cc in countrycodes:
        #plots = {}
        timelines[cc] = pd.DataFrame(index=results.index.get_level_values(3).unique())
        for t in techs:
            try:
                timelines[cc][t] = results.slice_unstacked(obj_label=cc + '_' + t,
                        type='to_bus', bus_label=cc + '_bus_el', formatted=True)
            except KeyError:
                continue
            except ValueError:
                continue
    return timelines

def get_transmission(results):
    """

    Returns
    -------
    DataFrame: transmission for each line. Negative values mean
    from second to first when first_second
    """
    powerlines = results.index.get_level_values(2).unique()
    powerlines = powerlines[powerlines.str.contains('powerline') == True]
    transmission = pd.DataFrame(index=results.index.get_level_values(3).unique(),
                                columns=powerlines)
    for p in powerlines:
        transmission[p] = results.slice_unstacked(obj_label=p,
                        type='from_bus', formatted=True)
    transmission.columns = transmission.columns.str.replace('_powerline', '')
    split = list(transmission.columns.str.split('_'))
    for i in range(0, len(split)):
        try:
            if list([split[i][1], split[i][0]]) not in split:
                split.remove(split[i])
        except IndexError:
            break
    join = []
    for i in range(0, len(split)): 
        join.append("_".join([split[i][0], split[i][1]]))
        join.append("_".join([split[i][1], split[i][0]]))
    join = list(OrderedDict.fromkeys(join))
    for i in range(0, len(join), 2):
        transmission[join[i]] = transmission[join[i]] - transmission[join[i+1]]
        transmission = transmission.drop(join[i+1], axis=1)
    return transmission
    

def plot_hourly_dispatch(timelines):
    """

    Returns
    -------
    str: Plotly div.
    """
    div = pd.Series(index=timelines.keys())
    for cc in timelines.keys():
        timelines[cc] = timelines[cc].loc[:, (timelines[cc] != 0).any(axis=0)]
        # two lines below work, but do't show stacked numbers instead of single numbers when hovered with mouse.
        # compare last entry in: https://plot.ly/python/filled-area-plots/#stacked-area-chart-with-original-values 
        try:
            fig = timelines[cc].iplot(kind='area', fill=True, asFigure=True)
            div[cc] = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        except:
            print(cc + ' could not be plotted.')
            continue
        
# =============================================================================
#         #trying to show correct numbers when hovering with mouse. taken from link above
#         for i in range(0, len(timelines[cc].ix[0])):
#             y_txt = [str(y0) for y0 in timelines[cc].ix[:, i]]
#             plots[str(i)] = go.Scatter(x=timelines[cc].index, y=timelines[cc].ix[:, i], text=y_txt, hoverinfo='x+text')
#             
#         y_txt = [str(y1) for y1 in timelines[cc].ix[:, 1]]
#         plots[str(1)] = [go.Scatter(x=timelines[cc].index, y=timelines[cc].ix[:, 1], text=y_txt, hoverinfo='x+text')]
#         
#         y_txt = [str(y0) for y0 in timelines[cc].ix[:, 0]]
#         p0 = [go.Scatter(x=timelines[cc].index, y=timelines[cc].ix[:, 0], text=y_txt, hoverinfo='x+text')]
#         y_txt = [str(y1) for y1 in timelines[cc].ix[:, 1]]
#         p1 = [go.Scatter(x=timelines[cc].index, y=timelines[cc].ix[:, 1], text=y_txt, hoverinfo='x+text')]
#         data = Data([p0, p1])
#         plotly.offline.plot(data, filename='timeline')
#         #fig = go.Figure(plots)
#         plotly.offline.plot(plots, filename='timeline')
# =============================================================================
    return div
        
def plot_yearly_sums(timelines, techs):
    """

    Returns
    -------
    str: Plotly div.
    """
    countrycodes = timelines.keys()
    sums = pd.DataFrame(index=techs, columns=countrycodes)
    for cc in countrycodes:
        sums[cc] = timelines[cc].sum()
    sums = sums.T
    fig = sums.iplot(kind='bar', barmode='stack', asFigure=True)
    div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    return div

def plot_transmission(transmission, countrycodes):
    """

    Returns
    -------
    str: Plotly div.
    """
    
    N = len(countrycodes)
    x_points = np.random.uniform(-N/2, N/2, N)
    y_points = np.random.uniform(-N/2, N/2, N)
    points = np.array([x_points, y_points, list(countrycodes)])
    lines = np.empty(shape=(2, len(transmission.columns)*3))
    lines_text = np.empty(shape=(2, len(transmission.columns)))
    text = []
    i = 0
    j = 0
    for join in transmission.columns:
        #lines[0]=x, lines[1]=y, i=x0/y0, i+1=x1/y1, i+2 to get gaps
        split = join.split('_')
        lines[0][i] = float(points[0][np.where(points==split[0])[1]][0])
        lines[0][i+1] = float(points[0][np.where(points==split[1])[1]][0])
        lines[1][i] = float(points[1][np.where(points==split[0])[1]][0])
        lines[1][i+1] = float(points[1][np.where(points==split[1])[1]][0])
        lines[0][i+2] = None
        lines[1][i+2] = None
        lines_text[0][j] = 0.5*(lines[0][i]+lines[0][i+1])
        lines_text[1][j] = 0.5*(lines[1][i]+lines[1][i+1])
        text.append(join + ': ' + str(round(transmission[join].sum(),0)))
        i += 3
        j += 1
        
    # Create a trace
    trace1 = go.Scatter(
        x=points[0],
        y=points[1],
        mode='markers',
        marker=dict(size='16'),
        text=points[2],
        hoverinfo='text'
    )
        
    trace2 = go.Scatter(
        x=lines[0],
        y=lines[1],
        marker=dict(size='16'),
        text='',
        hoverinfo='text'
    )
    
    trace3 = go.Scatter(
        x=lines_text[0],
        y=lines_text[1],
        mode='markers',
        marker=dict(opacity=0.),
        text=text,
        hoverinfo='text'
    )
    
    data = [trace1, trace2, trace3]
    div = plotly.offline.plot(data, include_plotlyjs=False, output_type='div')
    return div

    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    