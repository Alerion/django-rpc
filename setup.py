import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='DjangoRpc',
    version='0.2',
    license='Apache License 2.0',
    author='Dmitriy Kostochko',
    author_email='alerion.um@gmail.com',
    packages=find_packages(exclude=['example', 'example.*']),
    url='https://github.com/Alerion/Django-RPC',
    keywords='Django, RPC, API, jQuery',
    description='Django RPC for jQuery',
    long_description=README,
    install_requires=[],
)
