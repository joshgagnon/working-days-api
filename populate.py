import psycopg2
import dateutil
from dateutil import easter
from datetime import timedelta, date
from copy import copy


def merge_dicts(dicts):
    result = {}
    for d in filter(lambda x: x, dicts):
        result.update(d)
    return result


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def monday_ize(d):
    if is_weekend(d):
        return next_weekday(d, 0)
    return d

DB = 'working-days'
DB_USER = 'josh'
DB_PASSWORD = ''

START_DATE = date(1950, 1, 1)
END_DATE = date(2050, 1, 1)


try:
    conn = psycopg2.connect(database=DB, user=DB_USER, password=DB_PASSWORD)
except psycopg2.Error, e:
    print e


def is_waitangi(current_date):
    # Feburary 6
    waitangi_day = date(current_date.year, 2, 6)
    return {'waitangi': True} if current_date == monday_ize(waitangi_day) else None


def is_anzac(current_date):
    # April 25
    anzac_day = date(current_date.year, 4, 25)
    return {'anzac': True} if current_date == monday_ize(anzac_day) else None

def is_xmas(current_date):
    start = date(current_date.year, 12, 25)
    end = date(current_date.year + 1, 1, 2)
    jan_first = end = date(current_date.year + 1, 1, 1)
    # if friday, next monday
    if jan_first.weekday() == 4:
         end = end + timedelta(3)
    # if sat or sun, then next tuesday
    if 5 <= jan_first.weekday() <= 6:
        end = next_weekday(end, 2)

def is_queens_bday(current_date):
    # 1st monday in June
    return None

def is_labour(current_date):
    # 4th monday in october
    return None


nz_holidays = {
    'waitangi': is_waitangi,
    'is_anzac': is_anzac,
    'xmas': is_xmas,
    'queens_bday': is_queens_bday,
    'labour_day': is_labour
}



def is_weekend(current_date):
    return {'weekend': True} if 5 <= current_date.weekday() <= 6 else None


def is_easter(current_date):
    easter_date = easter.easter(current_date.year)
    easter_sunday = easter_date
    good_friday = easter_date - timedelta(2)
    easter_monday = easter_date + timedelta(1)
    if good_friday == current_date:
        return {'good_friday': True}
    if easter_monday == current_date:
        return {'easter_monday': True}
    return None

def is_nz_holiday(current_date):
    return merge_dicts([nz_holidays[h](current_date) for h in nz_holidays.keys()])



holiday_tests = {
    'weekend': is_weekend,
    'easter': is_easter,
    'nzholidays': is_nz_holiday,
}


for day in daterange(START_DATE, END_DATE):
    flags = merge_dicts([holiday_tests[h](day) for h in holiday_tests.keys()])
    print day, flags