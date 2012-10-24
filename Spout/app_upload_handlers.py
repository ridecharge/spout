import biplist
import os
import shutil
from datetime import datetime
from zipfile import ZipFile
from tempfile import mkdtemp, mkstemp
from Spout.models import *
from Spout import settings

package_key = "app_package"
version_key = "version"
product_key = "product"
package_type_key = "file_type"

#from PackageHandlers import *

package_handlers = dict({ 'IOS' : iOSHandler, 'ANDROID' : AndroidHandler })

def save_uploaded_file_to_temp(file_from_form):

    temp_file, temp_file_path = mkstemp()
    temp_file = open(temp_file_path, 'w')

    for chunk in file_from_form.chunks():
        temp_file.write(chunk)
    temp_file.close()

    return temp_file_path



class BuildUploadRequestHandler:

    def __init__(self, request):

        self.app_package = request.FILES[package_key]

        self.version = request.POST[version_key]
        self.product_id = request.POST[product_key]
        self.package_type = request.POST[package_type_key]

        self.uploaded_files = request.FILES
        self.post_data = request.POST

    def validate(self, post_form):

        form = post_form(self.post_data, self.uploaded_files)
        return form.is_valid()
    
    def process_upload(self):

        handler = package_handlers[self.package_type].__init__()
        handler.handle_package()


class iOSHandler:

    dsym_key = "dsym_file"

    def __init__(self, request):

        self.request = request
        if request.method == 'POST':

            temp_ipa_path = save_uploaded_file_to_temp(request.FILES[package_key])
            
            self.ipa_file = ZipFile(temp_ipa_path)
            self.dsym = request.FILES[dsym_key]
            self.ipa_plist = self.plist_from_ipa()
            self.temp_dir = mkdtemp()

    def handle_package(self):

        self.save_ipa()
        self.save_icon_files()

        version = self.ipa_plist['CFBundleVersion']
        note = self.request.POST['note'] 
        name = self.ipa_plist['CFBundleName']
        product = self.POST['product']
        creation_date = datetime.now()
        uuid = self.extract_uuid()

        tag = None

            if "tag" in self.request.POST.keys():
                tag_name = request.POST['tag']

                try:
                    tag = Tag.objects.get(name__iexact=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag(name=tag_name, description="Branch %s" % tag_name)
                    tag.save()

            app.save()
            if tag: 
                app.tags.add(tag)
                app.save()

        app = App(version=version, note=note, name=name, product=product, creation_date=creation_date, uuid=uuid)

        app.save()

        
    def ipa_path(uuid):

        path = "%s/%s.ipa" % (settings.MEDIA_ROOT, uuid)
        return path

    def save_uploaded_dsym(the_dsym, uuid):

        temp_dsym_path = save_uploaded_file_to_temp(the_dsym)
        new_dsym_location = dsym_path(uuid)
        shutil.move(temp_dsym_path, new_dsym_location)

    def extract_app_name(self): 

        filelist = self.ipa_file.filelist
        regex = re.compile(".*\.app/$")
        app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])

        return app_name

    def extract_uuid(self):

        app_name = self.extract_app_name()
        app_binary_location = self.ipa_file.extract("Payload/%s.app/%s" % (app_name, ipa_plist['CFBundleExecutable']), path=temp_dir)
        dump_handle = os.popen("dwarfdump --uuid %s" % app_binary_location)
        uuid = dump_handle.read().split(' ')[1]
        dump_handle.close()

        return uuid

    def save_icon_files(self):

        if 'CFBundleIconFiles' in self.ipa_plist.keys():
            icons = ipa_plist['CFBundleIconFiles']
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
                shutil.move(extracted_icon_path, "%s/%s.png" % (settings.MEDIA_ROOT, uuid))

    def save_ipa(self):

        new_ipa_location = self.ipa_path(self.uuid)
        shutil.move(temp_ipa_path, new_ipa_location)

    def plist_from_ipa(self):

        ipa_contents = self.ipa_file.filelist
        app_name = app_name_from_filelist(ipa_contents)
        temp_dir = mkdtemp()
        plist_dict_path = self.ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=temp_dir)

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
