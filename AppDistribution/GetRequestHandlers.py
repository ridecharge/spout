from AppDistribution import settings
from AppDistribution.models import App
import re
from zipfile import ZipFile
import biplist
from tempfile import mkdtemp
from django.http import HttpResponseRedirect, HttpResponse

from django.template import RequestContext, Context, Template
from django.shortcuts import get_object_or_404, render_to_response, render

class BaseGetRequestHandler(object):

    def __init__(self, request, app, extension):

        self.app = app
        self.extension = extension
        self.request = request

class iOSGetRequestHandler(BaseGetRequestHandler):

    handles_device_type = "IOS"
    handles_extensions = [".plist"]

    def respond(self):
        if self.extension == ".plist":
            return self.__plist_response()

    def __plist_response(self):
        """ Returns the formatted plist needed by iOS to download the ipa file."""
        theZip = ZipFile(self.app.primary_asset.asset_file.path)
        parsed_dict = self.__plist_from_ipa(theZip)

        url = "https://%s/app/%s/asset/%s" % ('spout.ridecharge.com', self.app.id, self.app.primary_asset.id) 
        bundle_id = parsed_dict['CFBundleIdentifier']
        bundle_version = parsed_dict['CFBundleVersion']
        app_title = parsed_dict['CFBundleName']

        template = "generic_enterprise_manifest.plist"
        theZip.close()
        return render_to_response(template, {"app_url": url,
                                    "bundle_identifier": bundle_id,
                                       "bundle_version": bundle_version,
                                            "app_title": app_title}, mimetype="application/xml")

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


class GetRequestHandler(object):

    handled_extensions = iOSGetRequestHandler.handles_extensions

    def __init__(self, request, app, extension):

        self.app = app
        self.extension = extension
        self.request = request

    def handler(self):

        if self.app.device_type in iOSGetRequestHandler.handles_device_type:
            return iOSGetRequestHandler(self.request, self.app, self.extension)


