import unittest
from populate import get_connection, init_db, populate
from server import app, calculate_period
import datetime

class TestPopulateDates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection()
        cls.cur = cls.conn.cursor()
        init_db(cls.cur)
        populate(cls.cur)

    @classmethod
    def tearDownClass(cls):
        cls.cur.close()
        cls.conn.close()

    def test_xmas(self):
        self.cur.execute("""SELECT summary_flags FROM holidays WHERE day = '2015-12-25'::date """)
        result = self.cur.fetchone()[0]
        self.assertEqual(result['interpretation'], True)
        self.assertEqual(result['judicature'], True)

    def test_query(self):
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 25,
                               'units': 'days',
                               'scheme': 'judicature'}), datetime.date(2016, 1, 27))
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 1,
                               'units': 'weeks',
                               'scheme': 'judicature'}), datetime.date(2015, 12, 8))
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 1,
                               'units': 'months',
                               'scheme': 'judicature'}), datetime.date(2016, 1, 18))
        self.assertEqual(calculate_period(self.cur, {
                               'start_date': '2015-12-01',
                               'amount': 2,
                               'units': 'years',
                               'scheme': 'judicature'}), datetime.date(2017, 12, 1))


if __name__ == '__main__':
    unittest.main()