import biplist
import os
import re
import shutil
from datetime import datetime
from zipfile import ZipFile
from tempfile import mkdtemp, mkstemp
from androguard.core import androconf
from androguard.core.bytecodes import apk
from elementtree.ElementTree import Element, parse
from xml.dom import minidom
from md5 import md5

from django.core.files import File

from AppDistribution.models import *
from AppDistribution import settings

package_key = "app_package"
version_key = "version"
product_key = "product"
package_type_key = "file_type"


dsym_key = "dsym_file"
from PackageHandlers import *


def save_uploaded_file_to_temp(file_from_form):

    temp_file, temp_file_path = mkstemp()
    temp_file = open(temp_file_path, 'w')

    for chunk in file_from_form.chunks():
        temp_file.write(chunk)
    temp_file.close()

    return temp_file_path

class UploadRequestHandler:

    def __init__(self, request):

        self.package_type = request.POST[package_type_key]
        self.request = request

    def validate(self, post_form):

        form = post_form(self.post_data, self.uploaded_files)
        return form.is_valid()
    
    def process_upload(self):

        handler = upload_package_handlers[self.package_type]
        handler = handler(self.request)

        handler.handle_package()


class BaseUploadHandler(object):
    
    def __init__(self, request):
        self.request = request
        self.temp_dir = mkdtemp()
        self.product = Product.objects.get(name__iexact=request.POST['product'])

    def add_tag(self, app):
 
        tag = None
        if "tag" in self.request.POST.keys():
            tag_name = self.request.POST['tag']

            try:
                tag = Tag.objects.get(name__iexact=tag_name)
            except Tag.DoesNotExist:
                tag = Tag(name=tag_name, description="Branch %s" % tag_name)
                tag.save()

        if tag: 
            app.tags.add(tag)
      


class AndroidPackageUploadHandler(BaseUploadHandler):

    def __init__(self, request):
        super(AndroidPackageUploadHandler, self).__init__(request)

        self.temp_apk_path = save_uploaded_file_to_temp(request.FILES[package_key])
        self.note = request.POST['note']


    def handle_package(self):

        device_type = self.request.POST[package_type_key].upper()

        app = App(note=self.note, product=self.product, device_type=device_type)
        app.package = File(open(self.temp_apk_path))
        app.save()
        self.add_tag(app)
        app.save()

class iOSPackageUploadHandler(BaseUploadHandler):


    def __init__(self, request):

        super(iOSPackageUploadHandler, self).__init__(request)

        self.temp_ipa_path = save_uploaded_file_to_temp(request.FILES[package_key])

        if dsym_key in request.FILES:
            self.dsym = request.FILES[dsym_key]


    def respond(self):

        self.handle_package()
        ret_val = HttpResponseRedirect("/apps/list")

        return ret_val

    def handle_package(self):

        app = App()

        app.package = File(open(self.temp_ipa_path))
        if 'note' in self.request.POST.keys(): 
            app.note = self.request.POST['note'] 

        app.product = Product.objects.get(name__iexact=self.request.POST['product']) # fetch product by name, case insensitive
        app.save()

        dsym_asset = AppAsset(app=app, asset_file=dsym)
        dsym_asset.save()
        app.assets = dsym_asset

        self.add_tag(app)
        app.save()

upload_package_handlers = dict({ 'IOS' : iOSPackageUploadHandler, 'ANDROID' : AndroidPackageUploadHandler })
