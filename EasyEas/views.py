from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.template import RequestContext
from zipfile import ZipFile
import utils

from Foundation import NSDictionary


from EasyEas.models import *
from EasyEas import forms

from datetime import datetime

@csrf_exempt
def upload_build(request):

    if request.method == 'POST':
        form = forms.UploadBuildForm(request.POST, request.FILES)    
        if form.is_valid():

            filename = request.FILES['ipa_file'].name
            filename_list = filename.split('.')
            filename_list = filename_list[0:-1]
            filename = ".".join(filename_list)

            app_info = utils.save_uploaded_ipa_and_dsym(request.FILES['ipa_file'], request.FILES['dsym_file'])
            app = App(version=app_info['version'], note=form.cleaned_data['note'], name=app_info['app_name'], product=form.cleaned_data['product'], creation_date=datetime.now())
            try:
                app.save()
                return HttpResponseRedirect("/apps/list")
            except IntegrityError:
                response_string = "The app '%s' already has a version '%s' in the system. Please upload a different version." % (filename, app_info['version'])
                return HttpResponse(status="409", content=response_string)

        else:
            return HttpResponse(form.errors)
    else:
        form = forms.UploadBuildForm()
        return render_to_response("forms/upload.html",  {'form': form})

def apps(request):

    if request.user.is_authenticated():
        apps = App.objects.all().order_by('-creation_date')
        auth = "logout"
    else:
        apps = App.objects.filter(approved=True).order_by('-creation_date')
        auth = "login"

    host = request.get_host()


    return render_to_response("appstore_index.html", {'apps': apps, 'host': host, 'auth': auth}, context_instance=RequestContext(request))

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
    theZip = ZipFile(settings.STATIC_ROOT + app_name + "-" + app_version + ".ipa")
    parsed_dict = utils.plist_from_ipa(theZip)

    url = "http://%s/apps/ipa/%s/%s" % (request.get_host(), app_name, app_version) 
    bundle_id = parsed_dict['CFBundleIdentifier']
    bundle_version = parsed_dict['CFBundleVersion']
    app_title = parsed_dict['CFBundleName']

    template = "generic_enterprise_manifest.plist"
    app_dict = NSDictionary.dictionaryWithContentsOfFile_(template)

    theZip.close()
    return render_to_response(template, {"app_url": url,
                                "bundle_identifier": bundle_id,
                                   "bundle_version": bundle_version,
                                        "app_title": app_title})

def get_ipa(request, app_name, app_version):

    app = open(settings.STATIC_ROOT + app_name + "-" + app_version + ".ipa", "r")
    
    return HttpResponse(app, mimetype="application/octet-stream")

def get_dsym(request, app_name, app_version):

    app_file = open("%s%s-%s.app.dSYM.zip" % (settings.STATIC_ROOT, app_name, app_version), "r")

    return HttpResponse(app_file, mimetype="application/octet-stream")

