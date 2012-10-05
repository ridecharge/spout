from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.template import RequestContext
from datetime import datetime
from zipfile import ZipFile
import tempfile
import shutil
import json
import time
import re

import utils
from Spout.models import *
from Spout import forms


@csrf_exempt
def upload_build(request):

    ret_val = None

    if request.method == 'POST':
        form = forms.UploadBuildForm(request.POST, request.FILES)    
        if form.is_valid():


            filename = request.FILES['ipa_file'].name
            filename_list = filename.split('.')
            filename_list = filename_list[0:-1]
            filename = ".".join(filename_list)

            app_info = utils.save_uploaded_ipa_and_dsym(request.FILES['ipa_file'], request.FILES['dsym_file'])
            print app_info
            app = App(version=app_info['version'], note=form.cleaned_data['note'], name=app_info['app_name'], product=form.cleaned_data['product'], creation_date=datetime.now(), uuid=app_info['uuid'])



            if "tag" in request.POST.keys():
                tag_name = request.POST['tag']

                try:
                    tag = Tag.objects.get(name__iexact=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag(name=tag_name, description="Branch %s" % tag_name)
                    tag.save()



            try:
                app.save()
                if tag: 
                    app.tags.add(tag)
                    app.save()

                ret_val = HttpResponseRedirect("/apps/list")
            except IntegrityError:
                response_string = "The app '%s' already has a version '%s' in the system. Please upload a different version." % (filename, app_info['version'])
                ret_val = HttpResponse(status="409", content=response_string)
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
        ipa_path = utils.ipa_path(app.name, app.version)
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


    if request.user.is_authenticated():
        apps = App.objects.all().order_by('-creation_date')
        auth = "logout"
    else:
        apps = App.objects.filter(approved=True).order_by('-creation_date')
        auth = "login"


    products = Product.objects.all()
    apps = []

    for p in products:
        app = App.objects.filter(product=p).latest('creation_date')
        apps.append(app)

    host = request.get_host()

    return render_to_response("homepage.html", {'apps': apps, 
                                                    'host': host, 
                                                    'auth': auth},
                                                    context_instance=RequestContext(request))

def apps(request):

    if request.user.is_authenticated():
        apps = App.objects.all().order_by('-creation_date')
        auth = "logout"
    else:
        apps = App.objects.filter(approved=True).order_by('-creation_date')
        auth = "login"

    host = request.get_host()
    tags = Tag.objects.all()


    return render_to_response("appstore_index.html", {'apps': apps,
        'host': host,
        'auth': auth,
        'tags': tags},
        context_instance=RequestContext(request))

def approve_app(request, app_id):

    if request.user.is_authenticated():

        app = App.objects.get(id=app_id)
        app.approved = True
        app.save()

    return HttpResponseRedirect("/apps/list")

def unapprove_app(request, app_id):

    if request.user.is_authenticated():
        app = App.objects.get(id=app_id)
        app.approved = False
        app.save()

    return HttpResponseRedirect("/apps/list")

def get_plist(request, app_name, app_version):
    theZip = ZipFile("%s/%s-%s.ipa" % (settings.MEDIA_ROOT, app_name, app_version))
    parsed_dict = utils.plist_from_ipa(theZip)

    url = "http://%s/apps/ipa/%s/%s" % (request.get_host(), app_name, app_version) 
    bundle_id = parsed_dict['CFBundleIdentifier']
    bundle_version = parsed_dict['CFBundleVersion']
    app_title = parsed_dict['CFBundleName']

    template = "generic_enterprise_manifest.plist"
    theZip.close()
    return render_to_response(template, {"app_url": url,
                                "bundle_identifier": bundle_id,
                                   "bundle_version": bundle_version,
                                        "app_title": app_title})

def tagged_apps(request, tag_name):

    apps = App.objects.filter(tags__name=tag_name).order_by('-creation_date')

    host = request.get_host()

    return render_to_response("tagged_build_list.html", {'apps': apps, 'host': host}, context_instance=RequestContext(request))


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

def get_ipa(request, app_name, app_version):

    app = open("%s/%s-%s.ipa" % (settings.MEDIA_ROOT, app_name, app_version), "r")
    
    return HttpResponse(app, mimetype="application/octet-stream")

def get_dsym(request, app_name, app_version):

    app_file = open("%s/%s-%s.app.dSYM.zip" % (settings.MEDIA_ROOT, app_name, app_version), "r")

    return HttpResponse(app_file, mimetype="application/octet-stream")

