import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import factory

from django.contrib.auth.models import User
from chromedriver import CHROMEDRV_PATH


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "u%s" % n)
    email = factory.Sequence(lambda n: "test-user-%s@example.com" % n)
    first_name = factory.Sequence(lambda n: 'User%s Bob' % n)
    last_name = factory.Sequence(lambda n: 'User%s Smith' % n)


class SeleniumBase(StaticLiveServerTestCase):

    def setUp(self):
        # We create a user
        self.sample_password = '123'
        self.user = UserFactory.create()
        self.user.is_staff = True
        self.user.set_password(self.sample_password)
        self.user.save()

    def tearDown(self):
        self.browser.implicitly_wait(4)
        self.browser.quit()

    def login_this_guy(self, uid, upwd):
        self.browser.get(self.live_server_url + reverse('admin:login'))
        email_input = self.browser.find_element_by_name('username')
        password_input = self.browser.find_element_by_name('password')
        email_input.send_keys(uid)
        password_input.send_keys(upwd)
        password_input.send_keys(Keys.ENTER)
        self.browser.implicitly_wait(3)


class SeleniumFirefoxBaseTests(SeleniumBase):

    def setUp(self):
        super(SeleniumFirefoxBaseTests, self).setUp()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.login_this_guy(uid=self.user.username, upwd=self.sample_password)


class SeleniumChromeBaseTests(SeleniumBase):
    """
    This class define the necessary to develop and run functional tests.
    Create a user, store It in DB and log in on a selenium chrome browser.
    """

    def setUp(self):
        super(SeleniumChromeBaseTests, self).setUp()
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches",
                                        ["ignore-certificate-errors"])
        self.browser = webdriver.Chrome(
            executable_path=CHROMEDRV_PATH,
            chrome_options=options)
        self.browser.implicitly_wait(3)
        self.login_this_guy(uid=self.user.username, upwd=self.sample_password)


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui as UI


class DumbTests(object):

    def test_dumb(self):
        self.browser.get('%s/%s/' % (self.live_server_url, 'admin'))
        self.wait = UI.WebDriverWait(self.browser, 1)
        self.wait.until(EC.visibility_of_element_located(
            (By.ID, 'user-tools'))
        )
        tools = self.browser.find_element_by_id('user-tools')
        self.assertIn(self.user.first_name, tools.text)

    def test_dumb_2(self):
        self.browser.get('%s/%s/' % (self.live_server_url, 'admin'))
        self.wait = UI.WebDriverWait(self.browser, 1)
        self.wait.until(EC.visibility_of_element_located(
            (By.ID, 'user-tools'))
        )
        tools = self.browser.find_element_by_id('user-tools')
        self.assertIn('Welcome', tools.text)


class DumbFFxTests(DumbTests, SeleniumFirefoxBaseTests):
    pass


class DumbCHRTests(DumbTests, SeleniumChromeBaseTests):
    pass
