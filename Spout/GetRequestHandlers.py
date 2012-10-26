from Spout import settings
import re
from zipfile import ZipFile
import biplist
from tempfile import mkdtemp
from django.http import HttpResponseRedirect, HttpResponse

from django.template import RequestContext, Context, Template
from django.shortcuts import get_object_or_404, render_to_response, render


class GetRequestHandler(object):

    def __init__(self, request):

        request_re = r'.*(?P<uuid>([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})).(?P<extension>\w+)'
        match_dict = re.match(request_re, request.META['PATH_INFO']).groupdict()
        self.extension = match_dict['extension']
        self.request = request

    def handler(self):

        if self.extension in AndroidGetRequestHandler.handles:
            return AndroidGetRequestHandler(self.request)
        elif self.extension in iOSGetRequestHandler.handles:
            return iOSGetRequestHandler(self.request)

class BaseGetRequestHandler(object):

    def __init__(self, request):

        request_re = r'.*(?P<uuid>([A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})).(?P<extension>\w+)'
        match_dict = re.match(request_re, request.META['PATH_INFO']).groupdict()
        self.uuid = match_dict['uuid']
        self.extension = match_dict['extension']
        self.request = request

class AndroidGetRequestHandler(BaseGetRequestHandler):

    handles = ['apk']

    def respond(self):

        if self.extension == "apk":
            return self.apk_response()

    def apk_response(self):

        apk = open("%s/%s.apk" % (settings.MEDIA_ROOT, self.uuid), "r")
        return HttpResponse(content=apk, mimetype="application/octet-stream")


class iOSGetRequestHandler(BaseGetRequestHandler):

    handles = ['ipa', 'plist', 'dsym']

    def respond(self):

        responders = dict({ 'ipa' : self.__ipa_response,
                            'plist' : self.__plist_response,
                            'dsym' : self.__dsym_response })

        responder = responders[self.extension]

        return responder()

    def __plist_response(self):
        theZip = ZipFile(self.__ipa_path())
        parsed_dict = self.__plist_from_ipa(theZip)

        url = "http://%s/app/%s.ipa" % (self.request.get_host(), self.uuid) 
        bundle_id = parsed_dict['CFBundleIdentifier']
        bundle_version = parsed_dict['CFBundleVersion']
        app_title = parsed_dict['CFBundleName']

        template = "generic_enterprise_manifest.plist"
        theZip.close()
        return render_to_response(template, {"app_url": url,
                                    "bundle_identifier": bundle_id,
                                       "bundle_version": bundle_version,
                                            "app_title": app_title})

    def __ipa_response(self):

        app = open(self.__ipa_path(), "r")
        
        return HttpResponse(app, mimetype="application/octet-stream")

    def __dsym_response(self):

        app_file = open(self.__dsym_path(), "r")

        return HttpResponse(app_file, mimetype="application/octet-stream")

    def __dsym_path(self):
        return "%s/%s.dSYM.zip" % (settings.MEDIA_ROOT, self.uuid)

    def __ipa_path(self):
        return "%s/%s.ipa" % (settings.MEDIA_ROOT, self.uuid)

    def __plist_from_ipa(self, ipa_file):

        ipa_contents = ipa_file.filelist
        app_name = self.__app_name_from_filelist(ipa_contents)
        temp_dir = mkdtemp()
        plist_dict_path = ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=temp_dir)

        parsed_dict = biplist.readPlist(plist_dict_path)
        copied_dict = dict(parsed_dict)

        return copied_dict

    def __app_name_from_filelist(self, filelist): 

        regex = re.compile(".*\.app/$")
        app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])
        return app_name

