from setuptools import setup, find_packages
from pachimari import __version__ as version, __title__ as name, __author__ as author, __license__ as license

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(
    name=name,
    version=version,
    author=author,
    url="https://github.com/khazhyk/osuapi",
    license="MIT",
    keywords="osu",
    requirements=requirements,
    packages=find_packages(),
    description="osu! api wrapper.",
    classifiers=[
      "Development Status :: 1 - Planning",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Topic :: Utilities"
    ]
)
