from boto3.session import Session
from radiople.config import config

region_name = 'ap-northeast-1'
access_key_id = config.external.aws.access_key_id
secret_access_key = config.external.aws.secret_access_key

session = Session(aws_access_key_id=access_key_id,
                  aws_secret_access_key=secret_access_key,
                  region_name=region_name)


class Upload(object):

    session = session.client('s3')

    def upload_file(self, upload_file, key=None):
        if not key:
            key = upload_file.split('/')[-1]

        return self.session.upload_file(upload_file,
                                        self.bucket_name, key,
                                        ExtraArgs={'ACL': 'public-read'})

    def delete_file(self):
        pass


class S3Audio(Upload):

    pass


class S3Image(Upload):

    pass

s3_audio = S3Audio()
