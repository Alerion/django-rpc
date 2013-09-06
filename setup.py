import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='DjangoRpc',
    version='0.3',
    license='The MIT License (MIT)',
    author='Dmitriy Kostochko',
    author_email='alerion.um@gmail.com',
    packages=find_packages(exclude=['example', 'example.*']),
    url='https://django-rpc.readthedocs.org/',
    keywords='Django, RPC, API, jQuery',
    description='Django RPC for jQuery',
    long_description=README,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
