from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from populate import get_connection
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


app = Flask(__name__)

def calculate_period(cur, args):
    start_date = args['start_date']
    amount = int(args['amount'])
    amount += int(args.get('inclusion', 0))
    units = args.get('units')
    scheme = args['scheme']
    flags = [scheme]
    direction = args.get('direction', 'postive')
    #if direction == 'negative':
    #    amount = -amount;
    if scheme == 'property':
        flags.append(args['region'])
    if units == 'days':
        target = start_date

    else:
        target = datetime.strptime(start_date, "%Y-%m-%d").date()
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

    cur.execute("""SELECT working_days(%s::date, %s, %s::text[])""", (target, amount, flags))

    return cur.fetchone()[0]

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
def working_days():
    try:
        with g.db.cursor() as cur:
            return calculate_period(cur, request.args).strftime('%Y-%m-%d'), 200
    except Exception, e:
        abort(400)



if __name__ == "__main__":
    app.run(debug=True)
