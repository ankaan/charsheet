import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'pyramid_persona',
    'deform',
    'deform_bootstrap',
    'SQLAlchemy',
    'waitress',
    'webhelpers',
    'transaction'
    ]

setup(name='charsheet',
      version='0.0',
      description='Nianze character sheet manager',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='charsheet',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = charsheet:main
      [console_scripts]
      initialize_charsheet_db = charsheet.scripts.initializedb:main
      """,
      )
