from django.conf.urls import patterns, url
from file_import import views

urlpatterns = patterns('',
    url('^start_import/$', views.start_import, name='file_import-start_import'),
    url('^choose_fields/(?P<import_log_id>\d+)/$', views.choose_fields, name='file_import-choose_fields'),
    url('^do_import/(?P<import_log_id>\d+)/$', views.do_import, name='file_import-do_import'),
)
