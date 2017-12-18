import unittest

import requests
import pachimari


class ParseTest(unittest.TestCase):

    def test_do_not_crash(self):
        bt = pachimari.BattleTag('pc', 'us', 'khazhyk', '1819')

        with requests.get(bt.profile_url) as resp:
            prof = pachimari.OverwatchProfile.from_html(
                bt, resp.text)
