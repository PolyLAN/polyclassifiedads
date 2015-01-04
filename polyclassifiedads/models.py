from django.db import models
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
import datetime
import markdown
import bleach
import os


class Ad(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)  # If null, anonymous ad
    secret_key = models.CharField(max_length=128)  # Key for anonymous access

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    is_validated = models.BooleanField(default=False)  # Is the ad moderated by an admin ?
    is_deleted = models.BooleanField(default=False)  # Is the ad deleted ?

    title = models.CharField(max_length=255)
    content = models.TextField(_('Text of your ad'), help_text=_('You may use markdown to format your content.'))

    price = models.IntegerField(_('Price (CHF)'), blank=True, null=True, help_text=_('Optionnal price for your item'))

    online_date = models.DateField(blank=True, null=True, help_text=_('Starting date to display the ad. Leave empty to start as soon as the ad is validataed.'))
    offline_date = models.DateField(blank=True, null=True, help_text=_('Ending date to display the ad. Maximum 30 days from today.'))

    contact_email = models.EmailField(_('Contact\'s email'))
    contact_phone = models.CharField(_('Contact\'s phone'), max_length=32, blank=True, null=True)

    notifications_send = models.CharField(max_length=128, default='')  # List of type of notifications already sent

    CATEGORY_CHOICES = (
        ('pets', _('Pets & Accessories')),
        ('art', _('Art & Antiques')),
        ('audio', _('Audio - TV - Video')),
        ('cars', _('Cars')),
        ('jewelry', _('Jewelry & Timepieces')),
        ('tickets', _('Tickets & good')),
        ('diy', _('DIY and Gardening')),
        ('camp', _('Camping')),
        ('coll', _('Collections')),
        ('kids', _('Kids & Baby')),
        ('mov', _('Movies & DVD')),
        ('real', _('Real')),
        ('games', _('Games')),
        ('vgame', _('Video Games')),
        ('books', _('Books - Comics - Journal')),
        ('house', _('Household & House')),
        ('model', _('Models - Hobby')),
        ('moto', _('Motorcycle & Bike')),
        ('music', _('Music - Instruments')),
        ('comp', _('Computers & Office')),
        ('mov', _('Movies')),
        ('photo', _('Photography')),
        ('servi', _('Services')),
        ('headl', _('Health - Beauty')),
        ('sport', _('Sports')),
        ('tel', _('Telephony')),
        ('travel', _('Holidays - Travel')),
        ('cloth', _('Clothing & Accessories')),
        ('wine', _('Wines - Gastronomy')),
        ('misc', _('Misc')),
    )

    category = models.CharField(_('Category'), max_length=64, choices=CATEGORY_CHOICES)

    TYPE_CHOICES = (
        ('togive', _('To give away')),
        ('torent', _('To rent')),
        ('lookingfor', _('Looking for')),
        ('tosell', _('To sell'))
    )

    type = models.CharField(max_length=64, choices=TYPE_CHOICES)

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
    filter_types = models.CharField(max_length=128)
    filter = models.CharField(max_length=512)


class AdPhoto(models.Model):

    file = models.ImageField(upload_to='polyclassifiedads/photos')
    ad = models.ForeignKey(Ad, blank=True, null=True)

    def basename(self):
        return os.path.basename(self.file.path)


class AdSeen(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ad = models.ForeignKey(Ad)
    when = models.DateTimeField(auto_now_add=True)
