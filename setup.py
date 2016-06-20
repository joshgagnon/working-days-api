from setuptools import setup

setup(name='working-days-api',
      version='0.0.1',
      description='',
      url='http://github.com/joshgagnon/workig-days-api',
      author='Joshua Gagnon',
      author_email='josh.n.gagnon@gmail.com',
      license='MIT',
     # packages=['template-law-odf'],
      install_requires=[
          'flask',
          'psycopg2',
          'python-dateutil'
      ],
      zip_safe=False)
