"""Main module."""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import yaml

ENV_FILE = "environment.yml"


class CondaEnvException(Exception):
    pass


def find_environment_file():
    p = Path(os.getcwd()).resolve()
    while True:
        env_file = p / ENV_FILE
        if env_file.is_file():
            return env_file
        if p.parents:
            p = p.parent
            continue
        raise CondaEnvException(
            "environment.yml file not find in '%s' or in any of parent directories"
            % os.getcwd()
        )


def get_conda():
    if sys.platform.startswith("win"):
        return "conda.bat"
    return "conda"


def print_args(args):
    def escape(arg):
        if arg.find(" ") > -1:
            return '"%s"' % arg
        return arg

    print(">>>", " ".join(map(escape, args)))


def in_directory(file_name, dir_name):
    return os.path.realpath(file_name).startswith(os.path.realpath(dir_name) + os.sep)


class CondaEnv:
    def __init__(self):
        super().__init__()
        self._conda = get_conda()
        self._env_file = find_environment_file()
        with open(self._env_file) as f:
            self._data = yaml.safe_load(f)
        data = subprocess.check_output([self._conda, "info", "--json"])
        data = json.loads(data)
        active_name = data["active_prefix_name"]
        active_prefix = data["active_prefix"]
        if active_name != self._data["name"]:
            raise CondaEnvException(
                f"Active environment is {active_name} but {ENV_FILE} points to {self._data['name']}"
            )
        if "prefix" in self._data and active_prefix != self._data["prefix"]:
            raise CondaEnvException(
                f"Active environment is located in {active_prefix} but {ENV_FILE} points to {self._data['prefix']}"
            )

        python_exe = shutil.which("python")
        if not python_exe:
            raise CondaEnvException("Python not found in path")
        # The following check is quite strict, but I think it is better to keep it. See comments below.
        if not in_directory(python_exe, active_prefix):
            raise CondaEnvException(
                f"Python '{python_exe}' is not in conda prefix '{active_prefix}'"
            )

    @staticmethod
    def pip_cmd(args):
        return [
            # disabled due to: https://github.com/conda/conda/issues/9572
            # "run", "-n", self._data["name"], "python",
            # This can lead to installing into the wrong place, but checks in the __init__ should help
            os.path.realpath(shutil.which("python")),
            "-m",
            "pip",
        ] + args

    def _exec_pip(self, args):
        args = self.pip_cmd(args)
        # return self._exec_conda(args)
        print_args(args)
        exit_code = subprocess.call(args)
        print("-" * 80)
        print("python -m pip finished with exit code: %d" % exit_code)
        return exit_code

    def _exec_conda(self, args):
        args = [self._conda] + args
        print_args(args)
        exit_code = subprocess.call(args)
        print("-" * 80)
        print("conda finished with exit code: %d" % exit_code)
        return exit_code

    @staticmethod
    def parse_pkg(pkg_spec: str):
        m = re.match(r"^(git|hg|svn|bzr)\+.*|^[\w-]+", pkg_spec)
        if m:
            return m.group(0)
        raise CondaEnvException("Failed to parse package specification '%s'" % pkg_spec)

    def _spec_add_package(self, deps: List[str], package: str) -> bool:
        """Add given package to a deps list if it is not already there

        :param deps: list of current dependencies
        :param package: package spec that should be added
        :return: True when deps list was mutated, False overwise
        """
        name = self.parse_pkg(package)
        for i, pkg in enumerate(deps):
            if not isinstance(pkg, str):
                continue
            pkg = pkg.strip()
            n = self.parse_pkg(pkg)
            if n == name:
                if pkg != package:
                    print(f"Updating spec from {pkg} to {package} ...")
                    deps[i] = package
                    break
                print(f"Same package spec already found: {pkg}")
                return False
        else:
            print(f"Adding package spec {package} to dependencies ...")
            deps.append(package)
        return True

    def install(self, package: str):
        package = package.strip()
        deps = self._get_deps()
        if not self._spec_add_package(deps, package):
            return

        exit_code = self._exec_conda(["install", "-n", self._data["name"], package])
        if exit_code != 0:
            raise CondaEnvException("Bad conda exitcode: %d" % exit_code)

        name = self.parse_pkg(package)
        if not self.check_installed(name):
            raise CondaEnvException(f"Package {name} was not installed")
        print("Verified that package has been installed")
        self._write_env_file()

    def check_installed(self, name):
        data = subprocess.check_output(
            [self._conda, "env", "export", "-n", self._data["name"]]
        )
        data = yaml.safe_load(data.decode("utf-8"))
        names = set(
            self.parse_pkg(x)
            for x in data.get("dependencies", [])
            if isinstance(x, str)
        )
        return name in names

    def pip_install(self, package: str):
        package = package.strip()
        deps = self._get_pip_deps()
        if not self._spec_add_package(deps, package):
            return

        exit_code = self._exec_pip(["install", package])
        if exit_code != 0:
            raise CondaEnvException("Bad conda+pip exitcode: %d" % exit_code)

        name = self.parse_pkg(package)
        if not self.check_pip_installed(name):
            raise CondaEnvException(
                f"Package {name} was not installed (not found in pip freeze)"
            )
        print("Verified that package has been installed")
        self._write_env_file()

    def check_pip_installed(self, name):
        data = subprocess.check_output(self.pip_cmd(["freeze"]))
        names = set(
            self.parse_pkg(l.strip()) for l in data.decode("utf-8").split("\n") if l
        )
        return name in names

    def _spec_rm_package(
        self, deps: List[str], package: str
    ) -> (Optional[str], List[str]):
        """Remove package from the deps list if it is present

        :param deps: current list of packages
        :param package: spec containing a package name that should be removed
        :return: tuple
          - package name if it was found or none
          - new list of packages
        """
        name = self.parse_pkg(package)
        new_deps = []
        to_remove = 0
        for pkg in deps:
            if not isinstance(pkg, str):
                continue
            n = self.parse_pkg(pkg)
            if n == name:
                to_remove += 1
                continue
            new_deps.append(pkg)

        if to_remove == 0:
            return None, new_deps

        if to_remove > 1:
            print("Warning: more than one spec matched")
        return name, new_deps

    def remove(self, package: str):
        package = package.strip()
        name, new_deps = self._spec_rm_package(self._get_deps(), package)
        self._set_deps(new_deps)
        if name is None:
            print("Specified package '%s' not found" % self.parse_pkg(package))
            return

        exit_code = self._exec_conda(["remove", "-n", self._data["name"], name])
        if exit_code != 0:
            raise CondaEnvException("Bad conda exitcode: %d" % exit_code)

        if self.check_installed(name):
            raise CondaEnvException(f"Package {name} was not removed")
        self._write_env_file()

    def pip_remove(self, package: str):
        package = package.strip()
        name, new_deps = self._spec_rm_package(self._get_pip_deps(), package)
        self._set_pip_deps(new_deps)
        if name is None:
            print(
                "Specified package '%s' not found in pip section"
                % self.parse_pkg(package)
            )
            return

        exit_code = self._exec_pip(["uninstall", name])
        if exit_code != 0:
            raise CondaEnvException("Bad conda exitcode: %d" % exit_code)

        if self.check_pip_installed(name):
            raise CondaEnvException(
                f"Package {name} was not removed (found in pip freeze)"
            )
        self._write_env_file()

    def _write_env_file(self):
        with open(self._env_file, "w") as f:
            yaml.dump(self._data, f, sort_keys=False)
        print("Updated %s" % ENV_FILE)

    def _get_deps(self):
        if "dependencies" not in self._data:
            self._data["dependencies"] = []
        return self._data["dependencies"]

    def _set_deps(self, value):
        self._data["dependencies"] = value

    def _get_pip_deps(self):
        for item in self._get_deps():
            if isinstance(item, dict) and "pip" in item:
                return item["pip"]
        self._data["dependencies"].append({"pip": []})
        return self._data["dependencies"][-1]["pip"]

    def _set_pip_deps(self, value):
        for item in self._get_deps():
            if isinstance(item, dict) and "pip" in item:
                item["pip"] = value
                return
        self._data["dependencies"].append({"pip": []})
        self._data["dependencies"][-1]["pip"] = value
