#from distutils.core import setup
from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt',session='')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='pdfgrep',
    packages=['pdfgrep'],
    version='0.8',
    description='a grep tool for pdf files',
    author='Amro Diab',
    author_email='adiab@linuxmail.org',
    url='https://github.com/adiabuk/pdfgrep',
    download_url='https://github.com/adiabuk/pdfgrep/archive/0.8.tar.gz',
    keywords=['pdf', 'grep'],
    install_requires=reqs,
    classifiers=[],
)
