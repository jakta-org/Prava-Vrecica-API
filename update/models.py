import re
import os

from django.core.files.uploadedfile import UploadedFile
from django.forms import ValidationError
from . import settings
from django.db import models
from django.conf import settings as proj_settings

# Mapping model
class Mapping(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    coordinates = models.JSONField()
    data = models.JSONField(blank=True, null=True)
    upvotes = models.IntegerField(default=0)
    creator_id = models.IntegerField(null=True, blank=True)

class Localization(models.Model):
    AI_version = models.CharField(max_length=100)
    tag = models.CharField(max_length=10, unique=True)
    data = models.JSONField()

class AI_regions(models.Model):
    version = models.CharField(max_length=100)
    file = models.FileField(upload_to='ai_models/', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['version']

    # generates the next version number based on the latest version saved in the database
    # increment_segment is the segment of the version to increment (0 = major, 1 = minor, 2 = patch)
    @classmethod
    def get_next_version(cls, increment_segment = 2):
        # get the latest version
        latest_version = cls.objects.last().version

        # if there are no files, return the default version
        if latest_version is None:
            return settings.DEFAULT_VERSION

        # split the version into segments
        version_segments = [int(x) for x in latest_version.split('.')]

        # increment the specified segment
        version_segments[increment_segment] += 1

        # reset all segments after the incremented segment to 0
        for i in range(increment_segment + 1, len(version_segments)):
            version_segments[i] = 0

        # return the new version
        return '.'.join([str(x) for x in version_segments])

    # set the file name to the version number
    def save(self):
        self.set_appropriate_file_name()

        # save the file
        self.file.save(self.file.name, self.file, save=False)
        super().save()
        
    @classmethod
    def get_valid_version(cls, version):
        # if the version is None, generate a new version number
        if version is None:
            if settings.ACCEPT_NONE_VERSION_UPLOAD:
                return cls.get_next_version()
            raise ValidationError('Version number required')

        pattern = re.compile(settings.REGEX_VERSION)
        # check if the version is valid
        if not re.match(pattern, version):            
            raise ValidationError('Invalid version number')

    # check if the version is higher than the latest version
        if cls.objects.count() == 0:
            return version

        # check if that version already exists
        if cls.objects.filter(version=version).exists():
            if settings.ACCEPT_VERSION_REUPLOAD:
                return version
            raise ValidationError('Version already exists')

        return version

    # set the file name to the version number and maintain the file extension
    def set_appropriate_file_name(self):
        # get the file extension
        extension = os.path.splitext(self.file.name)[-1]
        self.file.name = self.version + extension

    @classmethod
    def is_valid_file(cls, file: UploadedFile):
        return True
        return self.file.name.endswith(settings.AI_FILE_EXTENSION)
    
    def delete(self, *args, **kwargs):
        os.remove(self.file.path)
        super().delete(*args, **kwargs)
    
    # override operator <
    # compares the version numbers as integers
    def __lt__(self, other):
        if not isinstance(other, AI_regions):
            raise TypeError('Cannot compare AI_regions with ' + str(type(other)))
        
        self_version_fragments = self.version.split('.')
        other_version_fragments = other.version.split('.')

        if len(self_version_fragments) != len(other_version_fragments):
            raise ValueError('Version numbers must have the same number of segments')
        for i in range(len(self_version_fragments)):
            if int(self_version_fragments[i]) < int(other_version_fragments[i]):
                return True
            elif int(self_version_fragments[i]) > int(other_version_fragments[i]):
                return False
        
        return False
    
    # override operator >
    def __gt__(self, other):
        return other < self
    
    # override operator ==
    def __eq__(self, other):
        return self.version == other.version

    def __str__(self):
        return self.name
    

