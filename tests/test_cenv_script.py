#!/usr/bin/env python

"""Tests for `cenv_script` package."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
import unittest
from click.testing import CliRunner

from cenv_script import cenv_script
from cenv_script import cli


@contextmanager
def working_directory(directory):
    owd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(owd)


class TestCenv(unittest.TestCase):
    """Tests for `cenv_script` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_env_file_exists(self):
        with TemporaryDirectory() as tmpdir:
            work_dir = os.path.join(tmpdir, "foo", "bar")
            os.makedirs(work_dir)
            env_file = os.path.join(tmpdir, "environment.yml")
            with open(env_file, "w") as f:
                f.write("\n")
            with working_directory(work_dir):
                self.assertEqual(
                    cenv_script.find_environment_file(), Path(env_file).resolve(),
                )

    def test_env_file_not_found(self):
        # env file must not be in tmp directory path or its ancestors!
        # otherwise test will not work as expected!
        with TemporaryDirectory() as tmpdir:
            with working_directory(tmpdir):
                with self.assertRaises(cenv_script.CondaEnvException):
                    cenv_script.find_environment_file()

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        print(help_result.output)
        assert "--help" in help_result.output
