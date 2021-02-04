#!/usr/bin/env python

from setuptools import setup, find_packages
import pathlib

required_modules = [
	'audiogen @ https://github.com/rguisewite/audiogen/tarball/master',
	'PyAudio',
]

here				= pathlib.Path(__file__).parent.resolve()
long_description	= ( here / 'README.md' ).read_text( encoding='utf-8' )

setup(
	name='koch_trainer',
	version='0.0.4',
	description='Koch method Morse code training program with Word Mode, Callsign Mode, and Random Character Mode',
	author='Ryan Guisewite',
	author_email='ryan.guisewite@gmail.com',
	url='https://github.com/rguisewite/koch_trainer',

	packages=find_packages(),
	install_requires=required_modules,

	entry_points={
		'console_scripts': [
			'koch_trainer = koch_trainer.koch_trainer:main'
		]
	},

	long_description=long_description,
	classifiers=[
		'Environment :: Console',
		'Topic :: Multimedia :: Sound/Audio',
		'Topic :: Communications :: Ham Radio',
		'Programming Language :: Python :: 3.9',
	]
)
