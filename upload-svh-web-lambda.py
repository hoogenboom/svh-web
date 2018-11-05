import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:539127747096:deploySvhWeb')

    location = {
        "bucketName": 'build.svhproductions.com',
        "objectKey" : 'svhbuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"]=="BuildArtif":
                    location = artifact["location"]["s3Location"]

        print "Building SVH Web from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        prod_bucket = s3.Bucket('svhproductions.com')
        build_bucket = s3.Bucket(location["bucketName"])

        svhbuild_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], svhbuild_zip)

        with zipfile.ZipFile(svhbuild_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                prod_bucket.upload_fileobj(obj, nm,
                 ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                prod_bucket.Object(nm).Acl().put(ACL='public-read')

        print 'Job Done'
        topic.publish(Subject="SVH Web Deployed", Message="SVH Web deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="SVH Web Deploy Failed", Message="SVH Web was not deployed successfully")
        raise

    return 'Hello from Lambda'
