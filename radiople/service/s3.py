from io import BytesIO
from io import StringIO
from abc import ABCMeta
from abc import abstractproperty
from abc import abstractmethod

from uuid import uuid4

from boto3.session import Session
from radiople.config import config


BASE_URL = "https://s3-ap-northeast-1.amazonaws.com/{bucket}/{filename}"


class FileType(object):

    MULTIPART = 'multipart'
    FILE = 'file'
    PATH = "path"


class S3Service(metaclass=ABCMeta):

    def __init__(self):
        self.session = Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

        self.s3_resource = self.session.resource('s3')
        self.s3_client = self.session.client('s3')

    @abstractproperty
    def region(self):
        raise NotImplemented

    @abstractproperty
    def access_key(self):
        raise NotImplemented

    @abstractproperty
    def secret_key(self):
        raise NotImplemented

    @abstractproperty
    def max_content_length(self):
        raise NotImplemented

    @abstractproperty
    def bucket(self):
        raise NotImplemented

    @abstractproperty
    def acl(self):
        raise NotImplemented

    @abstractproperty
    def storage_class(self):
        raise NotImplemented

    @abstractproperty
    def allowed_mimes(self):
        raise NotImplemented

    @abstractmethod
    def validate(self, upload_file):
        raise NotImplemented

    def upload(self, upload_file, file_type=FileType.MULTIPART):
        filename = uuid4().hex
        content_type = self.validate(upload_file)
        if not content_type:
            return None

        if file_type == FileType.MULTIPART:
            upload_file.stream.seek(0)
        elif file_type == FileType.PATH:
            upload_file = open(upload_file, 'rb')

        try:
            self.s3_resource.Object(self.bucket, filename) \
                .put(Body=upload_file, ACL=self.acl,
                     StorageClass=self.storage_class,
                     ContentType=content_type)
            return BASE_URL.format(bucket=self.bucket, filename=filename)
        except Exception as e:
            return None
        finally:
            if file_type == FileType.MULTIPART:
                upload_file.flush()

    def get(self, filename):
        try:
            return self.s3_resource.Object(self.bucket, filename)
        except Exception as e:
            print(str(e))

    def get_object(self, filename):
        try:
            return self.get(filename).get().get('Body')
        except Exception as e:
            print(str(e))

    def get_metadata(self, filename):
        try:
            return self.get(filename).metadata
        except Exception as e:
            print(str(e))

    def delete(self, filename):
        try:
            return self.get(filename).delete()
        except Exception as e:
            print(str(e))

    def generate_signed_post(self, key, mime, expires_in=3600, success_action_redirect=None, **meta):
        params = {
            'Bucket': self.bucket,
            'Key': key,
            'ExpiresIn': expires_in,
            'Fields': {
                'acl': self.acl,
                'Content-Type': mime,
                'x-amz-storage-class': self.storage_class,
            },
            'Conditions': [
                {'acl': self.acl},
                ['content-length-range', 0, self.max_content_length],
                ['eq', '$Content-Type', mime],
                ['eq', '$x-amz-storage-class', self.storage_class],
            ]
        }

        if success_action_redirect:
            params['Fields']['success_action_redirect'] = success_action_redirect
            params['Conditions'].append(
                ['eq', '$success_action_redirect', success_action_redirect])

        if meta:
            params['Fields'].update(meta)
            for key, value in meta.items():
                params['Conditions'].append(['eq', '$' + key, value])

        return self.s3_client.generate_presigned_post(**params)
