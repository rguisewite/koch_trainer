#!/usr/bin/env python

from setuptools import setup, find_packages

required_modules = [
	'audiogen',
	'PyAudio',
]

with open( "README.md", "rb" ) as f:
	readme = f.read()

setup(
	name="koch_trainer",
	version="0.0.2",
	description="Koch method Morse code training program with Word Mode, Callsign Mode, and Random Character Mode",
	author="Ryan Guisewite",
	author_email="ryan.guisewite@gmail.com",
	url="https://github.com/rguisewite/koch_trainer",

	packages=find_packages(),
	install_requires=required_modules,

	entry_points={
		"console_scripts": [
			"koch_trainer = koch_trainer.koch_trainer:main"
		]
	},

	long_description=readme,
	classifiers=[
		"Environment :: Console",
		"Topic :: Multimedia :: Sound/Audio",
		"Topic :: Communications :: Ham Radio",
		"Programming Language :: Python :: 2.7",
	]
)
