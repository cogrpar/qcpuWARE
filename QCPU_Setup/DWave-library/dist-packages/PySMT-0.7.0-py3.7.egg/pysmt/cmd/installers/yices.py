# Copyright 2014 Andrea Micheli and Marco Gario
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
import glob

from pysmt.cmd.installers.base import SolverInstaller, TemporaryPath


class YicesInstaller(SolverInstaller):

    SOLVER = "yices"

    def __init__(self, install_dir, bindings_dir, solver_version,
                 mirror_link=None, yicespy_version='HEAD'):
        pack = "x86_64-unknown-linux-gnu-static-gmp"
        archive_name = "yices-%s-%s.tar.gz" % (solver_version, pack)
        native_link = "http://yices.csl.sri.com/cgi-bin/yices2-newnewdownload.cgi?file={archive_name}&accept=I+Agree"
        SolverInstaller.__init__(self, install_dir=install_dir,
                                 bindings_dir=bindings_dir,
                                 solver_version=solver_version,
                                 archive_name=archive_name,
                                 native_link=native_link,
                                 mirror_link=mirror_link)

        self.extract_path = os.path.join(self.base_dir, "yices-%s" % self.solver_version)
        self.yices_path = os.path.join(self.bindings_dir, "yices_bin")
        self.yicespy_git_version = yicespy_version

    def install_yicespy(self):
        yicespy_git_version = self.yicespy_git_version
        yicespy_base_name =  "yicespy"
        yicespy_archive_name = "%s.tar.gz" % yicespy_base_name
        yicespy_archive = os.path.join(self.base_dir, yicespy_archive_name)
        yicespy_dir_path = os.path.join(self.base_dir,
                                        yicespy_base_name + "-" + yicespy_git_version)

        yicespy_download_link = "https://codeload.github.com/pysmt/yicespy/tar.gz/%s" % (yicespy_git_version)
        SolverInstaller.do_download(yicespy_download_link, yicespy_archive)

        SolverInstaller.clean_dir(yicespy_dir_path)

        SolverInstaller.untar(yicespy_archive, self.base_dir)
        # Build yicespy
        SolverInstaller.run_python("setup.py --yices-dir=%s -- build_ext bdist_wheel --dist-dir=%s " % (self.yices_path, self.base_dir),
                                   directory=yicespy_dir_path)
        wheel_file = glob.glob(os.path.join(self.base_dir, "yicespy") + "*.whl")[0]
        SolverInstaller.unzip(wheel_file, self.bindings_dir)

    def compile(self):
        # Prepare an empty folder for installing yices
        SolverInstaller.clean_dir(self.yices_path)

        SolverInstaller.run("bash ./install-yices %s" % self.yices_path,
                            directory=self.extract_path)

        self.install_yicespy()


    def get_installed_version(self):
        with TemporaryPath([self.bindings_dir]):
            version = None
            try:
                import yicespy
                v = yicespy.__dict__['__YICES_VERSION']
                m = yicespy.__dict__['__YICES_VERSION_MAJOR']
                p = yicespy.__dict__['__YICES_VERSION_PATCHLEVEL']
                version = "%d.%d.%d" % (v, m, p)
            finally:
                if "yicespy" in sys.modules:
                    del sys.modules["yicespy"]
                # Return None, without raising an exception
                # pylint: disable=lost-exception
                return version