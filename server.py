from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from populate import get_connection
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from flask.ext.cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


judicature_holiday = ['weekend', 'easter', 'judiciature_act_holiday', 'waitangi', 'anzac', 'queens_bday', 'labour']
interpretation_holiday = ['weekend', 'easter', 'interpretation_act_holiday', 'waitangi', 'anzac', 'queens_bday', 'labour']
property_holiday = ['weekend', 'easter', 'property_act_holiday', 'waitangi', 'anzac', 'queens_bday', 'labour' ]

SCHEME_FLAGS = {
    'judicature': judicature_holiday,
    'interpretation': interpretation_holiday,
    'property': property_holiday
}


def calculate_period(cur, args):
    start_date = args['start_date']

    offset = int(args.get('inclusion', 0))
    amount = int(args['amount'])
    units = args.get('units')
    scheme = args['scheme']
    flags = SCHEME_FLAGS.get(scheme, [])
    direction = args.get('direction', 'positive')
    if scheme == 'property':
        flags.append(args['region'])
    target = datetime.strptime(start_date, "%Y-%m-%d").date()

    target += relativedelta(days=offset)

    if units == 'working_days':
        pass

    else:
        if direction == 'negative':
            amount = -amount
        if units == 'days':
            delta = relativedelta(days=amount)
        if units == 'weeks':
            delta = relativedelta(weeks=amount)
        elif units == 'fortnights':
            delta = relativedelta(weeks=amount * 2)
        elif units == 'months':
            delta = relativedelta(months=amount)
        elif units == 'years':
            delta = relativedelta(years=amount)
        amount = 0
        target = target + delta

    cur.execute("""SELECT working_days(%s::date, %s, %s::text[], %s)""", (target, amount, flags, direction == 'positive'))
    result = cur.fetchone()[0]
    end_date = datetime.strptime(result['result'], "%Y-%m-%d").date()
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    result['days_count'] = (end_date- start_date).days

    return result

@app.before_request
def before_request():
    if not hasattr(g, 'db'):
        g.db = get_connection()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/")
@app.route("/*")
@cross_origin()
def working_days():
    try:
        with g.db.cursor() as cur:
            return jsonify(calculate_period(cur, request.args)), 200
    except Exception, e:
        print e
        abort(400)



if __name__ == "__main__":
    app.run(debug=True)
