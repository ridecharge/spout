from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.template import RequestContext, Context, Template
from django.db.models import Q

from django.core.files import File

from datetime import datetime
from django.utils import timezone
from zipfile import ZipFile
import tempfile
import shutil
import json
import time
import re

from UploadHandlers import UploadRequestHandler
from GetRequestHandlers import GetRequestHandler
from ResponseFactory import PackageHttpResponseFactory
from AppDistribution.models import *
from AppDistribution import settings
from AppDistribution import forms

@csrf_exempt
def create_app(request):

    if request.method == "POST":
        form = forms.UploadAppForm(request.POST)
        if form.is_valid():
            try:
                product_string = form.cleaned_data['product']
                product = Product.objects.get(name__iexact=product_string)
            except Product.DoesNotExist:
                pass

            new_app = App(product=product, note=form.cleaned_data['note'])
            try:
                tag_list = form.cleaned_data['tags']
                query_list = map(lambda x: Q(name__iexact=x), tag_list)
                query_list = reduce(lambda a, b: a | b, query_list)
                tags = Tag.objects.filter(query_list)
            except:
                pass

            new_app.save()

            json_dict = {'new_app_id' : new_app.id}
            return HttpResponse(content=json.dumps(json_dict), mimetype="application/json")
        else:
            return HttpResponse(content=json.dumps(form.errors), mimetype="application/json")
    else:
        form = forms.UploadAppForm()
        return render_to_response("forms/upload.html", {'form' : form})


@csrf_exempt
def add_asset_to_app(request, app_id):

    if request.method == "POST":
        form = forms.UploadAppAssetForm(request.POST, request.FILES)
        if form.is_valid():
            app = App.objects.get(id=app_id)
            asset = form.save(commit=False)
            asset.app = app
            asset.save()
            response_dict = {'app' : app.id, 'added_asset' : {'id' : asset.id, 'primary' : asset.primary}}
            return HttpResponse(content=json.dumps(response_dict), mimetype="application/json")
        else:
            return HttpResponse(content=json.dumps(form.errors), mimetype="application/json")


@csrf_exempt
def upload_build(request):

    ret_val = None

    if request.method == 'POST':
        form = forms.UploadBuildForm(request.POST, request.FILES)    
        if form.is_valid():
            product_string = form.cleaned_data['product']
            product = Product.objects.get(name__iexact=product_string)
 
            new_app = App(product=product, note=form.cleaned_data['note'], device_type=form.cleaned_data['file_type'])
            new_app.save()
        
            try:
                tag = Tag.get_or_create(request.POST['tag'])
                new_app.tags.add(tag)
            except KeyError:
                pass
           

            from UploadHandlers import save_uploaded_file_to_temp;

            temp_package = save_uploaded_file_to_temp(request.FILES['app_package'])


            app_asset = AppAsset(asset_file=File(open(temp_package)), primary=True)
            app_asset.app = new_app
            app_asset.save()

            ret_val = HttpResponseRedirect("/")
        else:
            ret_val = HttpResponse(form.errors)
    else:
        form = forms.UploadBuildForm()
        ret_val = render_to_response("forms/upload.html",  {'form': form})
    return ret_val

@csrf_exempt
def post_crash(request):

    
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
            row_dict = {}
            if row.app:

                app = row.app

                row_dict['id'] = app.uuid
                row_dict['product'] = row.product.name
                if app.icon_url:
                    row_dict['icon'] = app.icon_url
                else:
                    row_dict['icon'] = ""
                row_dict['version'] = app.version

                page_rows.append(row_dict)
            


        page_dict = {'title' : page.title,
                'allowed_pages' : allowed_pages,
                'heading' :  page.heading,
                'rows' : page_rows }
        content = json.dumps(page_dict)
        return HttpResponse(content=content, mimetype="application/json")

    else:

        if page.expiration_date != None and timezone.now() > page.expiration_date: 
            return HttpResponse(content="This page has expired.  Please contact your admin for access.")
        if request.user.id != None and request.user.expiration_date != None and timezone.now() > request.user.expiration_date:
            return HttpResponse(content="Your user account has expired.  Please contact your admin for access.")

        if page.requires_auth == False:
                allowed_pages = Page.objects.filter(requires_auth=False)
                return render_to_response("page.html", {'page': page, 'allowed_pages' : allowed_pages}, context_instance=RequestContext(request))
        elif (page.requires_auth and request.user.is_authenticated()):

            allowed_pages = request.user.allowed_pages.all()
            print allowed_pages
            if page in allowed_pages:
                return render_to_response("page.html", {'page': page, 'allowed_pages': allowed_pages}, context_instance=RequestContext(request))
            else:
                return HttpResponse(content="You are not authorized to view this page.")
            
        elif request.user.is_authenticated() == False: 
            return HttpResponseRedirect("/accounts/login/?next=%s" % request.path)

def asset_redirect(request, uuid):

    app = App.objects.filter(uuid=uuid)[0]
    response = PackageHttpResponseFactory(request).response(app)
    return response
   
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

def get_app_asset(request, app_id, asset_id, extension):

    app = App.objects.get(id=app_id)

    if extension is not None and extension in GetRequestHandler.handled_extensions:
        response = GetRequestHandler(request, app, extension).handler().respond()
    else:
        asset = app.assets.get(id=asset_id)
        response = HttpResponse(content=asset.asset_file, content_type="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename=%s' % app.primary_asset.filename

    return response

def get_app_package_redirect(request, app_id):

    app = App.objects.get(id=app_id)
    app.download_count += 1
    app.save()
    
    response = PackageHttpResponseFactory(request).response(app)
    return response

