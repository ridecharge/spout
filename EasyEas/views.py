from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt

from Foundation import NSDictionary
from zipfile import ZipFile
import utils
import os


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
            app = App(version=form.cleaned_data['version'], note=form.cleaned_data['note'], name=filename, product=form.cleaned_data['product'], creation_date=datetime.now())
            app.save()
            utils.save_uploaded_file(request.FILES['file'], app.version)
            return HttpResponse("Success.")
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

    thezip = ZipFile(settings.STATIC_ROOT + app_name + "-" + app_version + ".ipa")
    plist_dict = thezip.open("Payload/" + app_name + ".app/" + "Info.plist")

    tempfile = open("/tmp/temp_plist.plist", "w")

    for line in plist_dict:
        tempfile.write(line)

    tempfile.close()

    parsed_dict = NSDictionary.dictionaryWithContentsOfFile_("/tmp/temp_plist.plist")
    os.remove("/tmp/temp_plist.plist")

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

