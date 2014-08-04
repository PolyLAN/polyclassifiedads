from django.db import models
from django.conf import settings


class Ad(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)  # If null, anonymous ad
    secret_key = models.CharField(max_length=128)  # Key for anonymous access

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    online_date = models.DateTimeField(blank=True, null=True)  # Starting date to display the ad
    offline_date = models.DateTimeField(blank=True, null=True)  # Endind date to display the ad

    is_validated = models.BooleanField(default=False)  # Is the ad moderated by an admin ?
    is_deleted = models.BooleanField(default=False)  # Is the ad deleted ?

    title = models.CharField(max_length=255)
    content = models.TextField()

    contact_email = models.EmailField()
    contact_phone = models.TextField(max_length=32, blank=True, null=True)

    tags = models.ManyToManyField('AdTag', related_name='ads')


class AdTag(models.Model):

    tag = models.CharField(max_length=255)
