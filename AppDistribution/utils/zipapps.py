from AppDistribution.models import *
from zipfile import ZipFile
import tempfile
from datetime import datetime
import shutil
import os


def zip_apps_and_assets(apps):

    working_dir = tempfile.mkdtemp()
    os.chdir(working_dir)
    root_dir = "%s" % datetime.now().strftime("%y-%m-%d-%H-%M-%S") 
    os.mkdir(root_dir)
    os.chdir(root_dir)
    zip_filename = "%s.zip" % root_dir


    for app in apps:

        folder_string = "%s - %s" % (app.name, app.creation_date.strftime("%Y %m %d %H-%M-%S"))

        os.mkdir(folder_string)
        shutil.copy(app.package.name, folder_string)

        app_assets = app.assets.all()

        for asset in app_assets:

            shutil.copy(asset.asset_file.name, folder_string)

    print working_dir

    os.chdir(working_dir)

    archive = shutil.make_archive(root_dir, "zip", root_dir=working_dir, base_dir=root_dir)

    thezip = ZipFile(archive, "r")

    return thezip

