django-file-import
====================

Hello!

<!--
[![Build Status](https://travis-ci.org/burke-software/django-file-import.png?branch=master)](https://travis-ci.org/burke-software/django-file-import)
-->

## Install

1. pip install django-file-import
1. Add 'file_import' to INSTALLED APPS
1. Add file_import to urls.py like
urlpatterns += url(r'^file_import/', include('file_import.urls')),
1. syncdb (you may use south)

## Usage

Go to /file_import/start_import/ or use the admin interface.
