from django.core.management.base import BaseCommand

from polyclassifiedads.models import Ad, AdNotification
from django.utils import translation

import datetime
from polyclassifiedads.utils import send_templated_mail

from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Command(BaseCommand):
    args = 'type'
    help = 'Send ad notification'

    def handle(self, *args, **options):

        translation.activate('fr')

        self.stdout.write('Sending notifications for type "%s"' % (args[0],))

        now = datetime.date.today()

        # Build list of ad first (to do it quick for concurent modifications)
        ads = []
        for ad in Ad.objects.filter(is_validated=True, is_deleted=False, online_date__lte=now, offline_date__gte=now).exclude(notifications_send__contains=args[0]).order_by('-pk'):
            ad.notifications_send += ',%s' % (args[0],)
            ad.save()
            ads.append(ad)

        for adn in AdNotification.objects.filter(type=args[0]):

            ads_for_user = []

            for ad in ads:
                filter_ok = not adn.filter_categories and not adn.filter_types and not adn.filter

                if adn.filter_categories:
                    for c in adn.filter_categories.split(','):
                        if ad.category == c.strip():
                            filter_ok = True
                if adn.filter_types:
                    for c in adn.filter_types.split(','):
                        if ad.type == c.strip():
                            filter_ok = True
                if adn.filter:
                    for w in adn.filter.split(','):
                        if w in ad.title or w in ad.content or w in ' '.join([t.tag for t in ad.tags.all()]):
                            filter_ok = True

                if filter_ok:
                    ads_for_user.append(ad)

            if ads_for_user:
                send_templated_mail(_("AGEPoly's classified ads: New ads !"), settings.POLYCLASSIFIEDADS_EMAIL_FROM, [adn.user.email], 'notification', {'site': get_current_site(None), 'adn': adn, 'ads': ads})

        translation.deactivate()
