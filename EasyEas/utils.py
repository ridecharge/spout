from django.conf import settings
from zipfile import ZipFile
import shutil
from tempfile import mkstemp, mkdtemp
import os
import re
from Foundation import NSDictionary, NSAutoreleasePool



def ipa_path(app_name, version):

    path = "%s%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)
    return path


def save_uploaded_file(the_file):

    temp_file, temp_file_path = mkstemp()
    temp_file = open(temp_file_path, 'w')

    for chunk in the_file.chunks():
        temp_file.write(chunk)
    temp_file.close()

    ipa_file = ZipFile(temp_file_path)
    ipa_contents = ipa_file.filelist

    temp_dir = mkdtemp()

    ipa_plist = plist_from_ipa(ipa_file)
    version = ipa_plist['CFBundleVersion']

    if 'CFBundleIconFiles' in ipa_plist.keys():
        icons = ipa_plist['CFBundleIconFiles']
        if len(icons) > 0:

            hires_search_pattern = re.compile(".*@2x.png")
            hires_icons = filter(hires_search_pattern.match, icons)
            if len(hires_icons) < 1:
                icon = icons[0]
            else:
                icon = hires_icons[0]
            icon_search_pattern = re.compile(".*%s" % icon)
            icon_path = [f.filename for f in ipa_file.filelist if icon_search_pattern.match(f.filename)][0] 
            extracted_icon_path = ipa_file.extract(icon_path, path=temp_dir)
            app_name = app_name_from_filelist(ipa_file.filelist)
            print extracted_icon_path
            shutil.move(extracted_icon_path, "%s/%s-%s.png" % (settings.STATIC_ROOT, app_name, version))
           
    new_file_location = "%s/%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)

    shutil.move(temp_file_path, new_file_location)

    ipa_file.close()
    return version


def plist_from_ipa(ipa_file_or_path):

    needs_closed = False
    if type(ipa_file_or_path) == str: 
        ipa_file = Zipfile(ipa_file_or_path)
        needs_closed = True
    else: 
        ipa_file = ipa_file_or_path


    ipa_contents = ipa_file.filelist
    app_name = app_name_from_filelist(ipa_contents)
    temp_dir = mkdtemp()
    plist_dict_path = ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=temp_dir)

    pool = NSAutoreleasePool.alloc().init()
    parsed_dict = NSDictionary.dictionaryWithContentsOfFile_(plist_dict_path)
    copied_dict = dict(parsed_dict)

    if needs_closed == True:
        ipa_file.close()

    return copied_dict

def app_name_from_filelist(filelist): 

    regex = re.compile(".*\.app/$")
    app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])
    return app_name

