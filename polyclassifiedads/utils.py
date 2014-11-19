from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.conf import settings

import hmac
import hashlib


def send_templated_mail(subject, email_from, emails_to, template, context):
    """Send a email using an template (both in text and html format)"""

    plaintext = get_template('polyclassifiedads/emails/%s.txt' % (template, ))
    htmly = get_template('polyclassifiedads/emails/%s.html' % (template, ))

    d = Context(context)

    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, email_from, emails_to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def generate_secret_rss_key(user):
    """Generate a secret key from user for RSS"""
    return hmac.new(settings.POLYCLASSIFIEDADS_RSS_SECRET, u''.join([str(user.pk), user.username]), hashlib.sha224).hexdigest()


def check_secret_rss_key(user, key):
    return hmac.compare_digest(generate_secret_rss_key(user), key.encode('utf-8'))
