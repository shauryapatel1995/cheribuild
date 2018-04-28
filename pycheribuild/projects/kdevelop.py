#
# Copyright (c) 2016 Alex Richardson
# All rights reserved.
#
# This software was developed by SRI International and the University of
# Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-10-C-0237
# ("CTSRD"), as part of the DARPA CRASH research programme.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
from .project import *
from ..utils import *


# doesn't seem to be part of distro packages
class BuildLibKompareDiff2(CMakeProject):
    defaultCMakeBuildType = "Debug"
    repository = "git://anongit.kde.org/libkomparediff2.git"
    defaultInstallDir = CMakeProject._installToBootstrapTools

    def __init__(self, config: CheriConfig):
        super().__init__(config)


class BuildKDevplatform(CMakeProject):
    dependencies = ["libkomparediff2"]
    defaultCMakeBuildType = "Debug"
    repository = "https://github.com/arichardson/kdevplatform.git"
    defaultInstallDir = CMakeProject._installToBootstrapTools
    appendCheriBitsToBuildDir = True

    def __init__(self, config: CheriConfig):
        super().__init__(config)
        self.gitBranch = "cheri"
        self.add_cmake_options(BUILD_git=False)


class BuildKDevelop(CMakeProject):
    dependencies = ["kdevplatform", "llvm"]
    defaultCMakeBuildType = "Debug"
    repository = "https://github.com/arichardson/kdevelop.git"
    defaultInstallDir = CMakeProject._installToBootstrapTools
    appendCheriBitsToBuildDir = True

    def __init__(self, config: CheriConfig):
        super().__init__(config)
        # Tell kdevelop to use the CHERI clang and install the wrapper script that sets the right environment variables
        self.add_cmake_options(LLVM_ROOT=self.config.sdkDir, INSTALL_KDEVELOP_LAUNCH_WRAPPER=True)
        self.gitBranch = "cheri"


class StartKDevelop(SimpleProject):
    target = "run-kdevelop"
    dependencies = ["kdevelop"]

    def __init__(self, config: CheriConfig):
        super().__init__(config)
        self._addRequiredSystemTool("cmake")
        self._addRequiredSystemTool("qtpaths")

    def process(self):
        kdevelopBinary = BuildKDevelop.getInstallDir(self.config) / "bin/start-kdevelop.py"
        if not kdevelopBinary.exists():
            self.dependencyError("KDevelop is missing:", kdevelopBinary,
                                 installInstructions="Run `cheribuild.py kdevelop` or `cheribuild.py " +
                                                     self.target + " -d`.")
        runCmd(kdevelopBinary, "--ps")
