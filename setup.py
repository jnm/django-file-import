from setuptools import setup, find_packages

setup(
    name = 'django-file-import',
    version = '0.0',
    author = 'John Milner',
    author_email = 'jmilner@burkesoftware.com',
    description = ('Import many files to FileFields at once by uploading a single ZIP archive'),
    license = 'BSD',
    keywords = 'django import zip archive filefield fieldfile batch',
    url = 'https://github.com/jnm/django-file-import',
    packages=find_packages(),
    include_package_data=True,
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
        'south',
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=['django']
)
