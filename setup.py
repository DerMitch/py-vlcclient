import os

from setuptools import setup, find_packages


setup(
    name='vlcclient',
    version='0.1.0',
    description="Control VLC instances using python.",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    license='BSD',
    url="https://github.com/DerMitch/py-vlcclient",
    author='Michael Mayr',
    author_email='michael@michfrm.net',
    py_modules=['vlcclient'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
    ],
)