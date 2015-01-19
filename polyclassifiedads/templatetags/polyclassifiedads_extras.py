from django import template
from django.core.urlresolvers import reverse
from django.conf import settings

from polyclassifiedads.utils import generate_secret_rss_key

register = template.Library()


@register.simple_tag(takes_context=True)
def polyclassifiedads_rss_link(context):

    return reverse('polyclassifiedads.views.rss', args=(context['user'].pk, generate_secret_rss_key(context['user']),))


@register.assignment_tag(takes_context=True)
def polyclassifiedads_is_seen(context, ad):
    return ad.adseen_set.filter(user=context['user']).count()


@register.simple_tag()
def polyclassifiedads_loginurl():
    return settings.LOGIN_URL


@register.simple_tag()
def polyclassifiedads_abuseemail():
    return settings.POLYCLASSIFIEDADS_EMAIL_MANAGERS
