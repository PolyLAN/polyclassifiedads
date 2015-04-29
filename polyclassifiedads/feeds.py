from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import datetime

from .models import Ad


class LatestAdFeed(Feed):
    title = _('Latest AGEPoly\'s classified ads')
    link = reverse('polyclassifiedads.views.home')
    description = _('Latest AGEPoly\'s classified ads')

    def items(self):
        now = datetime.date.today()
        liste = Ad.objects.filter(is_validated=True, is_deleted=False, online_date__lte=now, offline_date__gte=now).order_by('-last_modification_date')
        return liste[:10]

    def item_title(self, ad):
        return ad.title

    def item_description(self, ad):
        return ad.content_formated()

    def item_link(self, ad):
        return reverse('polyclassifiedads.views.show', args=(ad.pk,))

    def item_author_name(self, ad):
        return ad.author.get_full_name() if ad.author else 'Anonymous'

    def item_author_email(self, ad):
        return ad.contact_email
