from django.http.response import HttpResponseRedirect
import re
from django.conf import settings

class PackageHttpResponseFactory(object):

    def __init__(self, request):
        self.request = request

    def response(self, app):
 
        if app.device_type == "ANDROID":
            return HttpResponseRedirect(self.apk_url(app))
        elif app.device_type == "IOS":
            HttpResponseRedirect.allowed_schemes += ['itms-services']
            response = HttpResponseRedirect(self.ipa_url(app))
            return response

       

    def package_url(self, app):

        if app.device_type == "ANDROID":
            return self.apk_url(app)
        elif app.device_type == "IOS":
            return self.ipa_url(app)

    def apk_url(self, app):
        return "http://%s/app/%s/asset/%s.apk" % (self.request.get_host(), app.id, app.primary_asset.id)

    def ipa_url(self, app):
        user_agent_string = self.request.META['HTTP_USER_AGENT']

        if "iPhone" in user_agent_string:
            url_string = "itms-services://?action=download-manifest&url=https://%s/app/%s/asset/%s.plist" % (settings.FQ_HOSTNAME, app.id, app.primary_asset.id)
        else:
            url_string = "https://%s/app/%s/asset/%s" % (settings.FQ_HOSTNAME, app.id, app.primary_asset.id)
        print url_string
        return url_string

