xbbg
====

Bloomberg data toolkit for humans

============== ======================
Latest Release |pypi|
\              |version|
\              |download|
Docs           |docs|
Build          |travis|
Coverage       |codecov|
Quality        |codacy|
\              |codeFactor|
\              |codebeat|
License        |license|
\              |lic_check|
Release        |release|
Chat           |chat|
============== ======================

Features
========

Below are main features. Jupyter notebook examples can be found here_.

- Excel compatible inputs
- Straightforward intraday bar requests
- Subscriptions

Requirements
============

- Bloomberg C++ SDK version 3.12.1 or higher

    - `Bloomberg API Library`_

    - Downlaod C++ Experimental Release (for latest python API version ``3.14.0``, this can only be downloaded thru ``WAPI<GO>`` in terminal).

    - Copy ``blpapi3_32.dll`` and ``blpapi3_64.dll`` under ``bin`` folder to Bloomberg installation folder ``blp/DAPI``

- Bloomberg Open API (need to install manually as shown below)

- numpy, pandas, ruamel.yaml and pyarrow

.. _pdblp: https://github.com/matthewgilbert/pdblp
.. _download: https://bloomberg.bintray.com/BLPAPI-Experimental-Generic/blpapi_cpp_3.12.2.1-linux.tar.gz
.. _here: https://colab.research.google.com/drive/1YVVS5AiJAQGGEECmOFAb7DNQZMOHdXLR

Installation
============

.. code-block:: console

   pip install blpapi --index-url=https://bloomberg.bintray.com/pip/simple
   pip install xbbg

What's New
==========

*0.6.0* - Speed improvements and tick data availablity

*0.5.0* - Rewritten library to add subscription, BEQS, simplify interface and remove dependency of `pdblp`

*0.1.22* - Remove PyYAML dependency due to security vulnerability

*0.1.17* - Add ``adjust`` argument in ``bdh`` for easier dividend / split adjustments

Tutorial
========

.. code-block:: python

    In[1]: from xbbg import blp

Basics
------

``BDP`` example:

.. code-block:: python

    In[2]: blp.bdp(tickers='NVDA US Equity', flds=['Security_Name', 'GICS_Sector_Name'])
    Out[2]:
                   security_name        gics_sector_name
    NVDA US Equity   NVIDIA Corp  Information Technology

``BDP`` with overrides:

.. code-block:: python

    In[3]: blp.bdp('AAPL US Equity', 'Eqy_Weighted_Avg_Px', VWAP_Dt='20181224')
    Out[3]:
                    eqy_weighted_avg_px
    AAPL US Equity               148.75

``BDH`` example:

.. code-block:: python

    In[4]: blp.bdh(
      ...:     tickers='SPX Index', flds=['High', 'Low', 'Last_Price'],
      ...:     start_date='2018-10-10', end_date='2018-10-20',
      ...: )
    Out[4]:
               SPX Index
                    High      Low Last_Price
    2018-10-10  2,874.02 2,784.86   2,785.68
    2018-10-11  2,795.14 2,710.51   2,728.37
    2018-10-12  2,775.77 2,729.44   2,767.13
    2018-10-15  2,775.99 2,749.03   2,750.79
    2018-10-16  2,813.46 2,766.91   2,809.92
    2018-10-17  2,816.94 2,781.81   2,809.21
    2018-10-18  2,806.04 2,755.18   2,768.78
    2018-10-19  2,797.77 2,760.27   2,767.78

``BDH`` example with Excel compatible inputs:

.. code-block:: python

    In[4]: blp.bdh(
      ...:     tickers='SHCOMP Index', flds=['High', 'Low', 'Last_Price'],
      ...:     start_date='2018-09-26', end_date='2018-10-20',
      ...:     Per='W', Fill='P', Days='A',
      ...: )
    Out[4]:
               SHCOMP Index
                       High      Low Last_Price
    2018-09-28     2,827.34 2,771.16   2,821.35
    2018-10-05     2,827.34 2,771.16   2,821.35
    2018-10-12     2,771.94 2,536.66   2,606.91
    2018-10-19     2,611.97 2,449.20   2,550.47

``BDH`` without adjustment for dividends and splits:

.. code-block:: python

    In[5]: blp.bdh(
      ...:     'AAPL US Equity', 'Px_Last', '20140605', '20140610',
      ...:     CshAdjNormal=False, CshAdjAbnormal=False, CapChg=False
      ...: )
    Out[5]:
               AAPL US Equity
                      Px_Last
    2014-06-05         647.35
    2014-06-06         645.57
    2014-06-09          93.70
    2014-06-10          94.25

``BDH`` adjusted for dividends and splits:

.. code-block:: python

    In[6]: blp.bdh(
      ...:     'AAPL US Equity', 'Px_Last', '20140605', '20140610',
      ...:     CshAdjNormal=True, CshAdjAbnormal=True, CapChg=True
      ...: )
    Out[6]:
               AAPL US Equity
                      Px_Last
    2014-06-05          85.45
    2014-06-06          85.22
    2014-06-09          86.58
    2014-06-10          87.09

``BDS`` example:

.. code-block:: python

    In[7]: blp.bds('AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20180101', DVD_End_Dt='20180531')
    Out[7]:
                   declared_date     ex_date record_date payable_date  dividend_amount dividend_frequency dividend_type
    AAPL US Equity    2018-05-01  2018-05-11  2018-05-14   2018-05-17             0.73            Quarter  Regular Cash
    AAPL US Equity    2018-02-01  2018-02-09  2018-02-12   2018-02-15             0.63            Quarter  Regular Cash

Intraday bars ``BDIB`` example:

.. code-block:: python

    In[8]: blp.bdib(ticker='BHP AU Equity', dt='2018-10-17').tail()
    Out[8]:
                              BHP AU Equity
                                       open  high   low close   volume num_trds
    2018-10-17 15:56:00+11:00         33.62 33.65 33.62 33.64    16660      126
    2018-10-17 15:57:00+11:00         33.65 33.65 33.63 33.64    13875      156
    2018-10-17 15:58:00+11:00         33.64 33.65 33.62 33.63    16244      159
    2018-10-17 15:59:00+11:00         33.63 33.63 33.61 33.62    16507      167
    2018-10-17 16:10:00+11:00         33.66 33.66 33.66 33.66  1115523      216

Above example works because 1) ``AU`` in equity ticker is mapped to ``EquityAustralia`` in
``markets/assets.yml``, and 2) ``EquityAustralia`` is defined in ``markets/exch.yml``.
To add new mappings, define ``BBG_ROOT`` in sys path and add ``assets.yml`` and
``exch.yml`` under ``BBG_ROOT/markets``.

Intraday bars within market session:

.. code-block:: python

    In[9]: blp.bdib(ticker='7974 JT Equity', dt='2018-10-17', session='am_open_30').tail()
    Out[9]:
                              7974 JT Equity
                                        open      high       low     close volume num_trds
    2018-10-17 09:27:00+09:00      39,970.00 40,020.00 39,970.00 39,990.00  10800       44
    2018-10-17 09:28:00+09:00      39,990.00 40,020.00 39,980.00 39,980.00   6300       33
    2018-10-17 09:29:00+09:00      39,970.00 40,000.00 39,960.00 39,970.00   3300       21
    2018-10-17 09:30:00+09:00      39,960.00 40,010.00 39,950.00 40,000.00   3100       19
    2018-10-17 09:31:00+09:00      39,990.00 40,000.00 39,980.00 39,990.00   2000       15

Corporate earnings:

.. code-block:: python

    In[10]: blp.earning('AMD US Equity', by='Geo', Eqy_Fund_Year=2017, Number_Of_Periods=1)
    Out[10]:
                     level    fy2017  fy2017_pct
    Asia-Pacific      1.00  3,540.00       66.43
        China         2.00  1,747.00       49.35
        Japan         2.00  1,242.00       35.08
        Singapore     2.00    551.00       15.56
    United States     1.00  1,364.00       25.60
    Europe            1.00    263.00        4.94
    Other Countries   1.00    162.00        3.04

Dividends:

.. code-block:: python

    In[11]: blp.dividend(['C US Equity', 'MS US Equity'], start_date='2018-01-01', end_date='2018-05-01')
    Out[11]:
                    dec_date     ex_date    rec_date    pay_date  dvd_amt dvd_freq      dvd_type
    C US Equity   2018-01-18  2018-02-02  2018-02-05  2018-02-23     0.32  Quarter  Regular Cash
    MS US Equity  2018-04-18  2018-04-27  2018-04-30  2018-05-15     0.25  Quarter  Regular Cash
    MS US Equity  2018-01-18  2018-01-30  2018-01-31  2018-02-15     0.25  Quarter  Regular Cash

-----

*New in 0.1.17* - Dividend adjustment can be simplified to one parameter ``adjust``:

- ``BDH`` without adjustment for dividends and splits:

.. code-block:: python

    In[12]: blp.bdh('AAPL US Equity', 'Px_Last', '20140606', '20140609', adjust='-')
    Out[12]:
               AAPL US Equity
                      Px_Last
    2014-06-06         645.57
    2014-06-09          93.70

- ``BDH`` adjusted for dividends and splits:

.. code-block:: python

    In[13]: blp.bdh('AAPL US Equity', 'Px_Last', '20140606', '20140609', adjust='all')
    Out[13]:
               AAPL US Equity
                      Px_Last
    2014-06-06          85.22
    2014-06-09          86.58

Data Storage
------------

If `BBG_ROOT` is provided in `os.environ`, data can be saved locally.
By default, local storage is preferred than Bloomberg for all queries.

Noted that local data usage must be compliant with Bloomberg Datafeed Addendum
(full description in `DAPI<GO>`):

    To access Bloomberg data via the API (and use that data in Microsoft Excel),
    your company must sign the 'Datafeed Addendum' to the Bloomberg Agreement.
    This legally binding contract describes the terms and conditions of your use
    of the data and information available via the API (the "Data").
    The most fundamental requirement regarding your use of Data is that it cannot
    leave the local PC you use to access the BLOOMBERG PROFESSIONAL service.

.. |pypi| image:: https://img.shields.io/pypi/v/xbbg.svg
    :target: https://badge.fury.io/py/xbbg
.. |version| image:: https://img.shields.io/pypi/pyversions/xbbg.svg
    :target: https://badge.fury.io/py/xbbg
.. |travis| image:: https://img.shields.io/travis/alpha-xone/xbbg/master.svg?logo=travis&label=Travis%20CI
    :target: https://travis-ci.com/alpha-xone/xbbg
    :alt: Travis CI
.. |azure| image:: https://dev.azure.com/alpha-xone/xbbg/_apis/build/status/alpha-xone.xbbg
    :target: https://dev.azure.com/alpha-xone/xbbg/_build
    :alt: Azure Pipeline
.. |codecov| image:: https://codecov.io/gh/alpha-xone/xbbg/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/alpha-xone/xbbg
    :alt: Codecov
.. |docs| image:: https://readthedocs.org/projects/xbbg/badge/?version=latest
    :target: https://xbbg.readthedocs.io/
.. |codefactor| image:: https://www.codefactor.io/repository/github/alpha-xone/xbbg/badge
   :target: https://www.codefactor.io/repository/github/alpha-xone/xbbg
   :alt: CodeFactor
.. |codacy| image:: https://api.codacy.com/project/badge/Grade/2ec89be198cf4689a6a6c6407b0bc965
   :target: https://www.codacy.com/app/alpha-xone/xbbg
.. |codebeat| image:: https://codebeat.co/badges/eef1f14d-72eb-445a-af53-12d3565385ec
   :target: https://codebeat.co/projects/github-com-alpha-xone-xbbg-master
.. |license| image:: https://img.shields.io/github/license/alpha-xone/xbbg.svg
    :alt: GitHub license
    :target: https://github.com/alpha-xone/xbbg/blob/master/LICENSE
.. |lic_check| image:: https://app.fossa.com/api/projects/git%2Bgithub.com%2Falpha-xone%2Fxbbg.svg?type=shield
    :alt: FOSSA Status
    :target: https://app.fossa.com/projects/git%2Bgithub.com%2Falpha-xone%2Fxbbg
.. |release| image:: https://zenodo.org/badge/157477269.svg
   :target: https://zenodo.org/badge/latestdoi/157477269
.. |chat| image:: https://badges.gitter.im/xbbg/community.svg
   :target: https://gitter.im/xbbg/community
.. |download| image:: https://img.shields.io/pypi/dm/xbbg
   :target: https://pypistats.org/packages/xbbg
.. _Bloomberg API Library: https://www.bloomberg.com/professional/support/api-library/
