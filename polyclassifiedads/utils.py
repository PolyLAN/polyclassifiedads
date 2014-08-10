from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


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
