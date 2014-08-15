from django.forms import ModelForm, ValidationError
import datetime

from .models import Ad
from django.utils.translation import ugettext_lazy as _


class AdForm(ModelForm):
    class Meta:
        model = Ad
        exclude = ('author', 'secret_key', 'creation_date', 'last_modification_date', 'is_validated', 'is_deleted', 'tags', 'notifications_send')

    def __init__(self, *args, **kwargs):
        super(AdForm, self).__init__(*args, **kwargs)

    def clean_offline_date(self):

        data = self.cleaned_data['offline_date']

        if data and (data - datetime.timedelta(days=31)) > datetime.date.today():
            raise ValidationError(_('Offline date is too far in the futur: Maximum 30 days !'))

        return data

    def clean_contact_phone(self):
        data = self.cleaned_data['contact_phone']

        if not data and not self.instance.author:
            raise ValidationError(_('You must set an contact phone as you\'re not logged in !'))

        return data
