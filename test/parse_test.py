import unittest

import requests
import pachimari


class ParseTest(unittest.TestCase):

    def test_do_not_crash(self):
        bt = pachimari.BattleTag('pc', 'us', 'khazhyk', '1819')

        with requests.get(bt.profile_url) as resp:
            prof = pachimari.OverwatchProfile.from_html(
                bt, resp.text)

    def test_private_profile(self):
        bt = pachimari.BattleTag('pc', 'us', 'khazhyk', '1819')

        with open("test/test_data/sample_private.html", "r", encoding="utf8") as f:
            prof = pachimari.OverwatchProfile.from_html(bt, f.read())

        self.assertTrue(prof.private)
        self.assertEqual(prof.level, 33)
