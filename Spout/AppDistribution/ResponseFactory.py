from django.http.response import HttpResponseRedirect

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
        return "http://%s/app/%s.apk" % (self.request.get_host(), app.uuid)

    def ipa_url(self, app):
        return "itms-services://?action=download-manifest&url=http://%s/app/%s.plist" % (self.request.get_host(), app.uuid)

