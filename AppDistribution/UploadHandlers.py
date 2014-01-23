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

    temp_file_dir = mkdtemp()
    temp_file_path = "%s/%s" % (temp_file_dir, file_from_form.name)
    temp_file = open(temp_file_path, 'w')

    for chunk in file_from_form.chunks():
        temp_file.write(chunk)
    temp_file.close()

    return temp_file_path

class UploadRequestHandler:

    def __init__(self, request):

        self.request = request

    def validate(self, post_form):

        form = post_form(self.post_data, self.uploaded_files)
        return form.is_valid()
    
    def process_upload(self):

        handler = UploadHandler(self.request)

        handler.handle_upload()


class UploadHandler(object):
    
    def __init__(self, request):
        self.request = request
        self.temp_dir = mkdtemp()
        self.product = Product.objects.get(name__iexact=request.POST['product'])
        self.note = request.POST['note']
        self.device_type = self.request.POST[package_type_key].upper()

    def add_tag(self, app):
 
        tag = None
        if "tag" in self.request.POST.keys():
            tag_name = self.request.POST['tag']

            if len(tag_name) > 0:

                try:
                    tag = Tag.objects.get(name__iexact=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag(name=tag_name)
                    tag.save()

        if tag: 
            app.tags.add(tag)
      
    def handle_upload(self):

        app = App(note=self.note, product=self.product, device_type=self.device_type)
        app.save()
        self.add_tag(app)

        for file_key in self.request.FILES:
            temp_file = save_uploaded_file_to_temp(self.request.FILES[file_key])
            open_temp = File(open(temp_file))
            asset = AppAsset(app=app, asset_file=open_temp)
            if file_key == "app_package":
              asset.primary = True

            asset.save()


