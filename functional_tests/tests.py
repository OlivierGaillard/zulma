from selenium import webdriver
from selenium.webdriver.support.ui import Select

from django.test import LiveServerTestCase, TestCase
from django.test import TransactionTestCase
from django.conf import settings

import unittest
from datetime import datetime, timedelta
from django.utils import timezone
from _datetime import date
import locale
import time


class NewVisitorTest(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.base_url = 'http://127.0.0.1:8000/'
        #self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_view_articles_list(self):
        url = 'inventory/articles/'

        self.browser.get(self.base_url + url)
        username = self.browser.find_element_by_name('username')
        username.send_keys('golivier')
        password = self.browser.find_element_by_name('password')
        password.send_keys('10minwindow')
        button = self.browser.find_elements_by_xpath('//button[@type="submit"]')
        button[0].click()

        self.assertInHTML('About' in self.browser.page_source)





