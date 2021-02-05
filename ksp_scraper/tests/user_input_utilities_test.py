import unittest
from unittest import mock
import user_input_utilities
import consts


class TestUserInputUtilities(unittest.TestCase):

    def test_input_link(self):
        with mock.patch('builtins.input', return_value="https://ksp.co.il/?ref=mobileToDesktop&uin=68851"):
            self.assertEqual(user_input_utilities.input_link(), "https://ksp.co.il/?ref=mobileToDesktop&uin=68851")

        with mock.patch('builtins.input', return_value="www.ksp.co.il/?ref=mobileToDesktop&uin=68851"):
            with self.assertRaisesRegex(Exception, consts.LINK_ERROR_MESSAGE):
                user_input_utilities.input_link()

    def test_input_target_price(self):
        with mock.patch('builtins.input', return_value="10"):
            self.assertEqual(user_input_utilities.input_target_price(), 10)

        with self.assertRaises(Exception):
            with mock.patch('builtins.input', return_value="10.4"):
                user_input_utilities.input_target_price()

        with self.assertRaises(Exception):
            with mock.patch('builtins.input', return_value="tdcc"):
                user_input_utilities.input_target_price()

    def test_input_user_email(self):
        with mock.patch('builtins.input', return_value="gmail.com"):
            with self.assertRaisesRegex(Exception, consts.USER_EMAIL_ERROR_MESSAGE):
                user_input_utilities.input_user_email()

        with mock.patch('builtins.input', return_value="gmail@gmail.com"):
            self.assertEqual(user_input_utilities.input_user_email(), "gmail@gmail.com")

        with mock.patch('builtins.input', return_value="name@bezeq.com"):
            self.assertEqual(user_input_utilities.input_user_email(), "name@bezeq.com")

    def test_check_valid_email(self):
        self.assertEqual(user_input_utilities.check_valid_email('gmail@gmail.com'), True)
        self.assertEqual(user_input_utilities.check_valid_email('name@bezeq.com'), True)
        self.assertEqual(user_input_utilities.check_valid_email('gmailgmail.com'), False)

    def test_input_user_password(self):
        with mock.patch('builtins.input', return_value="secret"):
            self.assertEqual(user_input_utilities.input_user_password(), "secret")
        with mock.patch('builtins.input', return_value="secret12"):
            self.assertEqual(user_input_utilities.input_user_password(), "secret12")

    @mock.patch('builtins.input', side_effect=["secret", "secret", "no", "yes", "ok", "ok"])
    def test_input_user_password_sign_up(self, side_effect):
        self.assertEqual(len(user_input_utilities.input_user_password_sign_up()), 192)
        self.assertEqual(user_input_utilities.input_user_password_sign_up(), "Wrong")
        self.assertEqual(len(user_input_utilities.input_user_password_sign_up()), 192)
