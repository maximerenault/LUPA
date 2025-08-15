import unittest
from lupa.utils.strings import check_strint, check_strfloat, check_strfloat_pos


class TestStringUtils(unittest.TestCase):

    def test_check_strint(self):
        self.assertEqual(check_strint(""), "")
        self.assertEqual(check_strint("-"), "-")
        self.assertEqual(check_strint("-m080"), "-80")
        self.assertEqual(check_strint("123"), "123")
        self.assertEqual(check_strint("000123"), "123")
        self.assertEqual(check_strint("abc"), "")
        self.assertEqual(check_strint("-000"), "-0")

    def test_check_strfloat(self):
        self.assertEqual(check_strfloat(""), "")
        self.assertEqual(check_strfloat("-"), "-")
        self.assertEqual(check_strfloat("-m08.0.2"), "-8.02")
        self.assertEqual(check_strfloat("123.456"), "123.456")
        self.assertEqual(check_strfloat("000123.456"), "123.456")
        self.assertEqual(check_strfloat("abc"), "")
        self.assertEqual(check_strfloat("-000"), "-0")

    def test_check_strfloat_pos(self):
        self.assertEqual(check_strfloat_pos(""), "")
        self.assertEqual(check_strfloat_pos("-"), "")
        self.assertEqual(check_strfloat_pos("-m08.0.2"), "8.02")
        self.assertEqual(check_strfloat_pos("123.456"), "123.456")
        self.assertEqual(check_strfloat_pos("000123.456"), "123.456")
        self.assertEqual(check_strfloat_pos("abc"), "")
        self.assertEqual(check_strfloat_pos("000"), "0")
        self.assertEqual(check_strfloat_pos(".123"), ".123")
        self.assertEqual(check_strfloat_pos("123."), "123.")
        self.assertEqual(check_strfloat_pos("123.0.456"), "123.0456")


if __name__ == "__main__":
    unittest.main()
