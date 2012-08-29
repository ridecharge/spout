from django.conf import settings


def ipa_path(app_name, version):

    path = "%s%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)
    return path


def save_uploaded_file(the_file, version):

    split_filename = the_file.name.split('.')

    split_filename.insert(-1, "-" + version)
    split_filename.insert(-1, ".")


    new_file_location = settings.STATIC_ROOT + "/" + "".join(split_filename)
    new_file = open(new_file_location, "w") 

    for c in the_file.chunks():
        new_file.write(c)
    new_file.close()
