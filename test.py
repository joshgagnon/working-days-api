import unittest
from populate import get_connection, init_db, populate, is_wellington_anniversary, is_auckland_anniversary, is_nelson_anniversary, \
 is_otago_anniversary, is_westland_anniversary, is_chatham_islands_anniversary, is_taranaki_anniversary, is_southland_anniversary, \
  is_south_canterbury_anniversary, is_hawkes_bay_anniversary, is_marlborough_anniversary, is_canterbury_anniversary, is_provincial
from server import app, calculate_period
from datetime import date
import json


class TestPopulateDates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection()
        cls.cur = cls.conn.cursor()
        init_db(cls.cur)
        populate(cls.cur)
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.cur.close()
        cls.conn.close()

    def test_xmas(self):
        self.cur.execute("""SELECT flags FROM holidays WHERE day = '2015-12-25'::date """)
        result = self.cur.fetchone()[0]
        self.assertEqual(result['xmas_ending_2nd'], True)




    def test_regional(self):
        self.assertEqual(is_auckland_anniversary(date(2017, 1, 29)), None)
        self.assertEqual(is_auckland_anniversary(date(2017, 1, 30)), {'auckland_anniversary': True})
        self.assertEqual(is_auckland_anniversary(date(2018, 1, 29)), {'auckland_anniversary': True})
        self.assertEqual(is_auckland_anniversary(date(2018, 1, 30)), None)
        self.assertEqual(is_auckland_anniversary(date(2020, 1, 27)), {'auckland_anniversary': True})

        self.assertEqual(is_wellington_anniversary(date(2017, 1, 22)), None)
        self.assertEqual(is_wellington_anniversary(date(2017, 1, 23)), {'wellington_anniversary': True})
        self.assertEqual(is_wellington_anniversary(date(2018, 1, 22)), {'wellington_anniversary': True})
        self.assertEqual(is_wellington_anniversary(date(2019, 1, 21)), {'wellington_anniversary': True})
        self.assertEqual(is_wellington_anniversary(date(2019, 1, 22)), None)
        self.assertEqual(is_wellington_anniversary(date(2022, 1, 24)), {'wellington_anniversary': True})

        self.assertEqual(is_nelson_anniversary(date(2017, 2, 1)), None)
        self.assertEqual(is_nelson_anniversary(date(2017, 1, 30)), {'nelson_anniversary': True})
        self.assertEqual(is_nelson_anniversary(date(2018, 1, 29)), {'nelson_anniversary': True})
        self.assertEqual(is_nelson_anniversary(date(2019, 2, 4)), {'nelson_anniversary': True})
        self.assertEqual(is_nelson_anniversary(date(2019, 1, 22)), None)
        self.assertEqual(is_nelson_anniversary(date(2020, 2, 3)), {'nelson_anniversary': True})

        self.assertEqual(is_otago_anniversary(date(2017, 3, 22)), None)
        self.assertEqual(is_otago_anniversary(date(2017, 3, 20)), {'otago_anniversary': True})
        self.assertEqual(is_otago_anniversary(date(2018, 3, 26)), {'otago_anniversary': True})
        self.assertEqual(is_otago_anniversary(date(2019, 3, 25)), {'otago_anniversary': True})
        self.assertEqual(is_otago_anniversary(date(2019, 3, 22)), None)

        self.assertEqual(is_westland_anniversary(date(2017, 12, 1)), None)
        self.assertEqual(is_westland_anniversary(date(2017, 12, 4)), {'westland_anniversary': True})
        self.assertEqual(is_westland_anniversary(date(2018, 12, 3)), {'westland_anniversary': True})
        self.assertEqual(is_westland_anniversary(date(2019, 12, 2)), {'westland_anniversary': True})
        self.assertEqual(is_westland_anniversary(date(2019, 11, 28)), None)

        self.assertEqual(is_chatham_islands_anniversary(date(2017, 11, 30)), None)
        self.assertEqual(is_chatham_islands_anniversary(date(2017, 11, 27)), {'chatham_islands_anniversary': True})
        self.assertEqual(is_chatham_islands_anniversary(date(2018, 12, 3)), {'chatham_islands_anniversary': True})
        self.assertEqual(is_chatham_islands_anniversary(date(2019, 12, 2)), {'chatham_islands_anniversary': True})
        self.assertEqual(is_chatham_islands_anniversary(date(2019, 11, 1)), None)
        self.assertEqual(is_chatham_islands_anniversary(date(2022, 11, 28)), {'chatham_islands_anniversary': True})

        self.assertEqual(is_taranaki_anniversary(date(2017, 3, 31)), None)
        self.assertEqual(is_taranaki_anniversary(date(2017, 3, 13)), {'taranaki_anniversary': True})
        self.assertEqual(is_taranaki_anniversary(date(2018, 3, 12)), {'taranaki_anniversary': True})
        self.assertEqual(is_taranaki_anniversary(date(2019, 3, 11)), {'taranaki_anniversary': True})
        self.assertEqual(is_taranaki_anniversary(date(2019, 3, 31)), None)

        self.assertEqual(is_southland_anniversary(date(2017, 4, 17)), None)
        self.assertEqual(is_southland_anniversary(date(2017, 4, 18)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2018, 4, 3)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2019, 4, 23)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2019, 4, 22)), None)

        self.assertEqual(is_southland_anniversary(date(2017, 4, 17)), None)
        self.assertEqual(is_southland_anniversary(date(2017, 4, 18)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2018, 4, 3)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2019, 4, 23)), {'southland_anniversary': True})
        self.assertEqual(is_southland_anniversary(date(2019, 4, 22)), None)

        self.assertEqual(is_south_canterbury_anniversary(date(2017, 9, 24)), None)
        self.assertEqual(is_south_canterbury_anniversary(date(2017, 9, 25)), {'south_canterbury_anniversary': True})
        self.assertEqual(is_south_canterbury_anniversary(date(2018, 9, 24)), {'south_canterbury_anniversary': True})
        self.assertEqual(is_south_canterbury_anniversary(date(2019, 9, 23)), {'south_canterbury_anniversary': True})
        self.assertEqual(is_south_canterbury_anniversary(date(2019, 9, 22)), None)
        self.assertEqual(is_south_canterbury_anniversary(date(2021, 9, 27)), {'south_canterbury_anniversary': True})

        self.assertEqual(is_hawkes_bay_anniversary(date(2017, 10, 21)), None)
        self.assertEqual(is_hawkes_bay_anniversary(date(2017, 10, 20)), {'hawkes_bay_anniversary': True})
        self.assertEqual(is_hawkes_bay_anniversary(date(2018, 10, 19)), {'hawkes_bay_anniversary': True})
        self.assertEqual(is_hawkes_bay_anniversary(date(2019, 10, 25)), {'hawkes_bay_anniversary': True})
        self.assertEqual(is_hawkes_bay_anniversary(date(2019, 10, 24)), None)

        self.assertEqual(is_marlborough_anniversary(date(2017, 10, 29)), None)
        self.assertEqual(is_marlborough_anniversary(date(2017, 10, 30)), {'marlborough_anniversary': True})
        self.assertEqual(is_marlborough_anniversary(date(2018, 10, 29)), {'marlborough_anniversary': True})
        self.assertEqual(is_marlborough_anniversary(date(2019, 11, 4)), {'marlborough_anniversary': True})
        self.assertEqual(is_marlborough_anniversary(date(2019, 10, 29)), None)
        self.assertEqual(is_marlborough_anniversary(date(2020, 11, 2)), {'marlborough_anniversary': True})

        self.assertEqual(is_canterbury_anniversary(date(2017, 11, 16)), None)
        self.assertEqual(is_canterbury_anniversary(date(2017, 11, 17)), {'canterbury_anniversary': True})
        self.assertEqual(is_canterbury_anniversary(date(2018, 11, 16)), {'canterbury_anniversary': True})
        self.assertEqual(is_canterbury_anniversary(date(2019, 11, 15)), {'canterbury_anniversary': True})
        self.assertEqual(is_canterbury_anniversary(date(2019, 11, 14)), None)

        self.assertEqual(is_provincial(date(2019, 12, 2)), {'chatham_islands_anniversary': True, 'westland_anniversary': True})

    def test_agreement_for_sale(self):
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2017-06-08',
                               'amount': 1,
                               'units': 'months',
                               'direction': 'positive',
                               'region': 'auckland',
                               'scheme': 'agreement_sale_purchase_real_estate'})['result'], '2017-07-07')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2017-07-07',
                               'amount': 1,
                               'units': 'months',
                               'direction': 'negative',
                               'region': 'auckland',
                               'scheme': 'agreement_sale_purchase_real_estate'})['result'], '2017-06-07')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2017-06-02',
                               'amount': 1,
                               'units': 'day',
                               'direction': 'positive',
                               'region': 'auckland',
                               'scheme': 'agreement_sale_purchase_real_estate'})['result'], '2017-06-06')





    def test_query(self):
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 25,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2016-01-27')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2001-10-1',
                               'amount': 10,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2001-10-15')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 1,
                               'units': 'weeks',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2015-12-08')
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 1,
                               'units': 'months',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2016-01-18')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 2,
                               'units': 'years',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2017-12-01')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 20,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2016-10-07')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 1,
                               'units': 'working_days',
                               'direction': 'negative',
                               'scheme': 'high_court'})['result'], '2016-09-09')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 1,
                               'units': 'days',
                               'direction': 'negative',
                               'scheme': 'high_court'})['result'], '2016-09-09')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 2,
                               'units': 'days',
                               'direction': 'negative',
                               'scheme': 'high_court'})['result'], '2016-09-09')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 1,
                               'units': 'weeks',
                               'direction': 'negative',
                               'scheme': 'high_court'})['result'], '2016-09-02')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 1,
                               'units': 'weeks',
                               'direction': 'positive',
                               'scheme': 'high_court'})['result'], '2016-09-19')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-11',
                               'amount': 1,
                               'units': 'weeks',
                               'direction': 'negative',
                               'scheme': 'high_court'})['result'], '2016-09-02')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-17',
                               'amount': 30,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'companies'})['result'], '2016-10-31')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-09-17',
                               'amount': 30,
                               'units': 'working_days',
                               'direction': 'negative',
                               'scheme': 'companies'})['result'], '2016-08-08')


        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-10-01',
                               'amount': 20,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'companies'})['result'], '2016-10-31')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2016-12-03',
                               'amount': 30,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'companies'})['result'], '2017-01-24')

        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2018-12-06',
                               'amount': 40,
                               'units': 'working_days',
                               'direction': 'positive',
                               'scheme': 'interpretation'})['result'], '2019-02-12')

if __name__ == '__main__':
    unittest.main()