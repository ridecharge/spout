from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.template import RequestContext, Context, Template


from datetime import datetime
from zipfile import ZipFile
import tempfile
import shutil
import json
import time
import re

from UploadHandlers import UploadRequestHandler
from GetRequestHandlers import GetRequestHandler
from urlFactory import UrlFactory
from AppDistribution.models import *
from AppDistribution import settings
from AppDistribution import forms


@csrf_exempt
def upload_build(request):

    ret_val = None

    if request.method == 'POST':
        form = forms.UploadBuildForm(request.POST, request.FILES)    
        if form.is_valid():

            handler = UploadRequestHandler(request)
            handler.process_upload()

            ret_val = HttpResponseRedirect("/")
        else:
            ret_val = HttpResponse(form.errors)
    else:
        form = forms.UploadBuildForm()
        ret_val = render_to_response("forms/upload.html",  {'form': form})
    return ret_val

@csrf_exempt
def post_crash(request):

    print request.body;
    
    if request.body:
        """
        temp_crash_path = tempfile.mkstemp()[1]

        crash_file = open(temp_crash_path, "w")
        crash_file.writelines(request.body)

        regx = re.compile("(.{8}-.{4}-.{4}-.{4}-.{12})")

        crash_file = open(temp_crash_path, "r")
        crashed_uuid = [regx.search(x) for x in crash_file.readlines() if regx.search(x)][0].groups()[0]

        tmp_decoded_crash, tmp_decoded_crash_loc = utils.decode_crash_report(temp_crash_path)
        print tmp_decoded_crash, tmp_decoded_crash_loc, temp_crash_path, crashed_uuid

        app = App.objects.get(uuid=crashed_uuid)

        """
        ipa_path = utils.ipa_path(app.uuid)
        dsym_path = utils.dsym_path(app.name, app.version)
        temp_path = tempfile.mkdtemp()

        crash_obj = json.loads(request.body)

        symbolicated_crash, symbolicated_crash_location = utils.symbolicate_crash(tmp_decoded_crash_loc, dsym_path, ipa_path)
        crash_file.close()
        print temp_crash_path, symbolicated_crash_location 

        shutil.copy(symbolicated_crash_location, "~/Desktop/crash19999.txt")

        
        
        return HttpResponse(content="OK!!")
    else:
        return HttpResponse(content="No crash data posted.")

def app_homepage(request):

    if request.user.is_authenticated() and request.user.main_page:
        return page(request, request.user.main_page.slug)
    else:
        main_page = SpoutSite.objects.get_current().home_page
        return page(request, main_page.slug)

def filtered_apps(request):

    if "application/json" in request.META['HTTP_ACCEPT']:

        request_keys = request.GET.keys()

        apps = App.objects
        return_many = True

        if 'device_type' in request_keys:
            apps = apps.filter(device_type=request.GET['device_type'].upper())

        if 'product' in request_keys:
            product = Product.objects.get(pk=request.GET['product'])
            apps = apps.filter(product=product)

        if 'tag' in request_keys:
            apps = apps.filter(tags__name=request.GET['tag'])

        if 'latest' in request_keys:
            apps = [apps.latest('creation_date')]
            return_many = False

        url_factory = UrlFactory(request)

        hdate = lambda(d): Template("{% load humanize %} {{ date|timesince }}").render(Context({'date': d})).lstrip()
        formdict = lambda(a): dict({'uuid' : a.uuid,
                                 'refdate' : hdate(a.creation_date),
                                 'url'     : url_factory.package_url(a),
                                 'img_path': a.icon.url.replace(settings.MEDIA_ROOT, "media"),
                                 'product' : a.product.pk,
                                    'name' : a.name,
                                    'device_type' : a.device_type,
                                    'version' : a.version,
                                    'comment' : a.comment,
                                    'note' : a.note,
                                    })
        if return_many:
            serializable_apps = [formdict(app) for app in apps.all()]
        else:
            serializable_apps = formdict(apps[0])

        serializable_app_dict = dict({
            'apps': serializable_apps,
            })
        print request.GET, serializable_app_dict

        json_string = json.dumps(serializable_app_dict)
        print json_string

        return HttpResponse(content=json_string, mimetype="application/json")


def latest_app_for_each_tag(request):

    request_keys = request.GET.keys()
    tags = Tag.objects

    if 'product' in request_keys:
        tags = tags.filter(apps__product__pk=request.GET['product'])
    if 'device_type' in request_keys:
        tags = tags.filter(apps__device_type=request.GET['device_type'].upper())

    def filter_t(t):
        apps = t.apps.all()
        if 'product' in request_keys:
            apps = apps.filter(product__pk=request.GET['product'])
        if 'device_type' in request_keys:
            apps = apps.filter(device_type=request.GET['device_type'].upper())
        return apps

    
    apps = []
    tagset = [dict({'name': t.name, 'app': filter_t(t).latest("creation_date")}) for t in tags.all().distinct() if filter_t(t).count()]
    tagset.sort(key=lambda(d): d['app'].creation_date, reverse=True)

    tags = [tag['name'] for tag in tagset]

    tag_dict = dict({ 'tags':
                tags })

    json_string = json.dumps(tag_dict)
    print tagset

    return render_to_response("filtered_apps.html", {'tag_info' : tagset },  context_instance=RequestContext(request))



def filtered_tags(request):

    request_keys = request.GET.keys()
    tags = Tag.objects

    if 'product' in request_keys:
        tags = tags.filter(apps__product__pk=request.GET['product'])
    if 'device_type' in request_keys:
        tags = tags.filter(apps__device_type=request.GET['device_type'].upper())

    def filter_t(t):
        apps = t.apps.all()
        if 'product' in request_keys:
            apps = apps.filter(product__pk=request.GET['product'])
        if 'device_type' in request_keys:
            apps = apps.filter(device_type=request.GET['device_type'].upper())
        return apps

    
    tagset = [dict({'tag': t.name, 'date': filter_t(t).latest("creation_date").creation_date}) for t in tags.all().distinct() if filter_t(t).count()]
    tagset.sort(key=lambda(d): d['date'], reverse=True)

    tags = [tag['tag'] for tag in tagset]

    tag_dict = dict({ 'tags':
                tags })

    json_string = json.dumps(tag_dict)

    return HttpResponse(content=json_string, mimetype="application/json")

def page(request, page_slug):

    page = Page.objects.get(slug=page_slug)
    if 'application/json' in request.META['HTTP_ACCEPT']:
       
        page_rows = []
        for row in page.pagerow_set.all():
            if row.app:

                app = row.app

                row_dict['product'] = row.product.name
                if app.icon_url:
                    row_dict['icon'] = app.icon_url
                else:
                    row_dict['icon'] = ""
                row_dict['version'] = app.version

                page_rows.append(row_dict)
            

        page_dict = {'title' : page.title,
                'heading' :  page.heading,
                'rows' : page_rows }
        content = json.dumps(page_dict)
        return HttpResponse(content=content, mimetype="application/json")

    else:
            
        if page.requires_auth == False:
                return render_to_response("page.html", {'page': page}, context_instance=RequestContext(request))
        elif (page.requires_auth and request.user.is_authenticated()):

            if page in request.user.allowed_pages.all():
                return render_to_response("page.html", {'page': page}, context_instance=RequestContext(request))
            else:
                return HttpResponse(content="You are not authorized to view this page.")
            """ 

            if request.user.groups.filter(spoutuser__groups=page.allowed_groups.all()).count() > 0:
                return render_to_response("page.html", {'page': page}, context_instance=RequestContext(request))
            else:
                return HttpResponse(content="You are not authorized to view this page.")
            """
            
        elif request.user.is_authenticated() == False: 
            return HttpResponseRedirect("/accounts/login/?next=%s" % request.path)


def asset_redirect(request, uuid):

    app = App.objects.get(uuid=uuid)
    url = UrlFactory(request).package_url(app)
    return HttpResponseRedirect(url)
   
def apps(request):

    if request.user.is_authenticated():
        apps = App.objects.all().order_by('-creation_date')
        auth = "logout"
    else:
        apps = App.objects.all().order_by('-creation_date')
        auth = "login"

    host = request.get_host()
    tags = Tag.objects.all()


    return render_to_response("appstore_index.html", {'apps': apps,
        'host': host,
        'auth': auth,
        'tags': tags},
        context_instance=RequestContext(request))

def tagged_apps(request, tag_name):


    ret_val = None
    apps = App.objects.filter(tags__name=tag_name).order_by('-creation_date')
    host = request.get_host()

    if request.META['HTTP_ACCEPT'] == "application/json":

        app_info = [dict({'uuid': app.uuid, 'creation_ref': Template("{% load humanize %} {{ date|naturaltime }}").render(Context({'date': app.creation_date})).lstrip()}) for app in apps]

        json_dict = dict({ 
            'apps': app_info
        })

        json_string = json.dumps(json_dict)
        ret_val = HttpResponse(content=json_string, mimetype="application/json")

    else:
        ret_val =  render_to_response("tagged_build_list.html", {'apps': apps, 'host': host}, context_instance=RequestContext(request))

    return ret_val

def toggle_tag(request, app_id, tag_name):

    try:
        tag = Tag.objects.get(name__iexact=tag_name)
    except Tag.DoesNotExist:
        tag = Tag(name=tag_name)
        tag.save()

    app = App.objects.get(id=app_id)
    app_tags = app.tags.filter(id=tag.id)

    if(app_tags.count() < 1):
        app.tags.add(tag)
    else:
        app.tags.remove(tag)

    app.save()
    return HttpResponse(content="%s version %s now has %s tags." % (app.name, app.version, app.tags.count()))

def delete_tag(request, tag_name):

    ret_val = None
    try:
        tag = Tag.objects.get(name__iexact=tag_name)
        tag.delete()
        ret_val = HttpResponse(status=200)
    except Tag.DoesNotExist:
        ret_val = HttpResponse(status=400)

    return ret_val

def app_tag(request, app_id):

    app = App.objects.get(id=app_id)
    named_tags = [tag.name for tag in app.tags.all()]
    
    json_dict = dict({
        'tags' : named_tags})

    json_string = json.dumps(json_dict)

    return HttpResponse(content=json_string, mimetype="application/json")

def all_tags(request):
    named_tags = [tag.name for tag in Tag.objects.all()]
    
    json_dict = dict({
        'tags' : named_tags})

    json_string = json.dumps(json_dict)

    return HttpResponse(content=json_string, mimetype="application/json")

def get_package(request, uuid, extension):

    handler = GetRequestHandler(request).handler()
    return handler.respond()

