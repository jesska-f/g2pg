import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))
description = 'Google Sheets to Postgres DB using gspread and env files.'

# Import the README and use it as the long-description.
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = description


with open(os.path.join(here, "requirements.txt"),"r") as f:
    requirements = [line.strip() for line in f.readlines()]


setuptools.setup(
    name="g2pg",
    version="1.2.5",
    license = 'MIT',
    author="Jessica Franks",
    author_email="hello@jesska.co.za",
    url = 'https://github.com/jesska-f/g2pg',
    keywords = ['pandas','postgres','gspread','gsheets'],
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['g2pg'],
    install_requires= requirements,
    classifiers=["Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"])