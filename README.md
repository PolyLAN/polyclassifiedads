PolyClassifiedAds
=================

PolyClassifiedAds is a small django application used for classified ads at AGEPoly, the student association of EPFL.

## License

PolyClassifiedAds is distributed with the [BSD](http://opensource.org/licenses/BSD-2-Clause) license.

## Authors

PolyClassifiedAds has been developped by [Maximilien Cuony](https://github.com/the-glu) .

## Setup

### Install the package

`pip install https://github.com/PolyLAN/polyclassifiedads.git`

### Update your setttings

You need to activate this app, _bootstrap3_ and _south_.

Add to your INSTALLED_APPS:

```
    'polyclassifiedads',
    'south',
    'bootstrap3',
```

(Of course, you don't need to add a line twice if one app is already installed !)

### Set parameters

Add to your settings.py

```
POLYCLASSIFIEDADS_EMAIL_FROM = ''
POLYCLASSIFIEDADS_EMAIL_MANAGERS = ''
```

and update values as you need. The first one is the sender for all email send by the system and the second one is the email of someone who should be alerted e.g. to validate ads.

### Update your urls.py

Add something like this:

`url(r'^classifiedads/', include('polyclassifiedads.urls')),`

### Do the migrations

`python manage.py migrate`

### Notifications

To activate notifications, add something like this in your crontab:

```
00 04 * * * cd /var/www/project/ && /usr/bin/python2.7 manage.py ads_notifications daily
00 04 * * 1 cd /var/www/project/ && /usr/bin/python2.7 manage.py ads_notifications weekly
```
