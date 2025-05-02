from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import sys


class BuildScriptMixin:
    def run_build_script(self):
        subprocess.check_call([sys.executable, "scripts/build.py"])


class CustomInstallCommand(install, BuildScriptMixin):
    def run(self):
        super().run()
        self.run_build_script()


class CustomDevelopCommand(develop, BuildScriptMixin):
    def run(self):
        super().run()
        self.run_build_script()


setup(
    packages=find_packages(),
    include_package_data=True,
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
    },
)
