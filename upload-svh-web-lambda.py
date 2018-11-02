import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

    prod_bucket = s3.Bucket('svhproductions.com')
    build_bucket = s3.Bucket('build.svhproductions.com')

    svhbuild_zip = StringIO.StringIO()
    build_bucket.download_fileobj('svhbuild.zip', svhbuild_zip)

    with zipfile.ZipFile(svhbuild_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            prod_bucket.upload_fileobj(obj, nm,
             ExtraArgs={'ContentType':  mimetypes.guess_type(nm)[0]})
            prod_bucket.Object(nm).Acl().put(ACL='public-read')

    return 'Hello from Lambda'
