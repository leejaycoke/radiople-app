from io import BytesIO

from mutagen.mp3 import MP3

from radiople.config import config

from radiople.service.s3 import S3Service


class AudioService(S3Service):

    @property
    def region(self):
        return config.audio.s3.region

    @property
    def access_key(self):
        return config.audio.s3.access_key

    @property
    def secret_key(self):
        return config.audio.s3.secret_key

    @property
    def bucket(self):
        return config.audio.s3.bucket

    @property
    def max_content_length(self):
        return config.audio.upload.max_size

    @property
    def acl(self):
        return 'private'

    @property
    def storage_class(self):
        return 'REDUCED_REDUNDANCY'

    @property
    def allowed_mimes(self):
        return set(['audio/mpeg', 'audio/mp3'])

    def validate(self, upload_file, **kwargs):
        try:
            mp3 = MP3(upload_file)

            if not self.allowed_mimes & mp3.mime:
                return False
            return 'audio/mpeg'
        except:
            return False


service = AudioService()
api_service = AudioService()
console_service = AudioService()
