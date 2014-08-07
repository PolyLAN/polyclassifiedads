# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Ad
from .forms import AdForm


def home(request):

    return render_to_response('polyclassifiedads/home.html', {}, context_instance=RequestContext(request))


@login_required
def edit(request, id):
    """Allow a logged user to edit/add an ad"""

    try:
        object = Ad.objects.get(pk=id, author=request.user, is_deleted=False)
    except:
        object = Ad()

    object.author = request.user

    if request.method == 'POST':  # If the form has been submitted...
        form = AdForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, _('The ad has been saved !'))

            return redirect('polyclassifiedads.views.show', id=object.pk)
    else:
        form = AdForm(instance=object)

    date_format = form.fields['offline_date'].widget.format.replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd')

    return render_to_response('polyclassifiedads/myads/edit.html', {'form': form, 'date_format': date_format}, context_instance=RequestContext(request))


@login_required
def show(request, id):

    pass


@login_required
def delete(request, id):

    pass


@login_required
def put_offline(request, id):

    pass


@login_required
def my_ads(request):
    """Display ads of the current user"""

    liste = Ad.objects.filter(author=request.user, is_deleted=False)

    return render_to_response('polyclassifiedads/myads/list.html', {'liste': liste}, context_instance=RequestContext(request))
