"""

Top Heros:

section#top-heroes-section
> div > select - data row headers
> div >

"""
import re
import datetime
from bs4 import BeautifulSoup
from enum import Enum
from collections import namedtuple


# if psn or xbl, region is "global"
class Platform(Enum):
    pc = "pc"
    psn = "psn"
    xbl = "xbl"


class PCRegion(Enum):
    us = "us"
    eu = "eu"
    kr = "kr"
    cn = "cn"


class CONRegion(Enum):
    glob = "global"


class Map(dict):
    """
    http://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class BattleTag:

    def __init__(self, platform, region, username, discriminator):
        self.username = username
        self.discriminator = discriminator
        self.platform = Platform(platform) if platform else None
        if self.platform is Platform.psn or self.platform is Platform.xbl:
            self.region = CONRegion(region)
        elif self.platform is Platform.pc:
            self.region = PCRegion(region)
        else:
            self.region = None

    def __repr__(self):
        return ("<{0.__module__}.{0.__class__.__name__} "
                "{0.platform}-{0.region} {0.username}#{0.discriminator}>".format(self))

    def __str__(self):
        return "{0.platform.value}-{0.region.value} {0.username}#{0.discriminator}".format(self)

    def __iter__(self):
        for i in ["platform", "region", "username", "discriminator"]:
            yield (i, getattr(self, i))

    @property
    def profile_url(self):
        return ("https://playoverwatch.com/en-us/career/"
                "{0.platform.value}/{0.region.value}/{0.username}-{0.discriminator}".format(self))

    @property
    def tag(self):
        return "{0.platform.value}/{0.region.value}/{0.username}#{0.discriminator}".format(self)

    @property
    def tag_private(self):
        return "{0.platform.value}-{0.region.value} {0.username}".format(self)

    @property
    def is_complete(self):
        return self.region is not None and self.platform is not None

    @staticmethod
    def from_tag(a_str):
        res = re.match(
            r"(?:(?P<platform>.*)/(?P<region>.*)/)?(?P<username>.*)#(?P<discriminator>.*)", a_str)

        if not res or len(res.groups()) != 4:
            raise ValueError(
                "BattleTag must be of format '<platform>/<region>/username#number' or 'username#number'")

        return BattleTag(res.group("platform"), res.group("region"), res.group("username"), res.group("discriminator"))


class OverwatchProfile(Map):

    @staticmethod
    def from_html(battletag, content):
        soup = BeautifulSoup(content, "html.parser")

        o = OverwatchProfile()
        o.tag = battletag
        o.parse_acct_info(soup)
        o.parse_stats(soup)

        return o

    def parse_acct_info(self, elem):
        self.portrait_url = elem.find(lambda x: x.has_attr(
            'class') and 'player-portrait' in x['class'])['src']

        lvl_rnk = filter(lambda x: bool(x.name), elem.find(lambda x: x.has_attr(
            'class') and 'masthead-player-progression' in x['class']).children)
        level = next(lvl_rnk)
        self.level = int(level.div.string.strip())

        try:
            rank = next(lvl_rnk)
        except StopIteration:
            pass
        else:
            self.rank = int(rank.div.string.strip())

    def parse_stats(self, soup):
        quick_play = soup.find(lambda x: x.has_attr(
            'id') and x['id'] == 'quickplay')

        if not quick_play.find(lambda x: x.has_attr("class") and 'highlights-section' in x['class']).h6:
            self['quick_play'] = self.parse_stats_section(quick_play)

        competitive_play = soup.find(lambda x: x.has_attr('id') and x[
                                     'id'] == "competitive")

        if not competitive_play.find(lambda x: x.has_attr("class") and 'highlights-section' in x['class']).h6:
            self['competitive_play'] = self.parse_stats_section(
                competitive_play)

        achievements = soup.find(lambda x: x.has_attr('id') and x[
                                 'id'] == 'achievements-section')

        self['achievements'] = self.parse_achievements(achievements)

    def parse_stats_section(self, elem):
        return self.parse_career_section(elem.find(lambda x: x.has_attr('class') and 'career-stats-section' in x['class']))

    def parse_career_section(self, elem):
        children = filter(lambda x: bool(x.name), elem.div.children)
        options_section = next(children)
        headers = (entry.string.strip().lower().replace(" ", "_")
                   for entry in options_section.findAll('option'))

        next(children)
        hero_sections = children

        career_section = Map()

        for hero_section in filter(lambda x: x.name, hero_sections):
            current_hero = next(headers)

            career_section[current_hero] = Map()

            for card_block in filter(lambda x: x.name, hero_section.children):
                card_table = card_block.table

                card_name = card_table.thead.th.h5.string.lower().strip()

                career_section[current_hero][card_name] = Map()

                for row in filter(lambda x: x.name, card_table.tbody.children):
                    name, value = (x.string.strip()
                                   for x in filter(lambda x: x.name, row.children))

                    name = self.transform_card_entry_name(card_name, name)
                    value = self.transform_card_entry_value(name, value)

                    career_section[current_hero][card_name][name] = value

        return career_section

    def transform_card_entry_name(self, card_name, val):
        val = val.lower().replace(" ", "_")

        if val.startswith("medals") or "Hero" in card_name:
            # If in hero specific section, we do want the average/etc. info.
            return val.replace("_-_", "_")
        else:
            # If we're in an "Average" section etc., we don't want to have to
            # repeat average/best/etc.
            return val.split('_-_', maxsplit=1)[0]

    def transform_card_entry_value(self, name, val):
        if "%" in val:
            val = int(val.replace("%", "")) / 100.0
        elif "time" in name:
            precise_time = re.match(
                r"(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)", val)

            if precise_time:
                val = datetime.timedelta(seconds=(int(precise_time.group("hours") or 0) * 60 + int(
                    precise_time.group("minutes"))) * 60 + int(precise_time.group("seconds")))
            else:
                less_precise_time = re.match(
                    r'(?P<hours>\d+) hours?|(?P<minutes>\d+) minutes?', val)
                if less_precise_time:
                    val = datetime.timedelta(seconds=int(less_precise_time.group(
                        "hours") or 0) * 60 * 60 + int(less_precise_time.group("minutes") or 0) * 60)
        else:
            val = val.replace(',', '')
            try:
                val = int(val)
            except ValueError:
                val = float(val)

        return val

    def parse_achievements(self, elem):
        children = filter(lambda x: bool(x.name), elem.div.children)
        options_section = next(children)

        headers = (option.string.strip().lower().replace(" ", "_")
                   for option in options_section.findAll("option"))
        achievements_elem = next(children)

        achievements = Map()

        for achievement_section in filter(lambda x: x.name, achievements_elem.children):
            section = next(headers)
            for achievement_elem in filter(lambda x: x.name, achievement_section.ul.children):
                achieved = 'm-disabled' not in achievement_elem.find(
                    lambda x: x.name == 'div' and x.has_attr('class') and 'achievement-card' in x['class'])['class']
                name = achievement_elem.h6.string.strip()
                description = achievement_elem.p.string.strip()
                url = achievement_elem.img['src']

                achievements[name.lower().replace(" ", "_")] = Achievement(
                    name, description, achieved, url, section)

        return achievements


Achievement = namedtuple(
    "Achievement", ["name", "description", "achieved", "image_url", "section"])
