from unittest import TestCase
import fudge
import sys
import forgit

from docopt import DocoptExit


class TestCLI(TestCase):

    def test_unknown_command(self):

        sys.argv = ['forgit', 'unknown']
        try:
            forgit.handle_command_line()
            assert False, 'Failed to raise DocoptExit'
        except DocoptExit as de:
            assert de.args[0] == 'Usage:\n'\
                            '    forgit mode [<repo_path>]\n'\
                            '    forgit contained-by [<branch>...]'

    @fudge.patch('forgit.contained_by')
    def test_contained_by_called(self, fake_forgit):

        sys.argv = ['forgit', 'contained-by']
        fake_forgit.expects_call().returns(True)
        forgit.handle_command_line()

    @fudge.patch('forgit.mode')
    def test_mode_called(self, fake_forgit):

        sys.argv = ['forgit', 'mode']
        fake_forgit.expects_call().returns(True)
        forgit.handle_command_line()

    @fudge.patch('forgit.mode')
    def test_mode_called_with_repo_path(self, fake_forgit):

        sys.argv = ['forgit', 'mode', '/path/repo']
        fake_forgit.expects_call().with_args(
            command='mode', branch=[], repo_path='/path/repo').returns(True)
        forgit.handle_command_line()


class TestMode(TestCase):

    @fudge.patch('forgit.os.walk', 'forgit.git_diff', 'forgit.git_checkout')
    def test_fully_qualified_path(self, fake_walk, fake_diff, fake_checkout):

        def walk():
            paths = [('/somepath/somerepo', [], ['somemodule.py', 'somemodule.pyc']),
                ('/somepath/somerepo/somemodule', [], ['somemodule.py', 'somemodule.pyc'])]
            for path in paths:
                yield path

        fake_walk.expects_call().with_args('/somepath/somerepo').returns(walk())

        fake_diff.expects_call().returns(
            'diff --git a/somemodule.py b/somemodule.py\n'\
            'old mode 100644\n'\
            'new mode 100755\n'
        ).next_call().returns(
            'diff --git a/somemodule/somemodule.py b/somemodule/somemodule.py\n'\
            'old mode 100644\n'\
            'new mode 100755\n'
        )

        fake_checkout.expects_call().with_args('somemodule.py').\
            next_call().with_args('somemodule/somemodule.py')

        forgit.mode('/somepath/somerepo')

    @fudge.patch('forgit.os.walk')
    def test_ignores_git_dir(self, fake_walk):

        def walk():
            paths = [('/somepath/somerepo/.git', [], ['somemodule.py', 'somemodule.pyc'])]
            for path in paths:
                yield path

        fake_walk.expects_call().with_args('/somepath/somerepo').returns(walk())

        forgit.mode('/somepath/somerepo')
