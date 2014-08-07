from django.forms import ModelForm, ValidationError
import datetime

from .models import Ad
from django.utils.translation import ugettext_lazy as _


class AdForm(ModelForm):
    class Meta:
        model = Ad
        exclude = ('author', 'secret_key', 'creation_date', 'last_modification_date', 'is_validated', 'is_deleted', 'tags')

    def __init__(self, *args, **kwargs):
        super(AdForm, self).__init__(*args, **kwargs)

    def clean_offline_date(self):

        data = self.cleaned_data['offline_date']

        if data and (data - datetime.timedelta(days=61)) > datetime.date.today():
            raise ValidationError(_('Offline date is too far in the futur: Maximum 60 days !'))

        return data
