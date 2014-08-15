from django.db import models
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
import datetime
import markdown
import bleach


class Ad(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)  # If null, anonymous ad
    secret_key = models.CharField(max_length=128)  # Key for anonymous access

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    is_validated = models.BooleanField(default=False)  # Is the ad moderated by an admin ?
    is_deleted = models.BooleanField(default=False)  # Is the ad deleted ?

    title = models.CharField(max_length=255)
    content = models.TextField(_('Text of your ad'), help_text=_('You may use markdown to format your content.'))

    online_date = models.DateField(blank=True, null=True, help_text=_('Starting date to display the ad. Leave empty to start as soon as the ad is validataed.'))
    offline_date = models.DateField(blank=True, null=True, help_text=_('Ending date to display the ad. Maximum 30 days from today.'))

    contact_email = models.EmailField(_('Contact\'s email'))
    contact_phone = models.CharField(_('Contact\'s phone'), max_length=32, blank=True, null=True)

    notifications_send = models.CharField(max_length=128, default='')  # List of type of notifications already sent

    CATEGORY_CHOICES = (
        ('togive', _('To give away')),
        ('torent', _('To rent')),
        ('lookingfor', _('Looking for')),
        ('tosell', _('To sell'))
    )

    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES)

    tags = models.ManyToManyField('AdTag', related_name='ads')

    def is_online(self):
        if not self.is_validated:
            return False

        if self.online_date > datetime.date.today() or self.offline_date < datetime.date.today():
            return False

        return True

    def content_formated(self):
        """Return the formated content"""
        return bleach.clean(markdown.markdown(self.content, safe_mode='escape'), tags=bleach.ALLOWED_TAGS + ['p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'img'])

    def tags_for_list(self):
        return self.tags.all()[:10]

    def can_edit(self, user, secret_key):

        if user.is_staff:
            return True

        if self.author:
            return self.author == user

        if self.secret_key:
            return self.secret_key == secret_key


class AdTag(models.Model):

    tag = models.CharField(max_length=255)


class AdNotification(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    TYPE_CHOICES = (
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)

    filter_categories = models.CharField(max_length=128)
    filter = models.CharField(max_length=512)
