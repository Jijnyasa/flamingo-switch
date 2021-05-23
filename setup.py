import setuptools
from os import system
import os



with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

from setuptools.command.install import install
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'flam_switch_config.json')
oci_path = os.path.abspath("~/.oci/")
class CustomInstall(install):
    def run(self):
        install.run(self)
        system("echo 'copying file'")
        system("cp " + config_path + " " +  "~/.oci/")


system("echo 'copying file'")
system("cp " + config_path + " " +  "~/.oci/")
dependencies = ['certifi>=2.40', 'Click>=5.0', 'termcolor', 'retrying']


setuptools.setup(
    name="flamingo-switch", # Replace with your own username
    version="0.0.1",
    author="Naveen Aggarwal",
    author_email="naveen.a.aggarwal@oracle.com",
    description="Work with preprod happily",
    install_requires=dependencies,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
        entry_points = {
        'console_scripts': [
            'flamingo-switch=models.cli:cli'
        ]
    },
    cmdclass={'install': CustomInstall}
)