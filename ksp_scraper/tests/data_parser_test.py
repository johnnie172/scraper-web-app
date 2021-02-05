import unittest
import data_parser
import consts
from decimal import Decimal
from bs4 import BeautifulSoup


class TestDataParser(unittest.TestCase):

    def test_get_title_and_price(self):
        with open('source_text.txt') as source_text:
            source_text_beautiful = BeautifulSoup(source_text, 'lxml')
            self.assertEqual(data_parser.get_title_and_price(source_text_beautiful),
                             ("עכבר גיימרים Corsair HARPOON RGB PRO FPS/MOBA", "165 ₪"))

        with open('source_text_no_item.txt') as source_text:
            source_text_beautiful = BeautifulSoup(source_text, 'lxml')
            self.assertEqual(data_parser.get_title_and_price(source_text_beautiful), None)
            self.assertRaises(Exception, data_parser.get_title_and_price(source_text_beautiful))

    def test_change_price_from_str_to_decimal(self):
        self.assertEqual(data_parser.change_price_from_str_to_decimal("10.1"), Decimal("10.1"))
        self.assertEqual(data_parser.change_price_from_str_to_decimal("160 $"), Decimal("160"))
        self.assertEqual(data_parser.change_price_from_str_to_decimal("10.1 ₪"), Decimal("10.1"))

    def test_parse_uin_from_url(self):
        self.assertEqual(data_parser.parse_uin_from_url('https://ksp.co.il/?uin=68851'), '68851')
        self.assertEqual(data_parser.parse_uin_from_url(
            'https://ksp.co.il/?select=.112.&kg=&list=1&sort=2&glist=0&uin=65850'), '65850')
        self.assertEqual(data_parser.parse_uin_from_url('https://ksp.co.il/?uin=68851aa111'), '68851')
        with self.assertRaisesRegex(Exception, consts.UIN_ERROR_MESSAGE):
            data_parser.parse_uin_from_url('')
