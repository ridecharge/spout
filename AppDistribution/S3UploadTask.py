from __future__ import absolute_import

from AppDistribution.CeleryApp import app
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os

@app.task
def upload_asset_to_s3(asset, access_key, secret_key, bucket):

    connection = S3Connection(access_key, secret_key)

    asset_bucket = connection.get_bucket(bucket)
    asset_path = asset.asset_file.path
    asset_file = open(asset_path)

    tag_string = "-".join([tag.name.replace("/", "-") for tag in asset.app.tags.all()])
    product = asset.app.product.name
    file_extension = os.path.splitext(asset_path)[-1]
    version = asset.app.version

    key_name = "%s-%s-%s%s" % (product, tag_string, version, file_extension)

    app_key = Key(asset_bucket, key_name)
    app_key.set_contents_from_file(open(asset_path))
    app_key.make_public()
    metadata = {'version' : version, 'product' : product}
    app_key.set_remote_metadata(metadata, {}, preserve_acl=True)
    asset.external_url = app_key.generate_url(0, query_auth=False)
    asset.save()


