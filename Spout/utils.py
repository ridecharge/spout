from django.conf import settings
from zipfile import ZipFile
import shutil
from tempfile import mkstemp, mkdtemp
import os
import re
import biplist


def ipa_path(app_name, version):

    path = "%s/%s-%s.ipa" % (settings.MEDIA_ROOT, app_name, version)
    return path

def save_uploaded_file_to_temp(file_from_form):

    temp_file, temp_file_path = mkstemp()
    temp_file = open(temp_file_path, 'w')

    for chunk in file_from_form.chunks():
        temp_file.write(chunk)
    temp_file.close()

    return temp_file_path


def save_uploaded_ipa_and_dsym(the_ipa, the_dsym):

    temp_ipa_path = save_uploaded_file_to_temp(the_ipa)
    temp_dsym_path = save_uploaded_file_to_temp(the_dsym)
    
    ipa_file = ZipFile(temp_ipa_path)
    ipa_contents = ipa_file.filelist

    temp_dir = mkdtemp()

    ipa_plist = plist_from_ipa(ipa_file)
    version = ipa_plist['CFBundleVersion']
    app_name = ipa_plist['CFBundleDisplayName']
    app_name = app_name_from_filelist(ipa_file.filelist)

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
            print extracted_icon_path
            shutil.move(extracted_icon_path, "%s/%s-%s.png" % (settings.MEDIA_ROOT, app_name, version))

    app_binary_location = ipa_file.extract("Payload/%s.app/%s", (ipa_plist['CFBundleName'], ipa_plist['CFBundleExecutable']), path=temp_dir)

    dump_handle = os.popen("dwarfdump --uuid %s", app_binary_location)
    uuid = dump_handle.read().split(' ')[1]
    dump_handle.close()
           
    new_ipa_location = "%s/%s-%s.ipa" % (settings.MEDIA_ROOT, app_name, version)
    new_dsym_location = "%s/%s-%s.app.dSYM.zip" % (settings.MEDIA_ROOT, app_name, version)

    shutil.move(temp_ipa_path, new_ipa_location)
    shutil.move(temp_dsym_path, new_dsym_location)

    ipa_file.close()

    app_info = dict({'version': version, 'app_name': app_name, 'uuid': uuid })
    return app_info


def plist_from_ipa(ipa_file):

    ipa_contents = ipa_file.filelist
    app_name = app_name_from_filelist(ipa_contents)
    temp_dir = mkdtemp()
    plist_dict_path = ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=temp_dir)

    parsed_dict = biplist.readPlist(plist_dict_path)
    copied_dict = dict(parsed_dict)

    return copied_dict

def app_name_from_filelist(filelist): 

    regex = re.compile(".*\.app/$")
    app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])
    return app_name

def decode_crash_report(raw_crash_report):

    if os.path.isfile("%s/plcrashutil" % settings.UTILITIES_ROOT) == False:
        raise IOError("Could not file plcrashutil in your UTILITIES_ROOT defined in settings.py")
    if os.path.isfile(raw_crash_report) == False:
        raise IOError("Could not find crash report '%s'." % raw_crash_report)

    converted_crash = os.popen("%s/plcrashutil convert --format=ios %s" % (settings.UTILITIES_ROOT, raw_crash_report))

    temp_crash_loc = mkstemp()[1]
    temp_crash_rep = open(temp_crash_loc, "w")

    shutil.copyfileobj(converted_crash, temp_crash_rep)

    converted_crash.close()
    temp_crash_rep.close()
    temp_crash_rep = open(temp_crash_loc, "r")

    return temp_crash_rep

def symbolicate_crash(crash_report, dsym_location):

    temp_symd = mkstemp()[1]

    export_cmd = "export DEVELOPER_DIR=`xcode-select --print-path`;"
    sym_cmd =  "%s/symbolicatecrash -o %s %s %s" % (settings.UTILITIES_ROOT, temp_symd, crash_report, dsym_location)
    print sym_cmd
    os.system(export_cmd + sym_cmd)

    symd_crash = open(temp_symd, "r")

    return symd_crash
