# -*- coding: utf-8 -*-
""" renpass

Usage:
  renpass.py [options] DATAPACKAGE
  renpass.py -h | --help | --version

Examples:

  renpass_gis_main.py -o glpk path/to/datapackage.json

Arguments:

  DATAPACKAGE                valid datapackage with input data

Options:

  -h --help                  Show this screen and exit.
  -o --solver=SOLVER         Solver to be used. [default: cbc]
     --output-directory=DIR  Directory to write results to. [default: results]
     --version               Show version.
     --results=RESULTS       How should results be saved [default: datapackage]
  -s --safe                  If argument --safe is set, results will not be
                             overwritten
  -d --debug                 If set debug mode is turned on
     --t_start=T_START       Start timestep of simulation [default: 0]
     --t_end=T_END           End timestep of simulation, default is last
                             timestep of datapackage timeindex [default: -1]
"""

import os
import logging
import pandas as pd

from datapackage import Package
from datetime import datetime

import facades

from oemof.tools import logger
from oemof.solph import Model, EnergySystem, Bus
from oemof.outputlib import processing, views

try:
    from docopt import docopt
except ImportError:
    print("Unable to load docopt. Is docopt installed?")


###############################################################################

def stopwatch():
    if not hasattr(stopwatch, 'now'):
        stopwatch.now = datetime.now()
        return None
    last = stopwatch.now
    stopwatch.now = datetime.now()
    return str(stopwatch.now-last)[0:-4]


def create_energysystem(datapackage, **arguments):
    """Creates the energysystem.

    Parameters
    ----------
    datapackage: str
        path to datapackage metadata file in JSON format
    **arguments : key word arguments
        Arguments passed from command line
    """

    es = EnergySystem.from_datapackage(
        arguments['DATAPACKAGE'],
        attributemap={
            facades.Demand: {'demand-profiles': 'profile'},
            facades.Generator: {"generator-profiles": "profile"},
            facades.RunOfRiver: {"run-of-river-inflows": "inflow"}},
        typemap={
            'bus': facades.Hub,
            'extraction-turbine': facades.ExtractionTurbine,
            'demand': facades.Demand,
            'generator': facades.Generator,
            'storage': facades.Storage,
            'reservoir': facades.Reservoir,
            'backpressure': facades.Backpressure,
            'connection': facades.Connection,
            'conversion': facades.Conversion,
            'runofriver': facades.RunOfRiver})


    end = es.timeindex.get_loc(es.timeindex[int(arguments['--t_end'])]) + 1

    es.timeindex = es.timeindex[int(arguments['--t_start']):end]

    return es


def compute(es=None, **arguments):
    """Creates the optimization model, solves it and writes back results to
    energy system object

    Parameters
    ----------
    es : :class:`oemof.solph.network.EnergySystem` object
        Energy system holding nodes, grouping functions and other important
        information.
    **arguments : key word arguments
        Arguments passed from command line
    """

    m = Model(es)

    logging.info('Model creation time: ' + stopwatch())

    #m.receive_duals()
    if arguments['--debug']:
        filename  = 'renpass_model.lp'
        logging.info('Writing lp-file to {}.'.format(filename))
        m.write(filename,
                io_options={'symbolic_solver_labels': True})

    m.solve(solver=arguments['--solver'], solve_kwargs={'tee': True})

    logging.info('Optimization time: ' + stopwatch())

    return m

def links(es):
    """
    """
    buses = [n for n in es.nodes if isinstance(n, facades.Connection)]
    links = list()
    for b in buses:
        for i in b.inputs:
            for o in b.outputs:
                if o != i:
                    links.append((i, o))
    return links


def write_results(es, m, p, **arguments):
    """Write results to CSV-files

    Parameters
    ----------
    es : :class:`oemof.solph.network.EnergySystem` object
        Energy system holding nodes, grouping functions and other important
        information.
    m : A solved :class:'oemof.solph.models.Model' object for dispatch or
     investment optimization
    **arguments : key word arguments
        Arguments passed from command line
    p: datapackage.Package instance of the input datapackage
    """
    # output: create pandas dataframe with results

    results = processing.results(m)

    # postprocessing: write complete result dataframe to file system

    if not os.path.isdir(arguments['--output-directory']):
        os.mkdir(arguments['--output-directory'])

    output_base_directory = arguments['--output-directory']

    date = datetime.now().strftime("%Y-%m-%d %H-%M-%S").replace(' ', '_')

    modelname = p.descriptor['name'].replace(' ', '_')

    logging.info('Exporting result object to CSV.')

    # add regular optimization results
    nodes = sorted(set([item
                        for tup in results.keys()
                        for item in tup]))
    nodes = [n for n in nodes if isinstance(n, (Bus, facades.Storage))]

    package_root_directory = os.path.join(output_base_directory, modelname)

    for n in nodes:
        node_data = views.node(results, str(n), multiindex=True)

        # if 'scalars' in node_data:
        #     node_data['scalars'].to_excel(writer, sheet_name=str(n)+'_scalars')

        node_path = os.path.join(package_root_directory, 'data', str(n))

        if not os.path.exists(node_path):
            os.makedirs(node_path)
        else:
            if arguments['--safe']:
                # TODO: replace this with a atrifical result name to store
                # results at different location.
                raise ValueError('Resultpath {} already exists!'.format(
                                                                    node_path))
            else:
                logging.warning(('Resultpath {} already exist' +
                                 ' overwriting results').format(node_path))

        if 'sequences' in node_data:
            # TODO: Fix storage SOC
            if str(n) in node_data['sequences'].columns.get_level_values(1):
                production = node_data['sequences'].\
                    loc[:, (slice(None), str(n), 'flow')]
                production.columns = production.columns.droplevel([1, 2])
                production.to_csv(os.path.join(node_path, 'production.csv'),
                                  sep=";")

            if str(n) in node_data['sequences'].columns.get_level_values(0):
                consumption = node_data['sequences'].\
                    loc[:, (str(n), slice(None), 'flow')]
                consumption.columns = consumption.columns.droplevel([0, 2])
                consumption.to_csv(os.path.join(node_path, 'consumption.csv'),
                                           sep=";")

    # TODO prettify / complete package (meta-data) creation

    if arguments['--results'] == 'datapackage':
        # results package (rp)
        rp = Package()
        rp.infer(os.path.join(package_root_directory, 'data', '**/*.csv'))
        rp.descriptor['description'] = "Model results from renpass with version..."
        rp.descriptor['name'] = modelname + '-results'
        rp.commit()
        rp.save(os.path.join(package_root_directory, 'datapackage.json'))

    return True



def main(**arguments):
    """
    """
    logging.info('Starting renpass!')

    stopwatch()

    p = Package(arguments['DATAPACKAGE'])

    # create energy system and pass nodes
    es = create_energysystem(arguments['DATAPACKAGE'], **arguments)

    # create optimization model and solve it
    m = compute(es=es, **arguments)

    # write results in output directory
    write_results(es, m=m, p=p, **arguments)

    logging.info('Done! \n Check the results')

    return



###############################################################################

if __name__ == '__main__':
    arguments = docopt(__doc__, version='renpass v0.2')
    logger.define_logging()
    main(**arguments)
