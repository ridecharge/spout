from django.conf import settings
from zipfile import ZipFile
import shutil
import os
from Foundation import NSDictionary, NSAutoreleasePool



def ipa_path(app_name, version):

    path = "%s%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)
    return path


def save_uploaded_file(the_file):

    
    temp_file_path = "/tmp/temp_file.ipa"
    temp_file = open(temp_file_path, "w")

    for chunk in the_file.chunks():
        temp_file.write(chunk)
    temp_file.close()

    import re
    regex = re.compile(".*\.app/$")
    ipa_contents = ZipFile(temp_file_path).filelist

    app_name = "".join([thefile.filename for thefile in ipa_contents if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])

    ipa_plist = plist_from_ipa(temp_file_path, app_name)
    version = ipa_plist['CFBundleVersion']

    new_file_location = "%s/%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)

    shutil.move(temp_file_path, new_file_location)

    return version

def plist_from_ipa(filename, app_name):

    thezip = ZipFile(filename)
    plist_dict = thezip.open("Payload/" + app_name + ".app/" + "Info.plist")

    tempfile = open("/tmp/temp_plist.plist", "w")

    for line in plist_dict:
        tempfile.write(line)

    tempfile.close()

    pool = NSAutoreleasePool.alloc().init()
    parsed_dict = NSDictionary.dictionaryWithContentsOfFile_("/tmp/temp_plist.plist")
    copied_dict = dict(parsed_dict)

    return copied_dict
 
