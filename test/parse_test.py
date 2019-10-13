import unittest

import requests
import pachimari


class ParseTest(unittest.TestCase):

    def test_data_live(self):
        bt = pachimari.BattleTag('pc', 'us', 'fischer', '2188')

        with requests.get(bt.profile_url) as resp:
            prof = pachimari.OverwatchProfile.from_html(
                bt, resp.text)

        self.assertFalse(prof.private)
        # Assert some sections exist
        self.assertIn("all_heroes", prof.quick_play)
        self.assertIn("all_heroes", prof.competitive_play)
        self.assertTrue(
            {'best', 'assists', 'combat', 'game', 'average', 'miscellaneous', 'match awards'}
            <= set(prof.quick_play.all_heroes.keys()), prof.quick_play.all_heroes.keys())

        # Assert chevos exist
        self.assertIn("level_50", prof.achievements)

    def test_private_profile_local(self):
        bt = pachimari.BattleTag('pc', 'us', 'khazhyk', '1819')

        with open("test/test_data/sample_private.html", "r", encoding="utf8") as f:
            prof = pachimari.OverwatchProfile.from_html(bt, f.read())

        self.assertTrue(prof.private)
        self.assertEqual(prof.level, 33)

    def test_data_local(self):
        """Test that we parse the stats and chevos correctly."""
        bt = pachimari.BattleTag('pc', 'us', 'fischer', '2188')

        with open("test/test_data/sample.html", "r", encoding="utf8") as f:
            prof = pachimari.OverwatchProfile.from_html(
                bt, f.read())

        self.assertFalse(prof.private)
        # Assert some sections exist
        self.assertIn("all_heroes", prof.quick_play)
        self.assertIn("all_heroes", prof.competitive_play)
        self.assertTrue(
            {'best', 'assists', 'combat', 'game', 'average', 'miscellaneous', 'match awards'}
            <= set(prof.quick_play.all_heroes.keys()), prof.quick_play.all_heroes.keys())

        # Assert chevos exist
        self.assertIn("level_50", prof.achievements)
