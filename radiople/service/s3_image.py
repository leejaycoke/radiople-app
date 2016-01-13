from PIL import Image

from radiople.config import config

from radiople.service.s3 import S3Service


class ImageService(S3Service):

    @property
    def region(self):
        return config.image.s3.region

    @property
    def access_key(self):
        return config.image.s3.access_key

    @property
    def secret_key(self):
        return config.image.s3.secret_key

    @property
    def bucket(self):
        return config.image.s3.bucket

    @property
    def max_content_length(self):
        return config.image.upload.max_size

    @property
    def acl(self):
        return 'private'

    @property
    def storage_class(self):
        return 'REDUCED_REDUNDANCY'

    @property
    def allowed_mimes(self):
        return ['image/jpeg', 'image/png']

    def validate(self, upload_file, **kwargs):
        try:
            image = Image.open(upload_file)
            mime = 'image/' + image.format.lower()
            if mime not in self.allowed_mimes:
                return False
            return mime
        except Exception as e:
            print(">>>>>>>>>>> validate image error ", str(e))
            return False


service = ImageService()
api_service = ImageService()
console_service = ImageService()
