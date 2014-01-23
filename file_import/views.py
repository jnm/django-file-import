import sys
import zipfile
import django
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from .models import ImportLog
from .forms import ImportForm, FieldSelectionForm

if sys.version_info >= (3,0):
    unicode = str

@staff_member_required
def start_import(request):
    """ View to create a new import record
    """
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_log = form.save(commit=False)
            import_log.user = request.user
            import_log.save()
            return HttpResponseRedirect(reverse(choose_fields, kwargs={'import_log_id': import_log.id}))
    else:
        form = ImportForm()
    if request.user.is_superuser:
        permitted = ContentType.objects.all()
    else:
        permitted = ContentType.objects.filter(
            Q(permission__group__user=request.user, permission__codename__startswith="change_") |
            Q(permission__user=request.user, permission__codename__startswith="change_")).distinct()
    usable_choices = []
    for content_type in permitted:
        if content_type.model_class() is None: # wtf, mate?
            continue
        for field_name in content_type.model_class()._meta.get_all_field_names():
            field, model, direct, m2m = (
                content_type.model_class()._meta.get_field_by_name(field_name)
            )
            if issubclass(type(field), django.db.models.FileField):
                usable_choices.append((content_type.pk, u'{} ({})'.format(
                    content_type,
                    content_type.model_class()._meta.app_label # reduce ambiguity
                )))
                break
    form.fields['content_type'].choices = usable_choices
    return render_to_response(
        'file_import/import.html',
        {'form':form,},
        RequestContext(request, {})
    )

@staff_member_required
def choose_fields(request, import_log_id):
    import_log = get_object_or_404(ImportLog, id=import_log_id)
    if not request.user.is_superuser and import_log.user != request.user:
        raise SuspiciousOperation("Non-superuser attempting to view other user's import")
    unique_field_names = []
    file_field_names = []
    for field_name in import_log.content_type.model_class()._meta.get_all_field_names():
        if field_name.endswith('_ptr'):
            # duplicate of a parent's pk; skip it
            continue
        field, model, direct, m2m = (
            import_log.content_type.model_class()._meta.get_field_by_name(field_name)
        )
        if hasattr(field, 'unique') and field.unique:
            unique_field_names.append(field.name)
        if issubclass(type(field), django.db.models.FileField):
            file_field_names.append(field.name)
    if request.method == 'POST':
        form = FieldSelectionForm(request.POST)
        form.fields['update_key'].choices = zip(unique_field_names, unique_field_names) 
        form.fields['file_field'].choices = zip(file_field_names, file_field_names) 
        if form.is_valid():
            import_log.update_key = form.cleaned_data['update_key']
            import_log.file_field = form.cleaned_data['file_field']
            import_log.save()
            return HttpResponseRedirect(reverse(do_import,
                kwargs={'import_log_id': import_log.id}))
    else:
        form = FieldSelectionForm()
        form.fields['update_key'].choices = zip(unique_field_names, unique_field_names) 
        form.fields['file_field'].choices = zip(file_field_names, file_field_names) 
    return render_to_response(
        'file_import/import.html',
        {'form':form,},
        RequestContext(request, {})
    )

@staff_member_required
def do_import(request, import_log_id):
    import_log = get_object_or_404(ImportLog, id=import_log_id)
    if not request.user.is_superuser and import_log.user != request.user:
        raise SuspiciousOperation("Non-superuser attempting to run other user's import")
    manager = import_log.content_type.model_class().objects
    lookup = u'{}__iexact'.format(import_log.update_key)
    zippy = zipfile.ZipFile(import_log.import_file, 'r')
    successes = []
    failures = []
    for filename in zippy.namelist():
        if filename.endswith('/'):
            # skip directories
            continue
        name_without_path = filename.split(u'/')[-1]
        name_without_extension = name_without_path.split(u'.')
        if len(name_without_extension) > 1:
            name_without_extension = u''.join(name_without_extension[:-1])
        else:
            name_without_extension = name_without_path
        try:
            try:
                destination = manager.get(**{lookup: name_without_extension})
            except:
                destination = manager.get(**{lookup: name_without_path})
            content = django.core.files.base.ContentFile(zippy.read(filename))
            getattr(destination, import_log.file_field).save(name_without_path, content)
            content.close()
            successes.append(
                u'{}: modified {} successfully!\n'.format(filename, destination))
        except Exception as e:
            failures.append(u'{}: {}\n'.format(filename, e))
    zippy.close()

    return render_to_response(
        'file_import/do_import.html',
        {'successes': successes, 'failures': failures},
        RequestContext(request, {})
    )
