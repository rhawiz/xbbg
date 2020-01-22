import pandas as pd

import pytest
try: import blpapi
except ImportError: blpapi = pytest.importorskip('blpapi')

from collections import OrderedDict

from xbbg import const
from xbbg.core.timezone import DEFAULT_TZ
from xbbg.core import intervals, overrides, conn

RESPONSE_ERROR = blpapi.Name("responseError")
SESSION_TERMINATED = blpapi.Name("SessionTerminated")
CATEGORY = blpapi.Name("category")
MESSAGE = blpapi.Name("message")
BAR_DATA = blpapi.Name('barData')
BAR_TICK = blpapi.Name('barTickData')
TICK_DATA = blpapi.Name('tickData')


def init_request(request: blpapi.request.Request, tickers, flds, **kwargs):
    """
    Initiate Bloomberg request instance

    Args:
        request: Bloomberg request to initiate and append
        tickers: tickers
        flds: fields
        **kwargs: overrides and
    """
    while conn.bbg_session(**kwargs).tryNextEvent(): pass

    if isinstance(tickers, str): tickers = [tickers]
    for ticker in tickers: request.append('securities', ticker)

    if isinstance(flds, str): flds = [flds]
    for fld in flds: request.append('fields', fld)

    adjust = kwargs.pop('adjust', None)
    if isinstance(adjust, str) and adjust:
        if adjust == 'all':
            kwargs['CshAdjNormal'] = True
            kwargs['CshAdjAbnormal'] = True
            kwargs['CapChg'] = True
        else:
            kwargs['CshAdjNormal'] = 'normal' in adjust or 'dvd' in adjust
            kwargs['CshAdjAbnormal'] = 'abn' in adjust or 'dvd' in adjust
            kwargs['CapChg'] = 'split' in adjust

    if 'start_date' in kwargs: request.set('startDate', kwargs.pop('start_date'))
    if 'end_date' in kwargs: request.set('endDate', kwargs.pop('end_date'))

    for elem_name, elem_val in overrides.proc_elms(**kwargs):
        request.set(elem_name, elem_val)

    ovrds = request.getElement('overrides')
    for ovrd_fld, ovrd_val in overrides.proc_ovrds(**kwargs):
        ovrd = ovrds.appendElement()
        ovrd.setElement('fieldId', ovrd_fld)
        ovrd.setElement('value', ovrd_val)


def time_range(dt, ticker, session='allday', tz='UTC') -> intervals.Session:
    """
    Time range in UTC (for intraday bar) or other timezone

    Args:
        dt: date
        ticker: ticker
        session: market session defined in xbbg/markets/exch.yml
        tz: timezone

    Returns:
        intervals.Session
    """
    ss = intervals.get_interval(ticker=ticker, session=session)
    exch = const.exch_info(ticker=ticker)
    cur_dt = pd.Timestamp(dt).strftime('%Y-%m-%d')
    time_fmt = '%Y-%m-%dT%H:%M:%S'
    time_idx = pd.DatetimeIndex([
        f'{cur_dt} {ss.start_time}', f'{cur_dt} {ss.end_time}']
    ).tz_localize(exch.tz).tz_convert(DEFAULT_TZ).tz_convert(tz)
    if time_idx[0] > time_idx[1]: time_idx -= pd.TimedeltaIndex(['1D', '0D'])
    return intervals.Session(time_idx[0].strftime(time_fmt), time_idx[1].strftime(time_fmt))


def receive_events(func, **kwargs):
    """
    Receive events received from Bloomberg

    Args:
        func: must be generator function
        **kwargs: arguments for input function

    Yields:
        Elements of Bloomberg responses
    """
    timeout_counts = 0
    responses = [blpapi.Event.PARTIAL_RESPONSE, blpapi.Event.RESPONSE]
    while True:
        ev = conn.bbg_session(**kwargs).nextEvent(500)
        if ev.eventType() in responses:
            for msg in ev:
                for r in func(msg=msg, **kwargs):
                    yield r
            if ev.eventType() == blpapi.Event.RESPONSE:
                break
        elif ev.eventType() == blpapi.Event.TIMEOUT:
            timeout_counts += 1
            if timeout_counts > 10:
                break
        else:
            for _ in ev:
                if getattr(ev, 'messageType', lambda: None)() \
                    == SESSION_TERMINATED: break


def process_ref(msg: blpapi.message.Message) -> dict:
    """
    Process reference messages from Bloomberg

    Args:
        msg: Bloomberg reference data messages from events

    Returns:
        dict
    """
    data = None
    if msg.hasElement('securityData'):
        data = msg.getElement('securityData')
    elif msg.hasElement('data') and \
            msg.getElement('data').hasElement('securityData'):
        data = msg.getElement('data').getElement('securityData')
    if data is None: yield {}

    for sec in data.values():
        ticker = sec.getElement('security').getValue()
        for fld in sec.getElement('fieldData').elements():
            info = [('ticker', ticker), ('field', str(fld.name()))]
            if fld.isArray():
                for item in fld.values():
                    yield OrderedDict(info + [
                        (
                            str(elem.name()),
                            None if elem.isNull() else elem.getValue()
                        )
                        for elem in item.elements()
                    ])
            else:
                yield OrderedDict(info + [
                    ('value', None if fld.isNull() else fld.getValue()),
                ])


def process_hist(msg: blpapi.message.Message) -> dict:
    """
    Process historical data messages from Bloomberg

    Args:
        msg: Bloomberg historical data messages from events

    Returns:
        dict
    """
    if not msg.hasElement('securityData'): return {}
    ticker = msg.getElement('securityData').getElement('security').getValue()
    for val in msg.getElement('securityData').getElement('fieldData').values():
        if val.hasElement('date'):
            yield OrderedDict([('ticker', ticker)] + [
                (str(elem.name()), elem.getValue()) for elem in val.elements()
            ])


def process_bar(msg: blpapi.message.Message, typ='bar') -> OrderedDict:
    """
    Process Bloomberg intraday bar messages

    Args:
        msg: Bloomberg intraday bar messages from events
        typ: `bar` or `tick`

    Yields:
        OrderedDict
    """
    check_error(msg=msg)
    if typ[0].lower() == 't':
        lvls = [TICK_DATA, TICK_DATA]
    else:
        lvls = [BAR_DATA, BAR_TICK]

    for bar in msg.getElement(lvls[0]).getElement(lvls[1]).values():
        yield OrderedDict([
            (str(elem.name()), elem.getValue()) for elem in bar.elements()
        ])


def check_error(msg):
    """
    Check error in message
    """
    if msg.hasElement(RESPONSE_ERROR):
        error = msg.getElement(RESPONSE_ERROR)
        raise ValueError(
            f'[Intraday Bar Error] '
            f'{error.getElementAsString(CATEGORY)}: '
            f'{error.getElementAsString(MESSAGE)}'
        )
