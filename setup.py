#!/usr/bin/python

from distutils.core import setup

setup(
    name='PolyClassifiedAds',
    version='0.2',
    description='A small django application for classified ads at AGEPoly.',
    long_description='PolyClassifiedAds is a small django application used for classified ads at AGEPoly, the student association of EPFL.',
    author='Maximilien Cuony',
    author_email='theglu@theglu.org',
    url='https://github.com/PolyLAN/polyclassifiedads',
    download_url='https://github.com/PolyLAN/polyclassifiedads',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    packages=[
        'polyclassifiedads',
    ],
    include_package_data=True,
    install_requires=[
        'south',
        'django',
        'django-bootstrap3',
        'markdown',
        'bleach',
        'django-simple-captcha',
    ]
)
