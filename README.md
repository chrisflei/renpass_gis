The application renpassG!S stands for (r)enewable (en)ergy (pa)thway (s)imulation (s)ystem capable of working with data
from geographic information systems (GIS).
It is based on the original idea of `renpass <http://www.renpass.eu>`_ and based on
the `Open Energy Modelling Framework (oemof) <https://github.com/oemof/oemof>`_.

This documentation is meant to explain the basic functionality and is structured as follows:

.. contents::
    :depth: 1
    :local:
    :backlinks: top
.. sectnum::


Overview
========

renpassG!S is an easy-to-use application designed to model the cost-minimal dispatch of energy supply systems.
Technically speaking, it is a so-called numerical partial equilibrium model of a liberalised electricity market often referred to as fundamental model.
Making use of the broad functionality of `oemof <https://github.com/oemof/oemof>`_, the application enables the user to calculate easy-to-understand energy system scenarios
for different regions in spreadsheet format (CSV), optimizing the power plant dispatch at minimum costs.
Results are exported into spreadsheet format as well an can be easily accessed using suitable software such as LibreOffice Calc or Microsoft Excel.

The general functionality can be derived from the following figure:

.. image:: /documents/model_overview_renpass_gis_en.png
    :alt: renpassG!S model model overview
    :align: center
    :width: 100%


Currently, it is developed and maintained at the Center for Sustainable Energy Systems (Zentrum für nachhaltige Energysysteme (ZNES)) in Flensburg.
As there are currently some licensing issues concerning the scenario data, this repository only provides the application code.
For questions on the data, you can use our `contact details <#contact>`_ below.


Application Examples
====================

The model has been used in different research projects.
One application was to model future scenarios of the power plant dispatch
and day-ahead market price formation in Germany and its interconnected neighbor
countries based on operational and marginal costs and the assumption of an inflexible electricity demand.
The following figures show some impressions of possible outcomes.

Hourly power plant dispatch for a week in January
-------------------------------------------------

.. image:: /documents/renpass_gis_dispatch.png
    :alt: power plant dispatch
    :align: center
    :width: 100%

Day-ahead market price formation for a week in May/June
-------------------------------------------------------------------

.. image:: /documents/renpass_gis_prices.png
    :alt: wholesale market price formation
    :align: center
    :width: 100%

Annual production per energy carrier for two selected scenarios
-------------------------------------------------------------------

.. image:: /documents/renpass_gis_annual_production.png
    :alt: annual production
    :align: center
    :width: 100%

Diurnal pumped-storage dispatch in Norway for a selected scenario
-------------------------------------------------------------------

.. image:: /documents/renpass_gis_pumped_hydro.png
    :alt: pump
    :align: center
    :width: 100%


Currently, a similar spin-off model is adapted to the requirements of the Middle East and North Africa
(MENA) region to model possible pathways for the future electricity generation based on a high share of
renewables.

Installation
============

renpassG!S is build within `oemof <https://github.com/oemof/oemof>`_ and works with the current stable version (v.0.1).
Please follow the installation guidelines in the `documentation <https://github.com/oemof/oemof#documentation>`_.

If oemof has been installed successfully (including a suitable solver), the application can be run from the directory.
Just clone this repository using:

.. code:: bash

    git clone https://github.com/znes/renpass_gis.git


Usage
=====

Energy supply systems can be modelled via oemof's `datapackage-reader` functionality
and so called oemof `facades`. Facades allow an easy reduced, energy specific way
to access the generic oemof solph library.
To see how it work check out the example folder.

Once the energy supply systems have been modelled, the application script can be run from the command line:

General usage:

.. code:: bash

    renpass_gis_main.py [options] DATAPACKAGE

Getting help:

.. code:: bash

    renpass_gis_main.py -h

Example usage with another solver (standard is `CBC <https://projects.coin-or.org/Cbc>`_):

.. code:: bash

    renpass_gis_main.py -o gurobi path/to/datapackage.json

Per default, all result files are written back into the subfolder *results*.


Contribution
============

We adhere strictly to the `oemof developer rules <http://oemof.readthedocs.io/en/stable/developing_oemof.html>`_.
For any questions concerning the contribution, you can use our `contact details <#contact>`_ below.


Contact
=======

If you have any questions or want to contribute, feel free to contact us!

For questions, bugs, or possible improvements please create an `issue <https://github.com/znes/renpass_gis/issues>`_.

For all other concerns, please write us an e-mail:

* Simon Hilpert  (University of Flensburg): <simon.hilpert(at)uni-flensburg.de>

* Martin Söthe (University of Flensburg): <martin.soethe(at)uni-flensburg.de>

Credits
=======

Oemof and renpassG!S are community projects and have been realised in collaborative work.
We therefore thank all people who contributed to the framework and the scenario development,
and in particular the following people for their contributions to this first version of renpassG!S:

* Cord Kaldemeyer for the renpass_gis v0.1
* All oemof developers
* All people at the Center for Sustainable Energy Systems (ZNES) Flensburg

Citation
============

We have an `entry <http://osf.io/kp4mh>`_ in the `Open Science Network <https://osf.io>`_ which can be used.
