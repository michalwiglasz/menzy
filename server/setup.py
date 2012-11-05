# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


authors = [
    u'Michal Wiglasz',
]


install_requires = [
    'beautifulsoup4',
    'requests',
    'flask',
    'simplejson',
]


setup(
    name='menzy',
    version='1',
    author=', '.join(authors),
    url='http://menzy.michalwiglasz.cz',
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    include_package_data=True,
)
