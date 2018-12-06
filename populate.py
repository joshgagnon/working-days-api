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

def closest_monday(d):
    if d.weekday() == 0:
        return d
    if d.weekday() <= 3:
        return d - timedelta(d.weekday())
    else:
        return d + timedelta(7 - d.weekday())



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
    args = [(x[0], Json(x[1])) for x in calculate_dates()]
    records_list_template = ','.join(['%s'] * len(args))
    insert = 'INSERT INTO holidays (day, flags) values {0}'.format(records_list_template)
    cur.execute(cur.mogrify(insert, args))
    print('Inserted %d dates' % len(args))


def is_provincial(current_date):
    pronvicial_dates = {
        'wellington_anniversary': is_wellington_anniversary,
        'auckland_anniversary': is_auckland_anniversary,
        'nelson_anniversary': is_nelson_anniversary,
        'taranaki_anniversary': is_taranaki_anniversary,
        'otago_anniversary': is_otago_anniversary,
        'southland_anniversary': is_southland_anniversary,
        'south_canterbury_anniversary': is_south_canterbury_anniversary,
        'hawkes_bay_anniversary': is_hawkes_bay_anniversary,
        'marlborough_anniversary': is_marlborough_anniversary,
        'canterbury_anniversary': is_canterbury_anniversary,
        'westland_anniversary': is_westland_anniversary,
        'chatham_islands_anniversary': is_chatham_islands_anniversary
    }
    result = None

    for p in pronvicial_dates.keys():
        result = merge_dicts([result, pronvicial_dates[p](current_date)])
    return result


def is_wellington_anniversary(current_date):
    """ Wellington Anniversary Day is actually the 22nd of January but it is observed on the Monday closest to that date.
    Wellington Anniversary applies to the Wellington Province which includes Wellington, Whanganui,
    Palmerston North, Kapiti, Feilding, Levin and Masterton."""
    official_day =  date(current_date.year, 1, 22)
    if current_date == closest_monday(official_day):
        return {'wellington_anniversary': True}


def is_auckland_anniversary(current_date):
    """ Taranaki Anniversary Day is actually the 31st of March but it is observed on the second Monday of March.
    Taranaki Anniversary applies to the Taranaki Region which includes Inglewood, Waitara, Hawera, Stratford, and Eltham."""
    official_day = date(current_date.year, 1, 29)
    if current_date == closest_monday(official_day):
        return {'auckland_anniversary': True}


def is_nelson_anniversary(current_date):
    """ Nelson Anniversary Day is actually the 1st of February but it is observed on the Monday closest to that date."""
    official_day = date(current_date.year, 2, 1)
    if current_date == closest_monday(official_day):
        return {'nelson_anniversary': True}


def is_otago_anniversary(current_date):
    """ Otago Anniversary Day is actually the 23rd of March but it is observed on the Monday closest to that date. """
    official_day = date(current_date.year, 3, 23)
    if current_date == closest_monday(official_day):
        return {'otago_anniversary': True}


def is_westland_anniversary(current_date):
    """ Westland Anniversary Day is actually the 1st of December but it is observed on the Monday closest to that date. This date can vary outside of Greymouth."""
    official_day = date(current_date.year, 12, 1)
    if current_date == closest_monday(official_day):
        return {'westland_anniversary': True}

def is_chatham_islands_anniversary(current_date):
    """ Chatham Islands Anniversary Day is actually the 30th of November but it is observed on the Monday closest to that date."""
    official_day = date(current_date.year, 11, 30)
    if current_date == closest_monday(official_day):
        return {'chatham_islands_anniversary': True}

def is_taranaki_anniversary(current_date):
    """ Taranaki Anniversary Day is actually the 31st of March but it is observed on the second Monday of March.
    Taranaki Anniversary applies to the Taranaki Region which includes Inglewood, Waitara, Hawera, Stratford, and Eltham."""
    if current_date.month == 3 and current_date.weekday() == 0 and 8 <= current_date.day and current_date.day < 16:
        return {'taranaki_anniversary': True}


def is_southland_anniversary(current_date):
    easter_date = easter.easter(current_date.year)
    easter_tuesday = easter_date + timedelta(2)
    if current_date == easter_tuesday:
        return {'southland_anniversary': True}


def is_south_canterbury_anniversary(current_date):
    """ South Canterbury Anniversary Day is actually the 16th of December but it is observed on the fourth Monday in September.
    This is also Dominion Day which is the anniversary of New Zealand being granted Dominion status within the British Empire (1907). """
    if current_date.month == 9 and current_date.weekday() == 0 and 22 <= current_date.day and current_date.day < 28:
        return {'south_canterbury_anniversary': True}


def is_hawkes_bay_anniversary(current_date):
    """ Hawke's Bay Anniversary Day is actually the 1st of November but it is observed on the Friday before Labour Day. """
    """ (labour day is the fourth monday in october ) """
    labour_day = date(current_date.year, 10, 22)
    while labour_day.weekday() != 0:
        labour_day += timedelta(1)

    if (labour_day - timedelta(3)) == current_date:
        return {'hawkes_bay_anniversary': True}


def is_marlborough_anniversary(current_date):
    """ Marlborough Anniversary Day is actually the 1st of November but it is observed on the first Monday after Labour Day. """
    labour_day = date(current_date.year, 10, 22)
    while labour_day.weekday() != 0:
        labour_day += timedelta(1)

    if (labour_day + timedelta(7)) == current_date:
        return {'marlborough_anniversary': True}

def is_canterbury_anniversary(current_date):
    """ Canterbury Anniversary Day is actually the 16th of December but it is observed on the second Friday after the first Tuesday in November.
    This is also Christchurch Show Day. Canterbury Anniversary applies to the North and Central Canterbury Regions which include Christchurch and Ashburton. """
    first_tuesday = date(current_date.year, 11, 1)
    while first_tuesday.weekday() != 1:
        first_tuesday += timedelta(1)
    anniversary = first_tuesday + timedelta(10)
    if anniversary == current_date:
        return {'canterbury_anniversary': True}


def is_waitangi(current_date):
    # Feburary 6
    waitangi_day = date(current_date.year, 2, 6)
    if current_date == monday_ize(waitangi_day) and monday_ize(waitangi_day) != waitangi_day:
        return {'waitangi_mondayized': True}
    if current_date == waitangi_day:
        return {'waitangi': True}


def is_anzac(current_date):
    # April 25
    anzac_day = date(current_date.year, 4, 25)
    if current_date == monday_ize(anzac_day) and monday_ize(anzac_day) != anzac_day:
        return {'anzac_mondayized': True}
    if current_date == anzac_day:
        return {'anzac': True}


def is_xmas(current_date):
    if current_date.month == 12 and current_date.day == 24:
        return {'xmas_eve': True}

    if current_date.month == 12 and current_date.day == 25:
        return {'xmas': True}

    if current_date.month == 12 and current_date.day == 26:
        return {'boxing': True}

    if current_date.month == 1 and current_date.day == 1:
        return {'new_year': True}

    if current_date.month == 1 and current_date.day == 2:
        return {'second_jan': True}


def is_xmas_ending_15th_holiday(current_date):
    if (current_date.month == 12 and current_date.day >= 25) or \
        (current_date.month == 1 and current_date.day <= 15):
        return {'xmas_ending_15th': True}


def is_xmas_ending_5th_holiday(current_date):
    if (current_date.month == 12 and current_date.day >= 25) or \
        (current_date.month == 1 and current_date.day <= 5):
        return {'xmas_ending_5th': True}


def is_xmas_ending_10th_holiday(current_date):
    if (current_date.month == 12 and current_date.day >= 20) or \
        (current_date.month == 1 and current_date.day <= 10):
        return {'xmas_starting_20th_ending_10th': True}


def is_xmas_ending_2nd_holiday(current_date):
    start = date(current_date.year, 12, 25)
    end = date(current_date.year, 1, 2)
    jan_first =  date(current_date.year, 1, 1)
    # if friday, next monday
    if jan_first.weekday() == 4:
         end = end + timedelta(3)
    # if sat or sun, then next tuesday
    if 5 <= jan_first.weekday() <= 6:
        end = next_weekday(end, 1)

    if current_date >= start or current_date <= end:
        return {'xmas_ending_2nd': True}


def is_queens_bday(current_date):
    # 1st monday in June
    if current_date.month == 6 and current_date.weekday() == 0 and 1 <= current_date.day <= 7:
        return {'queens_bday': True}
    return None


def is_labour(current_date):
    # 4th monday in october
    if current_date.month == 10 and current_date.weekday() == 0 and 22 <= current_date.day and current_date.day < 28 :
        return {'labour': True}
    return None


nz_holidays = {
    'waitangi': is_waitangi,
    'anzac': is_anzac,
    'xmas': is_xmas,
    'queens_bday': is_queens_bday,
    'labour': is_labour,
    'xmas_ending_2nd': is_xmas_ending_2nd_holiday,
    'xmas_ending_15th': is_xmas_ending_15th_holiday,
    'xmas_ending_5th': is_xmas_ending_5th_holiday,
    'xmas_starting_20th_ending_10th': is_xmas_ending_10th_holiday,
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
        yield (day, flags)


if __name__ == "__main__":
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            init_db(cur)
            populate(cur)
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(e)
