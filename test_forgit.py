from unittest import TestCase
import forgit
import fudge


class TestForGit(TestCase):

    @fudge.patch('forgit.os.walk', 'forgit.git_diff', 'forgit.git_checkout')
    def test_mode_fully_qualified_path(self, fake_walk, fake_diff, fake_checkout):

        def walk():
            index = 0
            paths = [('/somepath/somerepo', [], ['.git', 'somemodule.py', 'somemodule.pyc']),
                ('/somepath/somerepo/somemodule', [], ['.git', 'somemodule.py', 'somemodule.pyc'])]
            while index < len(paths):
                yield paths[index]
                index += 1

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
