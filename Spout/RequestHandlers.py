from Spout import settings
import re
from zipfile import ZipFile
import biplist

import UploadHandlers
import GetRequestHandlers

class AndroidRequestHandler(object):

    handles = dict({ 'apk' : True })

    def __init__(self, request):

        if request.method == 'GET':
            handler = AndroidGetRequestHandler(request)

        if request.method == 'POST':
            handler = AndroidPackageHandler(request)

        self.respond = handler.respond

class iOSRequestHandler(object):

    handles = dict({ 'plist' : True, 'ipa' : True, 'dSYM.zip' : True })


    def __init__(self, request):

        if request.method == 'GET':
            handler = iOSGetRequestHandler(request)

        if request.method == 'POST':
            handler = iOSPackageHandler(request)

        self.respond = handler.respond

