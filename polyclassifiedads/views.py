# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q


import datetime
import json
from math import log10

from .models import Ad, AdTag, AdNotification
from .forms import AdForm, AnonymousAdForm
from .utils import send_templated_mail, check_secret_rss_key

from django.contrib.sites.models import get_current_site
from django.contrib.auth import get_user_model

import uuid


def home(request):

    return render_to_response('polyclassifiedads/home.html', {}, context_instance=RequestContext(request))


@login_required
def browse(request):

    tag = request.GET.get('tag', '')
    typ = request.GET.get('typ', '')
    cat = request.GET.get('cat', '')
    q = request.GET.get('q', '')

    now = datetime.date.today()

    liste = Ad.objects.filter(is_validated=True, is_deleted=False, online_date__lte=now, offline_date__gte=now).order_by('-last_modification_date')

    if tag:
        liste = liste.filter(tags__tag=tag)
    if q:
        liste = liste.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(contact_email__icontains=q))
    if typ:
        liste = liste.filter(type=typ)
    if cat:
        liste = liste.filter(category=cat)

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

    tags = map(lambda t: (t, int((log10(t.count) / log10(total + 1)) * (max_size - min_size) + min_size)), tags)

    return render_to_response('polyclassifiedads/browse.html', {'liste': liste, 'tag': tag, 'tags': tags, 'q': q, 'typ': typ, 'cat': cat, 'TYPE_CHOICES': Ad.TYPE_CHOICES, 'CATEGORY_CHOICES': Ad.CATEGORY_CHOICES}, context_instance=RequestContext(request))


@login_required
def edit(request, id):
    return _edit(request, id, AdForm)


def _edit(request, id, Form, secret_key=None):
    """Allow a logged user to edit/add an ad"""

    if not secret_key and not request.user.pk:
        raise Http404

    try:
        object = Ad.objects.get(pk=id, is_deleted=False)

        if not request.user.is_staff and ((not secret_key and (object.author != request.user or object.secret_key)) or (secret_key and (object.secret_key != secret_key or object.author))):
            raise Http404
    except:
        object = Ad(offline_date=datetime.date.today() + datetime.timedelta(days=30))

        if not secret_key:
            object.author = request.user
        else:
            object.secret_key = secret_key

    if request.method == 'POST':  # If the form has been submitted...
        form = Form(request.POST, instance=object)

        tags = request.POST.get('tags')

        if form.is_valid():  # If the form is valid
            was_a_new_object = not form.instance.pk
            object = form.save()

            object.tags.clear()

            for t in tags.split(','):
                if t.strip():
                    tag, __ = AdTag.objects.get_or_create(tag=t.strip())
                    object.tags.add(tag)

            messages.success(request, _('The ad has been saved !'))

            if object.is_validated:
                object.is_validated = False
                object.save()

                messages.warning(request, _('The ad has been put offline until validation !'))

                send_templated_mail(_('AGEPoly\'s classified ads: Ad ID %s need to be validated again') % (object.id,), settings.POLYCLASSIFIEDADS_EMAIL_FROM, [settings.POLYCLASSIFIEDADS_EMAIL_MANAGERS], 'ad_to_revalidate', {'ad': object, 'site': get_current_site(request)})
            else:

                send_templated_mail(_('AGEPoly\'s classified ads: New ad with ID %s need to be validated') % (object.id,), settings.POLYCLASSIFIEDADS_EMAIL_FROM, [settings.POLYCLASSIFIEDADS_EMAIL_MANAGERS], 'new_ad_to_validate', {'ad': object, 'site': get_current_site(request)})

            if secret_key and was_a_new_object:
                send_templated_mail(_('AGEPoly\'s classified ads: New ad (%s)') % (object.title,), settings.POLYCLASSIFIEDADS_EMAIL_FROM, [object.contact_email], 'external_ad', {'ad': object, 'site': get_current_site(request)})

            if secret_key:
                r = redirect('polyclassifiedads.views.external_show', id=object.pk)

                key, val = r._headers['location']

                r._headers['location'] = (key, '%s?secret_key=%s' % (val, secret_key,))  # Todo: Hackpourri

                return r
            return redirect('polyclassifiedads.views.show', id=object.pk)
    else:
        form = Form(instance=object)

        tags = ','.join([tag.tag for tag in object.tags.all()]) if object.pk else ''

    date_format = form.fields['offline_date'].widget.format.replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd')

    return render_to_response('polyclassifiedads/myads/edit.html', {'form': form, 'date_format': date_format, 'tags': tags, 'secret_key': secret_key}, context_instance=RequestContext(request))


@login_required
def show(request, id):
    return _show(request, id)


def _show(request, id, secret_key=None):

    ad = get_object_or_404(Ad, pk=id, is_deleted=False)

    if not ad.can_edit(request.user, secret_key):
        if not ad.is_validated or ad.online_date > datetime.date.today() or ad.offline_date < datetime.date.today():
            raise Http404
        can_edit = False

        if not request.user.pk:
            raise Http404
    else:
        can_edit = True

    return render_to_response('polyclassifiedads/show.html', {'ad': ad, 'secret_key': secret_key, 'can_edit': can_edit, 'site': get_current_site(request)}, context_instance=RequestContext(request))


@login_required
def delete(request, id):
    return _delete(request, id)


def _delete(request, id, secret_key=None):

    ad = get_object_or_404(Ad, pk=id, is_deleted=False)

    if not ad.can_edit(request.user, secret_key):
        raise Http404

    if request.method == 'POST':

        ad.is_deleted = True
        ad.save()
        messages.success(request, _('The ad has been deleted !'))

        if secret_key:
            return redirect('polyclassifiedads.views.home')
        return redirect('polyclassifiedads.views.my_ads')

    return render_to_response('polyclassifiedads/myads/delete.html', {'ad': ad, 'secret_key': None}, context_instance=RequestContext(request))


@login_required
def put_offline(request, id):
    return _put_offline(request, id)


def _put_offline(request, id, secret_key=None):

    ad = get_object_or_404(Ad, pk=id, is_deleted=False)

    if not ad.can_edit(request.user, secret_key):
        raise Http404

    if request.method == 'POST':

        ad.offline_date = datetime.date.today() - datetime.timedelta(days=1)
        ad.save()
        messages.success(request, _('The ad has been put offline !'))

        if secret_key:
            return redirect('polyclassifiedads.views.home')
        return redirect('polyclassifiedads.views.my_ads')

    return render_to_response('polyclassifiedads/myads/put_offline.html', {'ad': ad, 'secret_key': None}, context_instance=RequestContext(request))


@login_required
def my_ads(request):
    """Display ads of the current user"""

    liste = Ad.objects.filter(author=request.user, is_deleted=False).order_by('-pk')

    return render_to_response('polyclassifiedads/myads/list.html', {'liste': liste}, context_instance=RequestContext(request))


def search_in_tags(request):

    q = request.GET.get('q')

    retour = []

    for tag in AdTag.objects.filter(tag__istartswith=q)[:20]:
        retour.append({'id': tag.tag, 'text': tag.tag})

    return HttpResponse(json.dumps(retour), content_type='text/json')


@login_required
@staff_member_required
def unvalidated_list(request):

    liste = Ad.objects.filter(is_validated=False, is_deleted=False).order_by('pk').all()

    return render_to_response('polyclassifiedads/unvalidated.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def validate(request, id):

    ad = get_object_or_404(Ad, pk=id, is_deleted=False)

    if request.method == 'POST':
        ad.is_validated = True
        ad.notifications_send = ''  # If needed, resend notifications

        if not ad.online_date:
            ad.online_date = datetime.date.today()

        ad.save()

        send_templated_mail(_('AGEPoly\'s classified ads: Your ad \'%s\' has been validated !') % (ad.title,), settings.POLYCLASSIFIEDADS_EMAIL_FROM, [ad.author.email if ad.author else ad.contact_email], 'ad_validated', {'ad': ad, 'site': get_current_site(request)})

        messages.success(request, _('The ad is now validated !'))

        return redirect('polyclassifiedads.views.unvalidated_list')
    return render_to_response('polyclassifiedads/validate.html', {'ad': ad}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def unvalidate(request, id):

    ad = get_object_or_404(Ad, pk=id, is_deleted=False)

    if request.method == 'POST':
        ad.is_validated = False
        ad.save()

        messages.success(request, _('The ad is now unvalidated !'))

        return redirect('polyclassifiedads.views.unvalidated_list')
    return render_to_response('polyclassifiedads/unvalidate.html', {'ad': ad}, context_instance=RequestContext(request))


@login_required
def notifications(request):

    if request.method == 'POST':

        if request.POST.get('action') == 'create':
            AdNotification.objects.get_or_create(user=request.user, type=request.POST.get('type'))
            messages.success(request, _('Notification activated !'))

        if request.POST.get('action') == 'delete':
            adn, __ = AdNotification.objects.get_or_create(user=request.user, type=request.POST.get('type'))
            adn.delete()
            messages.success(request, _('Notification desactivated !'))

        if request.POST.get('action') == 'save':
            adn, __ = AdNotification.objects.get_or_create(user=request.user, type=request.POST.get('type'))
            adn.filter_types = request.POST.get('types')
            adn.filter_categories = request.POST.get('categories')
            adn.filter = request.POST.get('words')
            adn.save()

            messages.success(request, _('Filter saved !'))

    try:
        daily = AdNotification.objects.get(user=request.user, type='daily')
    except AdNotification.DoesNotExist:
        daily = None

    try:
        weekly = AdNotification.objects.get(user=request.user, type='weekly')
    except AdNotification.DoesNotExist:
        weekly = None

    return render_to_response('polyclassifiedads/notifications.html', {'daily': daily, 'weekly': weekly, 'CATEGORY_CHOICES': Ad.CATEGORY_CHOICES, 'TYPE_CHOICES': Ad.TYPE_CHOICES}, context_instance=RequestContext(request))


def search_in_categories(request):

    q = request.GET.get('q')

    retour = []

    for (val, text) in Ad.CATEGORY_CHOICES:
        if q in text:
            retour.append({'id': val, 'text': unicode(text)})

    return HttpResponse(json.dumps(retour), content_type='text/json')


def search_in_types(request):

    q = request.GET.get('q')

    retour = []

    for (val, text) in Ad.TYPE_CHOICES:
        if q in text:
            retour.append({'id': val, 'text': unicode(text)})

    return HttpResponse(json.dumps(retour), content_type='text/json')


def external_edit(request, id):
    secret_key = request.GET.get('secret_key', str(uuid.uuid4()))

    return _edit(request, id, AnonymousAdForm, secret_key)


def external_show(request, id):
    secret_key = request.GET.get('secret_key')

    if not secret_key:
        raise Http404

    return _show(request, id, secret_key)


def external_delete(request, id):
    secret_key = request.GET.get('secret_key')

    if not secret_key:
        raise Http404

    return _delete(request, id, secret_key)


def external_put_offline(request, id):
    secret_key = request.GET.get('secret_key')

    if not secret_key:
        raise Http404

    return _put_offline(request, id, secret_key)


def rss(request, user_id, key):
    """Return a RSS feed with lastest ads"""

    from .feeds import LatestAdFeed  # Need to be imported later to allow resolution of urls in the class

    if not check_secret_rss_key(get_object_or_404(get_user_model(), pk=user_id), key):
        raise Http404

    return LatestAdFeed()(request)
