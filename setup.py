# coding=utf-8
# author: Gao Xiang
# email:  xgao85@gmail.com
# date:   2018-10-19 17:33:23
import shutil
import os
import sys
from setuptools import setup
from distutils.extension import Extension
from distutils.command.clean import clean
from setuptools.command.install import install

try:
    from Cython.Distutils import build_ext
except:
    print('Install Cython first: pip install Cython')
    sys.exit(1)

MODULE_NAME = "u_shape_framework"
SRC_DIR = "u_shape_framework"
IGNORE_FILES = ["__init__.py"]


def travel_path(dir, files=None, folders=None, extension_list=('py',)):
    if folders is None:
        folders = []
    if files is None:
        files = []
    folders.append(dir)
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            if '.' in path:
                _, extension = path.rsplit('.', 1)
                if extension.lower() in extension_list and file not in IGNORE_FILES:
                    files.append(path)
        elif os.path.isdir(path):
            travel_path(path, files, folders, extension_list)


def get_extensions():
    py_files = []
    travel_path(MODULE_NAME, files=py_files)
    ext_names = map(lambda x: x.replace(os.path.sep, '.')[:-3], py_files)

    def make_extension(ext_name):
        ext_path = ext_name.replace('.', os.path.sep) + '.py'
        return Extension(ext_name, [ext_path], include_dirs=['.'])

    extensions = map(lambda x: make_extension(x), ext_names)
    return extensions


def get_packages():
    folders = []
    travel_path(MODULE_NAME, folders=folders)
    packages = map(lambda x: x.replace('/', '.'), folders)
    return packages


def get_requirements():
    with open('requirements.txt') as fp:
        install_requires = fp.read()
    return install_requires.split('\n')


class CleanCode(object):

    def clean_build(self, distribution):
        clean_command = clean(distribution)
        clean_command.all = True
        clean_command.finalize_options()
        clean_command.run()

    def delete_source_code(self, target_dir):
        source_file_list = []
        travel_path(target_dir, files=source_file_list, extension_list=('py', 'pyc', 'c'))
        for source_file in source_file_list:
            if os.path.basename(source_file) not in IGNORE_FILES:
                os.remove(source_file)

    def copy_so(self, build_path, source_code_path):
        self._copy_so(build_path, build_path, source_code_path)

    def _copy_so(self, target_dir, build_base_dir, target_base_dir):
        for file in os.listdir(target_dir):
            path = os.path.join(target_dir, file)
            if os.path.isfile(path) and path.endswith('.so'):
                new_path = path.replace(build_base_dir, target_base_dir)
                shutil.copyfile(path, new_path)
            elif os.path.isdir(path):
                self._copy_so(path, build_base_dir, target_base_dir)


class CustomBuildExt(build_ext, CleanCode):

    def run(self):
        build_ext.run(self)

        source_code_path = MODULE_NAME
        build_path = os.path.join(self.build_lib, MODULE_NAME)
        self.copy_so(build_path, source_code_path)
        if not {'install', 'bdist_wheel'} & set(self.distribution.commands):
            self.clean_build(self.distribution)
        self.delete_source_code(source_code_path)


class CustomInstall(install, CleanCode):

    def run(self):
        install.run(self)

        source_code_path = os.path.join(self.install_lib, MODULE_NAME)
        self.delete_source_code(source_code_path)
        if 'bdist_wheel' not in self.distribution.commands:
            self.clean_build(self.distribution)


setup(
    name=MODULE_NAME,
    version="0.6.1",
    packages=get_packages(),
    ext_modules=get_extensions(),
    cmdclass={
        'build_ext': CustomBuildExt,
        'install': CustomInstall,
    },
    install_requires=get_requirements(),
)
