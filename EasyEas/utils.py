from django.conf import settings


def ipa_path(app_name, version):

    path = "%s%s-%s.ipa" % (settings.STATIC_ROOT, app_name, version)
    return path
