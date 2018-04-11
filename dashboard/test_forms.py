from django.test import TestCase
from .forms import DateForm

class TestDashBoardForms(TestCase):
    """The most simple form is made from only
    one input field: the year. The most flexible and simple
    is made of one range of dates. We build this one."""

    def setUp(self):
        pass

    def test_only_first_date(self):
        """If only the first date is entered, then all data
        from this date are retrieved."""
        data = {'start_date' : '2018-01-01'}
        f = DateForm(data=data)
        self.assertTrue(f.is_valid(), f.errors.as_data())

    def test_invalid_date(self):
        data = {'start_date': '2018-01-41'}
        f = DateForm(data=data)
        self.assertFalse(f.is_valid(), f.errors.as_data())

    def test_only_second_date(self):
        """If only the 2nd date, then all data until this date
        are retrieved."""
        data = {'end_date': '2018-01-01'}
        f = DateForm(data=data)
        self.assertTrue(f.is_valid(), f.errors.as_data())

    def test_1st_and_2nd_date_right_ordering(self):
        """The data ranging between these dates are retrieved."""
        data = {'start_date': '2018-01-01', 'end_date': '2018-01-31'}
        f = DateForm(data=data)
        self.assertTrue(f.is_valid(), f.errors.as_data())

    def test_1st_and_2nd_date_inversed_ordering(self):
        """The data ranging between these dates are retrieved."""
        data = {'start_date': '2018-01-31', 'end_date': '2018-01-01'}
        f = DateForm(data=data)
        self.assertFalse(f.is_valid(), f.errors.as_data())

    def test_both_date_fields_empty(self):
        f = DateForm(data={})
        self.assertFalse(f.is_valid(), 'Both fields are empty. It should be invalid')
