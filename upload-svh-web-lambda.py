import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:539127747096:deploySvhWeb')

    try:
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

        print 'Job Done'
        topic.publish(Subject="SVH Web Deployed", Message="SVH Web deployed successfully")
    except:
        topic.publish(Subject="SVH Web Deploy Failed", Message="SVH Web was not deployed successfully")
        raise

    return 'Hello from Lambda'
