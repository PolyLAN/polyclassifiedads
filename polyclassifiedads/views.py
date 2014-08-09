# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Ad, AdTag
from .forms import AdForm
import datetime
import json
from math import log10


def home(request):

    return render_to_response('polyclassifiedads/home.html', {}, context_instance=RequestContext(request))


@login_required
def browse(request):

    tag = request.GET.get('tag', '')

    now = datetime.date.today()

    liste = Ad.objects.filter(is_validated=True, is_deleted=False, online_date__lte=now, offline_date__gte=now).order_by('-last_modification_date')

    if tag:
        liste = liste.filter(tags__tag=tag)

    paginator = Paginator(liste, 50)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        liste = paginator.page(page)
    except (EmptyPage, InvalidPage):
        liste = paginator.page(paginator.num_pages)

    # Tags
    min_size = 50
    max_size = 150

    tags = AdTag.objects.all()

    total = 0

    for t in tags:
        t.count = t.ads.filter(is_validated=True, is_deleted=False, online_date__lte=now, offline_date__gte=now).count()
        total += t.count

    tags = filter(lambda t: t.count, tags)

    tags = map(lambda t: (t, int((log10(t.count) / log10(total)) * (max_size - min_size) + min_size)), tags)

    return render_to_response('polyclassifiedads/browse.html', {'liste': liste, 'tag': tag, 'tags': tags}, context_instance=RequestContext(request))


@login_required
def edit(request, id):
    """Allow a logged user to edit/add an ad"""

    try:
        object = Ad.objects.get(pk=id, author=request.user, is_deleted=False)
    except:
        object = Ad(offline_date=datetime.date.today() + datetime.timedelta(days=60))

    object.author = request.user

    if request.method == 'POST':  # If the form has been submitted...
        form = AdForm(request.POST, instance=object)

        tags = request.POST.get('tags')

        if form.is_valid():  # If the form is valid
            object = form.save()

            object.tags.clear()

            for t in tags.split(','):
                if t.strip():
                    tag, __ = AdTag.objects.get_or_create(tag=t.strip())
                    object.tags.add(tag)

            messages.success(request, _('The ad has been saved !'))

            return redirect('polyclassifiedads.views.show', id=object.pk)
    else:
        form = AdForm(instance=object)

        tags = ','.join([tag.tag for tag in object.tags.all()]) if object.pk else ''

    date_format = form.fields['offline_date'].widget.format.replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd')

    return render_to_response('polyclassifiedads/myads/edit.html', {'form': form, 'date_format': date_format, 'tags': tags}, context_instance=RequestContext(request))


@login_required
def show(request, id):

    pass


@login_required
def delete(request, id):

    ad = get_object_or_404(Ad, pk=id, author=request.user, is_deleted=False)

    if request.method == 'POST':

        ad.is_deleted = True
        ad.save()
        messages.success(request, _('The ad has been deleted !'))
        return redirect('polyclassifiedads.views.my_ads')

    return render_to_response('polyclassifiedads/myads/delete.html', {'ad': ad}, context_instance=RequestContext(request))


@login_required
def put_offline(request, id):

    ad = get_object_or_404(Ad, pk=id, author=request.user, is_deleted=False)

    if request.method == 'POST':

        ad.offline_date = datetime.date.today() - datetime.timedelta(days=1)
        ad.save()
        messages.success(request, _('The ad has been put offline !'))
        return redirect('polyclassifiedads.views.my_ads')

    return render_to_response('polyclassifiedads/myads/put_offline.html', {'ad': ad}, context_instance=RequestContext(request))


@login_required
def my_ads(request):
    """Display ads of the current user"""

    liste = Ad.objects.filter(author=request.user, is_deleted=False)

    return render_to_response('polyclassifiedads/myads/list.html', {'liste': liste}, context_instance=RequestContext(request))


def search_in_tags(request):

    q = request.GET.get('q')

    retour = []

    for tag in AdTag.objects.filter(tag__istartswith=q)[:20]:
        retour.append({'id': tag.tag, 'text': tag.tag})

    return HttpResponse(json.dumps(retour), content_type='text/json')
