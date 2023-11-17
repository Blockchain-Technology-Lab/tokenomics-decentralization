import argparse
import datetime
import pytest
from tokenomics_decentralization.helper import get_ledgers, valid_date, get_date_beginning, get_date_end, get_dates_between, get_median_tx_fee

def test_valid_date():
    for d in ['2022', '2022-01', '2022-01-01']:
        assert valid_date(d)

    for d in ['2022/1/01', '2022/01/1', '2022/1', '2022/01', '2022.1.01', '2022.01.1', '2022.1', '2022.01', 'blah',
              '2022-', '2022-1-1', '2022-1-01', '2022-1', '2022-01-1', '2022-02-29']:
        with pytest.raises(argparse.ArgumentTypeError) as e_info:
            valid_date(d)
        assert e_info.type == argparse.ArgumentTypeError


def test_get_date_beginning():
    dates = {'2022': datetime.date(2022, 1, 1), '2022-03': datetime.date(2022, 3, 1),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, start_date in dates.items():
        assert get_date_beginning(date) == start_date


def test_get_date_end():
    dates = {'2022': datetime.date(2022, 12, 31), '2024-02': datetime.date(2024, 2, 29),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, end_date in dates.items():
        assert get_date_end(date) == end_date


def test_get_ledgers():
    ledgers = get_ledgers()
    assert type(ledgers) == list
    assert len(ledgers) > 0


def test_get_dates_between():
    start_date = datetime.date(2023, 9, 25)
    end_date = datetime.date(2023, 11, 20)
    dates_day = get_dates_between(start_date, end_date, granularity='day')
    assert len(dates_day) == 57
    assert dates_day[0] == "2023-09-25"
    assert dates_day[2] == "2023-09-27"
    assert dates_day[-1] == "2023-11-20"

    start_date = datetime.date(2023, 11, 10)
    end_date = datetime.date(2023, 11, 10)
    dates_day = get_dates_between(start_date, end_date, granularity='day')
    assert len(dates_day) == 1
    assert dates_day[0] == "2023-11-10"

    start_date = datetime.date(2023, 11, 8)
    end_date = datetime.date(2023, 12, 25) 
    dates_week = get_dates_between(start_date, end_date, granularity='week')
    assert len(dates_week) == 7
    assert dates_week[0] == "2023-11-08"
    assert dates_week[3] == "2023-11-29"
    assert dates_week[-1] == "2023-12-20"

    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2023, 1, 15)    
    dates_month = get_dates_between(start_date, end_date, granularity='month')
    assert len(dates_month) == 13
    assert dates_month[3] == "2022-04-01"
    assert dates_month[10] == "2022-11-01"
    assert dates_month[-1] == "2023-01-01"

    start_date = datetime.date(1996, 9, 25)
    end_date = datetime.date(2023, 9, 24)
    dates_year = get_dates_between(start_date, end_date, granularity='year')
    assert len(dates_year) == 27
    assert dates_year[0] == "1996-09-25"
    assert dates_year[14] == "2010-09-25"
    assert dates_year[-1] == "2022-09-25"

    start_date = datetime.date(2023, 11, 11)
    end_date = datetime.date(2023, 11, 10)
    with pytest.raises(ValueError) as e_info:
        get_dates_between(start_date, end_date, granularity='day')
    assert e_info.type == ValueError

    start_date = datetime.date(2023, 11, 10)
    end_date = datetime.date(2023, 11, 10)
    with pytest.raises(ValueError) as e_info:
        get_dates_between(start_date, end_date, granularity='bla')
    assert e_info.type == ValueError


def test_get_median_tx_fee(mocker):
    get_granularity_mock = mocker.patch("tokenomics_decentralization.helper.get_granularity")

    get_granularity_mock.return_value = 'month'
    fee1 = get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee1 == 2820
    fee2 = get_median_tx_fee('ethereum', '2023-10-18')
    assert fee2 == 619000000000000

    get_granularity_mock.return_value = 'week'
    fee3 = get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee3 == 2712