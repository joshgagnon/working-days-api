from __future__ import print_function
import psycopg2
from psycopg2.extras import Json
import dateutil
from dateutil import easter
from datetime import timedelta, date
from copy import copy

try:
    from config import DB, DB_USER, DB_PASSWORD
except:
    DB = 'working-days'
    DB_USER = ''
    DB_PASSWORD = ''

START_DATE = date(2000, 1, 1)
END_DATE = date(2050, 1, 1)


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
    # mondayization from Jan 1st 2014
    if d >= date(2014, 1, 1) and is_weekend(d):
        return next_weekday(d, 0)
    return d


def get_connection():
    conn = psycopg2.connect(database=DB, user=DB_USER, password=DB_PASSWORD)
    return conn



def init_db(cur):
    with open('tables.sql') as tables:
        cur.execute(tables.read())
    with open('functions.sql') as tables:
        cur.execute(tables.read())


def populate(cur):
    print('%s to %s' % (START_DATE, END_DATE))
    args = [(x[0], Json(x[1]), Json(x[2])) for x in calculate_dates()]
    records_list_template = ','.join(['%s'] * len(args))
    insert = 'INSERT INTO holidays (day, flags, summary_flags) values {0}'.format(records_list_template)
    cur.execute(cur.mogrify(insert, args))
    print('Inserted %d dates' % len(args))


def is_provincial(current_date):
    pronvicial_dates = {
        'wellington_anniversary': (1, 25),
        'auckland_anniversary': (2, 1),
        'nelson_anniversary': (2, 1),
        'tarankai_anniversary': (3, 14),
        'otago_anniversary': (3, 21),
        'southland_anniversary': (3, 29),
        'south_canterbury_anniversary': (9, 26),
        'hawkes_bay_anniversary': (10, 21),
        'marlborough_anniversary': (10, 31),
        'canterbury_anniversary': (11, 11),
        'westland_anniversary': (11, 28),
        'chatham_islands_anniversary': (11, 28)
    }
    result = None
    for p in pronvicial_dates.keys():
        if pronvicial_dates[p][0] == current_date.month and pronvicial_dates[p][1] == current_date.day:
            result = result or {}
            result[p] = True
    return result and {'provincial': result}


def is_waitangi(current_date):
    # Feburary 6
    waitangi_day = date(current_date.year, 2, 6)
    if current_date == waitangi_day:
        return {'waitangi': True}
    if current_date == monday_ize(waitangi_day):
        return {'waitangi': True, 'mondayized': True}


def is_anzac(current_date):
    # April 25
    anzac_day = date(current_date.year, 4, 25)
    if current_date == anzac_day:
        return {'anzac': True}
    if current_date == monday_ize(anzac_day):
        return {'anzac': True, 'mondayized': True}


def is_xmas(current_date):
    if current_date.month == 12 and current_date.day == 25:
        return {'xmas': True}

    if current_date.month == 12 and current_date.day == 26:
        return {'boxing': True}


def is_judicature_act_holiday(current_date):
    if (current_date.month == 12 and current_date.day >= 25) or \
        (current_date.month == 1 and current_date.day <= 15):
        return {'judiciature_act_holiday': True}


def is_intepretation_act_holiday(current_date):
    start = date(current_date.year, 12, 25)
    end = date(current_date.year, 1, 2)
    jan_first = end = date(current_date.year + 1, 1, 1)
    # if friday, next monday
    if jan_first.weekday() == 4:
         end = end + timedelta(3)
    # if sat or sun, then next tuesday
    if 5 <= jan_first.weekday() <= 6:
        end = next_weekday(end, 2)

    if start >= current_date  or current_date <= end:
        return {'interpretation_act_holiday': True, 'companies_act_holiday': True}


def is_queens_bday(current_date):
    # 1st monday in June
    if current_date.month == 6 and current_date.weekday() == 0 and 1 <= current_date.day <= 7:
        return {'queens_bday': True}
    return None


def is_labour(current_date):
    # 4th monday in october
    if current_date.month == 10 and current_date.weekday() == 0 and 22 <= current_date.day:
        return {'labour': True}
    return None


nz_holidays = {
    'waitangi': is_waitangi,
    'anzac': is_anzac,
    'xmas': is_xmas,
    'queens_bday': is_queens_bday,
    'labour': is_labour,
    'judicature': is_judicature_act_holiday,
    'interpretation': is_intepretation_act_holiday,
    'pronvincial': is_provincial
}



def is_weekend(current_date):
    return {'weekend': True} if 5 <= current_date.weekday() <= 6 else None


def is_easter(current_date):
    easter_date = easter.easter(current_date.year)
    good_friday = easter_date - timedelta(2)
    easter_monday = easter_date + timedelta(1)
    result = None
    if good_friday == current_date:
        result = result or {}
        result['good_friday'] = True
    if easter_monday == current_date:
        result = result or {}
        result['easter_monday'] = True
    if good_friday <= current_date <= easter_monday:
        result = result or {}
        result['easter'] = True
    return result


def is_nz_holiday(current_date):
    return merge_dicts([nz_holidays[h](current_date) for h in nz_holidays.keys()])



holiday_tests = {
    'weekend': is_weekend,
    'easter': is_easter,
    'nzholidays': is_nz_holiday,
}


def calculate_dates():
    for day in daterange(START_DATE, END_DATE):
        flags = merge_dicts([holiday_tests[h](day) for h in holiday_tests.keys()])
        summary = {}
        if flags.get('provincial'):
            summary.update(flags.get('provincial'))
        judicature_holiday = ['weekend', 'easter', 'judiciature_act_holiday', 'waitangi', 'anzac', 'queens_bday', 'labour']
        interpretation_holiday = ['weekend', 'easter', 'interpretation_act_holiday', 'waitangi', 'anzac', 'queens_bday', 'labour']
        if any([flags.get(s) for s in judicature_holiday]):
            summary['judicature'] = True
        if any([flags.get(s) for s in interpretation_holiday]):
            summary['interpretation'] = True
        yield (day, flags, summary)


if __name__ == "__main__":
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            init_db(cur)
            populate(cur)
        conn.commit()
        conn.close()
    except psycopg2.Error, e:
        print(e)
