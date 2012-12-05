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
                            '    forgit contained-by [<branches>...]'

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
            command='mode', branches=[], repo_path='/path/repo').returns(True)
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


class TestContained(TestCase):

    @fudge.patch('forgit.subprocess.check_output')
    def test_git_merged(self, fake_p):
        """
        Find the branches containing the commit.

        Verify * denoting current branch is removed.
        """
        # find branches containing the commit
        fake_p.expects_call().returns(
            '* master\n'\
            '  stage\n'\
            '  feature_branch\n'\
            '  feature_two_branch\n'
        )

        assert ['master', 'stage', 'feature_branch', 'feature_two_branch'] == forgit.git_merged('somecommit')

    @fudge.patch('forgit.subprocess.check_output')
    def test_git_verbose_branch_listing(self, fake_p):
        """
        Find the branches commit hash.

        Verify * denoting current branch is removed.
        """
        # find branches containing the commit
        fake_p.expects_call().returns(
            ' master fe942c68f40bc162746885a07ff4e40d6eeace7f 0.0.1 some feature commit message'
        )

        assert ['master','fe942c68f40bc162746885a07ff4e40d6eeace7f','0.0.1','some','feature','commit','message'] ==\
             forgit.git_merged('somecommit')

    @fudge.patch('forgit.subprocess.check_output',
        'forgit.delete_branches')
    def test_contained_by_prunes_nothing(self, fake_p, fake_d):
        """
        Verify nothing is merged with passed branch,
        therefore nothing is pruned.
        """
        # first call is to get branch commit
        # 2nd call is to find branches containing the commit
        fake_p.expects_call().returns(
            ' master fe942c68f40bc162746885a07ff4e40d6eeace7f 0.0.1 some feature commit message'
        ).next_call().returns(
            '* master\n'
        )

        fake_d.expects_call().with_args(set())
        sys.argv = ['forgit', 'contained-by', 'master']
        forgit.handle_command_line()

    @fudge.patch('forgit.subprocess.check_output',
        'forgit.delete_branches')
    def test_prune_contained_by(self, fake_p, fake_d):
        """
        Verify nothing is merged with passed branch,
        therefore nothing is pruned.
        """
        # first call is to get branch commit
        # 2nd call is to find branches containing the commit
        fake_p.expects_call().returns(
            ' master fe942c68f40bc162746885a07ff4e40d6eeace7f 0.0.1 some feature commit message'
        ).next_call().returns(
            '* master\n'\
            ' stage\n'\
            ' feature_branch\n'\
            ' feature_two_branch\n'
        )

        fake_d.expects_call().with_args(set(['stage', 'feature_branch', 'feature_two_branch']))
        sys.argv = ['forgit', 'contained-by', 'master']
        forgit.handle_command_line()

    @fudge.patch('forgit.subprocess.check_output',
        'forgit.delete_branches')
    def test_prune_contained_by_intersection(self, fake_p, fake_d):
        """
        Verify nothing is merged with passed branch,
        therefore nothing is pruned.
        """
        # first call is to get branch commit
        # 2nd call is to find branches containing the commit
        fake_p.expects_call().returns(
            '* master 123456 0.0.1 some feature commit message'
        ).next_call().returns(
            '* master\n'\
            ' stage\n'\
            ' feature_branch\n'\
            ' feature_two_branch\n'\
            ' feature_three_branch\n'
        ).next_call().returns(
            ' stage 654321 0.0.1 some feature commit message'
        ).next_call().returns(
            '* master\n'\
            ' stage\n'\
            ' feature_branch\n'\
            ' feature_two_branch\n'\
            ' feature_four_branch\n'
        )

        fake_d.expects_call().with_args(set(['feature_branch', 'feature_two_branch']))
        sys.argv = ['forgit', 'contained-by', 'master', 'stage']
        forgit.handle_command_line()
