import sys
import zipfile
from django.contrib.contenttypes.models import ContentType
from django.db import models
from file_import.compat import AUTH_USER_MODEL

if sys.version_info >= (3,0):
    unicode = str

class ImportLog(models.Model):
    """ A log of all import attempts """
    name = models.CharField(max_length=255, verbose_name='job name')
    user = models.ForeignKey(AUTH_USER_MODEL, editable=False, related_name='file_import_log')
    date = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    import_file = models.FileField(upload_to='import_file')
    update_key = models.CharField(max_length=200, blank=True)
    file_field = models.CharField(max_length=200, blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name='destination model')
    
    def __unicode__(self):
        return unicode(self.name)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.import_file or not zipfile.is_zipfile(self.import_file):
            raise ValidationError("The file selected does not appear to be a ZIP archive. Please try again.")
