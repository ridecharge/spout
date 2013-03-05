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

from Spout.models import *
from Spout import settings

package_key = "app_package"
version_key = "version"
product_key = "product"
package_type_key = "file_type"


dsym_key = "dsym_file"
#from PackageHandlers import *


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

        handler = package_handlers[self.package_type]
        handler = handler(self.request)

        handler.handle_package()


class BaseHandler(object):
    
    def __init__(self, request):
        self.request = request
        self.temp_dir = mkdtemp()
        self.product = Product.objects.get(name__iexact=request.POST['product'])

class AndroidPackageHandler(BaseHandler):

    def __init__(self, request):
        super(AndroidPackageHandler, self).__init__(request)


        self.temp_apk_path = save_uploaded_file_to_temp(request.FILES[package_key])

        a = apk.APK(self.temp_apk_path)
        md5_raw = x = md5(a.get_dex()).hexdigest().upper()
        self.uuid = "%s-%s-%s-%s-%s" % (x[0:8], x[8:12], x[12:16], x[16:20], x[20:32]) 
        self.name = a.package
        self.version = a.get_androidversion_name()

        self.note = request.POST['note']


    def handle_package(self):

        #self.save_icon_files()
        self.save_apk()

        creation_date = datetime.now()
        device_type = self.request.POST[package_type_key].upper()

        app = App(version=self.version, note=self.note, name=self.name, product=self.product, creation_date=creation_date, uuid=self.uuid, device_type=device_type)

        app.save()

    def save_icon_files(self):

        temp_decoded = "%s/app" % self.temp_dir

        os.system("%s/apktool d %s %s" % (settings.UTILITIES_ROOT, self.temp_apk_path, temp_decoded))

        xml = minidom.parse("%s/AndroidManifest.xml" % temp_decoded)
        application_node = xml.getElementsByTagName("application")[0]

        icon_from_xml = application_node.attributes['android:icon'].value
        icon_from_xml = icon_from_xml.replace("@", "")

        resource_dir = "%s/res" % temp_decoded
        matching_dirs = ["%s/%s" % (resource_dir, x) for x in os.listdir(resource_dir) if re.match(icon_from_xml.split("/")[0], x)]

        for d in matching_dirs:

            matching_files = ["%s/%s" % (d, x) for x in os.listdir(d) if re.match("%s.png" % icon_from_xml.split("/")[-1], x)]

            if len(matching_files) > 0:
                
                print "".join(matching_files) + "XXXXX"
                [shutil.move(the_file, "%s/%s.png" % (settings.MEDIA_ROOT, self.uuid)) for the_file in matching_files]

    def save_apk(self):

        shutil.move(self.temp_apk_path, "%s/%s.apk" % (settings.MEDIA_ROOT, self.uuid))


class iOSPackageHandler(BaseHandler):


    def __init__(self, request):

        super(iOSPackageHandler, self).__init__(request)

        temp_ipa_path = save_uploaded_file_to_temp(request.FILES[package_key])
        
        self.ipa_file = ZipFile(temp_ipa_path)
        if dsym_key in request.FILES:
            self.dsym = request.FILES[dsym_key]
        self.ipa_plist = self.plist_from_ipa()
        self.uuid = self.extract_uuid()


    def respond(self):

        self.handle_package()
        ret_val = HttpResponseRedirect("/apps/list")

        return ret_val

    def handle_package(self):

        self.save_ipa()
        self.save_icon_files()
        self.save_uploaded_dsym()

        version = self.ipa_plist['CFBundleVersion']
        note = self.request.POST['note'] 
        name = self.ipa_plist['CFBundleName']
        device_type = self.request.POST[package_type_key]

        creation_date = datetime.now()

        tag = None

        app = App(version=version, note=note, name=name, product=self.product, creation_date=creation_date, uuid=self.uuid, device_type=device_type)

        if "tag" in self.request.POST.keys():
            tag_name = self.request.POST['tag']

            try:
                tag = Tag.objects.get(name__iexact=tag_name)
            except Tag.DoesNotExist:
                tag = Tag(name=tag_name, description="Branch %s" % tag_name)
                tag.save()

        app.save()
        if tag: 
            app.tags.add(tag)
            app.save()

    def ipa_path(self):

        path = "%s/%s.ipa" % (settings.MEDIA_ROOT, self.uuid)
        return path

    def save_uploaded_dsym(self):

        temp_dsym_path = save_uploaded_file_to_temp(self.dsym)
        new_dsym_location = dsym_path(self.uuid)
        shutil.move(temp_dsym_path, new_dsym_location)
        shutil.move(temp_dsym_path, "%s/%s.dSYM.zip" % (settings.MEDIA_ROOT, self.uuid))


    def extract_app_name(self): 

        filelist = self.ipa_file.filelist
        regex = re.compile(".*\.app/$")
        app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])

        return app_name

    def extract_uuid(self):

        app_name = self.extract_app_name()
        app_binary_location = self.ipa_file.extract("Payload/%s.app/%s" % (app_name, self.ipa_plist['CFBundleExecutable']), path=self.temp_dir)
        dump_handle = os.popen("dwarfdump --uuid %s" % app_binary_location)
        uuid = dump_handle.read().split(' ')[1]
        dump_handle.close()

        return uuid

    def save_icon_files(self):

        if 'CFBundleIconFiles' in self.ipa_plist.keys():
            icons = self.ipa_plist['CFBundleIconFiles']
            if len(icons) > 0:

                hires_search_pattern = re.compile(".*@2x.png")
                hires_icons = filter(hires_search_pattern.match, icons)
                if len(hires_icons) < 1:
                    icon = icons[0]
                else:
                    icon = hires_icons[0]
                icon_search_pattern = re.compile(".*%s" % icon)
                icon_path = [f.filename for f in self.ipa_file.filelist if icon_search_pattern.match(f.filename)][0] 
                extracted_icon_path = self.ipa_file.extract(icon_path, path=self.temp_dir)
                print extracted_icon_path
                shutil.move(extracted_icon_path, "%s/%s.png" % (settings.MEDIA_ROOT, self.uuid))

    def save_ipa(self):

        new_ipa_location = self.ipa_path()
        temp_ipa_path = save_uploaded_file_to_temp(self.request.FILES[package_key])
        shutil.move(temp_ipa_path, new_ipa_location)

    def plist_from_ipa(self):

        app_name = self.extract_app_name()
        plist_dict_path = self.ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=self.temp_dir)

        parsed_dict = biplist.readPlist(plist_dict_path)
        copied_dict = dict(parsed_dict)

        return copied_dict

    def decode_crash_report(raw_crash_report):

        if os.path.isfile("%s/plcrashutil" % settings.UTILITIES_ROOT) == False:
            raise IOError("Could not file plcrashutil in your UTILITIES_ROOT defined in settings.py")
        if os.path.isfile(raw_crash_report) == False:
            raise IOError("Could not find crash report '%s'." % raw_crash_report)

        
        temp_crash_loc = mkstemp()[1]

        os.system("%s/plcrashutil convert --format=ios %s > %s 2> /dev/null" % (settings.UTILITIES_ROOT, raw_crash_report, temp_crash_loc))

        temp_crash_rep = open(temp_crash_loc, "r")

        return (temp_crash_rep, temp_crash_loc)

    def symbolicate_crash(crash_json, dsym_zip_location, ipa_location):


        the_zip = ZipFile(dsym_zip_location)
        the_ipa = ZipFile(ipa_location)

        temp_location = mkdtemp()

        the_zip.extractall(path=temp_location)
        the_ipa.extractall(path=temp_location)

        rx = re.compile("^(.*DWARF/$)")
        dsym_dir = [x.filename for x in the_zip.filelist if rx.match(x.filename)][0]

        rx = re.compile("Payload/(.*).app/")
        binary_dir = [x.filename for x in the_ipa.filelist if rx.match(x.filename)][0]

        temp_dsym_path = temp_location + "/" + dsym_dir
        temp_ipa_path = temp_location + "/" + binary_dir

        temp_symd = mkstemp()[1]

        export_cmd = "export DEVELOPER_DIR=`xcode-select --print-path`;"
        sym_cmd =  "%s/symbolicatecrash -v -o %s %s %s %s" % (settings.UTILITIES_ROOT, temp_symd, crash_report, temp_dsym_path, temp_ipa_path)
        print sym_cmd
        os.system(export_cmd + sym_cmd)

        symd_crash = open(temp_symd, "r")

        return (symd_crash, temp_symd)

package_handlers = dict({ 'IOS' : iOSPackageHandler, 'ANDROID' : AndroidPackageHandler })
