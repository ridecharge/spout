from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from Foundation import NSDictionary
from zipfile import ZipFile
import utils


from EasyEas.models import *
from EasyEas import forms

from datetime import datetime

@csrf_exempt
def upload_build(request):

    if request.method == 'POST':
        form = forms.UploadBuildForm(request.POST, request.FILES)    
        if form.is_valid():

            filename = request.FILES['file'].name
            filename_list = filename.split('.')
            filename_list = filename_list[0:-1]
            filename = ".".join(filename_list)

            app_version = utils.save_uploaded_file(request.FILES['file'])
            app = App(version=app_version, note=form.cleaned_data['note'], name=filename, product=form.cleaned_data['product'], creation_date=datetime.now())
            try:
                app.save()
                return HttpResponseRedirect("/apps/list")
            except IntegrityError:
                response_string = "The app '%s' already has a version '%s' in the system. Please upload a different version." % (filename, app_version)
                return HttpResponse(status="409", content=response_string)

        else:
            return HttpResponse(form.errors)
    else:
        form = forms.UploadBuildForm()
        return render_to_response("forms/upload.html",  {'form': form})

def apps(request):

    apps = App.objects.all().order_by('-creation_date')

    host = request.get_host()


    return render_to_response("appstore_index.html", {'apps': apps, 'host': host})

def get_plist(request, app_name, app_version):

    parsed_dict = utils.plist_from_ipa(settings.STATIC_ROOT + app_name + "-" + app_version + ".ipa", app_name)

    url = "http://%s/apps/ipa/%s/%s" % (request.get_host(), app_name, app_version) 
    bundle_id = parsed_dict['CFBundleIdentifier']
    bundle_version = parsed_dict['CFBundleVersion']
    app_title = parsed_dict['CFBundleName']

    template = "generic_enterprise_manifest.plist"
    app_dict = NSDictionary.dictionaryWithContentsOfFile_(template)

    return render_to_response(template, {"app_url": url,
                                                "bundle_identifier": bundle_id,
                                                   "bundle_version": bundle_version,
                                                        "app_title": app_title})

def get_ipa(request, app_name, app_version):

    app = open(settings.STATIC_ROOT + app_name + "-" + app_version + ".ipa", "r")
    
    return HttpResponse(app, mimetype="application/octet-stream")

