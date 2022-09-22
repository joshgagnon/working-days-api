from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from populate import get_connection
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
try:
    from flask.ext.cors import CORS, cross_origin
except:
    from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


judicature_holiday = ['queen_memorial', 'matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
judicature_holiday_no_mondayize = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'queens_bday', 'labour']
appeal_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi','waitangi_mondayized', 'anzac', 'anzac_mondayized', 'queens_bday', 'labour']
supreme_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'queens_bday', 'labour', 'wellington_anniversary']
interpretation_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
companies_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
property_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
agreement_sale_purchase_real_estate = ['queen_memorial', 'matariki', 'weekend', 'easter', 'xmas_eve', 'xmas_ending_5th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
income_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
goods_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
credit_holiday = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
personal_property = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
personal_property_special = ['queen_memorial','weekend', 'easter', 'xmas_ending_15th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
land_transfer = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas', 'boxing', 'new_years', 'second_jan', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
land_transfer_2017 = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_ending_2nd', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']
resource_management = ['queen_memorial','matariki', 'weekend', 'easter', 'xmas_starting_20th_ending_10th', 'waitangi', 'anzac', 'waitangi_mondayized', 'anzac_mondayized', 'queens_bday', 'labour']


SCHEME_FLAGS = {
    'district_court': judicature_holiday,
    'high_court': judicature_holiday,
    'high_court_special': judicature_holiday_no_mondayize,
    'court_of_appeal': appeal_holiday,
    'supreme_court': supreme_holiday,
    'companies': companies_holiday,
    'interpretation': interpretation_holiday,
    'property': property_holiday,
    'income': income_holiday,
    'goods_services': goods_holiday,
    'credit_contracts': credit_holiday,
    'personal_property': personal_property,
    'personal_property_special': personal_property_special,
    'land_transfer': land_transfer,
     'land_transfer_2017': land_transfer_2017,
    'agreement_sale_purchase_real_estate': agreement_sale_purchase_real_estate,
    'resource_management': resource_management,
    'official_information_act': judicature_holiday
}

ROUND_DOWN = {
    'agreement_sale_purchase_real_estate': True
}


def calculate_period(cur, args):
    start_date = args['start_date']
    offset = int(args.get('inclusion', 0))
    amount = int(args['amount'])
    units = args.get('units')
    scheme = args['scheme']
    flank = int(args.get('flank', 0))
    flags = SCHEME_FLAGS.get(scheme, [])[:]
    direction = args.get('direction', 'positive')
    if scheme in ['property', 'land_transfer', 'agreement_sale_purchase_real_estate']:
        flags.append(args['region'])
    calendar_days = args.get('mode') == 'calendar_days'

    target = datetime.strptime(start_date, "%Y-%m-%d").date()

    target += relativedelta(days=offset)
    if units == 'working_days':
        cur.execute("""SELECT working_day_offset(%s, %s, %s::text[], %s)""", (target, amount, flags, direction == 'positive'))
    else:
        if units == 'fortnights':
            units = 'weeks'
            amount *= 2
        params = (target, '%s %s' % (amount, units), flags, direction == 'positive', calendar_days)
        if ROUND_DOWN.get(scheme):
            cur.execute("""SELECT day_offset_round_down(%s, %s::interval, %s::text[], %s, %s)""", params)
        else:
            cur.execute("""SELECT day_offset(%s, %s::interval, %s::text[], %s, %s)""", params)

    result = cur.fetchone()[0]
    end_date = datetime.strptime(result['result'], "%Y-%m-%d").date()
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if flank > 0:
        query = """SELECT day_offset(%s, '%s days', %s::text[], %s, false) """;
        cur.execute(query, [start_date, flank, flags, False])
        before_range = cur.fetchone()[0]['range'] or []
        cur.execute(query, [end_date, flank, flags, True])
        after_range = cur.fetchone()[0]['range'] or []
        if not result['range']:
            result['range'] = []
        flank_map = lambda x: dict({'flank': True}, **x)
        result['range'].extend(list(map(flank_map, before_range)))
        result['range'].extend(list(map(flank_map, after_range)))

    result['days_count'] = (end_date - start_date).days
    return result

def is_working_day(cur, args):
    date = args['date']
    scheme = args['scheme']
    flags = SCHEME_FLAGS.get(scheme, [])[:]
    if scheme in ['property', 'land_transfer', 'agreement_sale_purchase_real_estate']:
        flags.append(args['region'])
    params = (date, flags)
    cur.execute("""SELECT is_working_day(%s, %s::text[])""", params)
    return {'is_working_day': cur.fetchone()[0]}


def get_holidays(cur):
    cur.execute("""SELECT get_holidays() as holidays """)
    return {'holidays': cur.fetchone()[0]}


@app.before_request
def before_request():
    if not hasattr(g, 'db'):
        g.db = get_connection()

@app.after_request
def add_header(response):
    response.cache_control.max_age = 86400
    return response

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/get_holidays")
@cross_origin()
def get_holdiays():
    try:
        with g.db.cursor() as cur:
            return jsonify(get_holidays(cur)), 200
    except Exception as e:
        abort(400)


@app.route("/is_working_day")
@cross_origin()
def get_is_working_day():
    try:
        with g.db.cursor() as cur:
            return jsonify(is_working_day(cur, request.args)), 200
    except Exception as e:
        app.logger.error(e)
        abort(400)

@app.route("/")
@app.route("/*")
@cross_origin()
def working_days():
    try:
        #app.logger.error('hi')
        with g.db.cursor() as cur:
            return jsonify(calculate_period(cur, request.args)), 200
    except Exception as e:
        app.logger.error(e)
        abort(400)




if __name__ == "__main__":
    app.run(debug=True)
