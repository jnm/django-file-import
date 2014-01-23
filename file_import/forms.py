from django import forms
from django.contrib.contenttypes.models import ContentType

from file_import.models import ImportLog

class ImportForm(forms.ModelForm):
    class Meta:
        model = ImportLog
        fields = ('name', 'import_file', 'content_type')

class FieldSelectionForm(forms.Form):
    update_key = forms.ChoiceField()
    file_field = forms.ChoiceField()
