from AppDistribution import settings
from AppDistribution.models import App
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
        self.app = App.objects.filter(uuid=match_dict['uuid'])[0]
        self.extension = match_dict['extension']
        self.request = request

class AndroidGetRequestHandler(BaseGetRequestHandler):

    handles = ['apk']

    def respond(self):

        if self.extension == "apk":
            return self.apk_response()

    def apk_response(self):

        self.app.package.open() 
        return HttpResponse(content=self.app.package, mimetype="application/octet-stream")


class iOSGetRequestHandler(BaseGetRequestHandler):

    handles = ['ipa', 'plist']

    def respond(self):

        responders = dict({ 'ipa' : self.__ipa_response,
                            'plist' : self.__plist_response})

        responder = responders[self.extension]

        return responder()

    def __plist_response(self):
        """ Returns the formatted plist needed by iOS to download the ipa file."""
        theZip = ZipFile(self.app.package.path)
        parsed_dict = self.__plist_from_ipa(theZip)

        url = "http://%s/app/%s.ipa" % (self.request.get_host(), self.app.uuid) 
        bundle_id = parsed_dict['CFBundleIdentifier']
        bundle_version = parsed_dict['CFBundleVersion']
        app_title = parsed_dict['CFBundleName']

        self.app.download_count += 1
        self.app.save()

        template = "generic_enterprise_manifest.plist"
        theZip.close()
        return render_to_response(template, {"app_url": url,
                                    "bundle_identifier": bundle_id,
                                       "bundle_version": bundle_version,
                                            "app_title": app_title}, mimetype="application/xml")

    def __ipa_response(self):

        self.app.package.open()
        return HttpResponse(content=self.app.package, mimetype="application/octet-stream")

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

