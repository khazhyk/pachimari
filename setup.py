from setuptools import setup, find_packages

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(
    name="pachimari",
    version="0.0.0",
    author="khazhyk",
    url="https://github.com/khazhyk/osuapi",
    license="MIT",
    keywords="osu",
    install_requires=[requirements],
    packages=find_packages(),
    description="osu! api wrapper.",
    classifiers=[
      "Development Status :: 1 - Planning",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Topic :: Utilities"
    ]
)
