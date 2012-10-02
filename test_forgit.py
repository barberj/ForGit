from unittest import TestCase
import forgit
import sys
import fudge

_exit = sys.exit

class TestForGit(TestCase):

    @fudge.patch('forgit.os.walk', 'forgit.git_diff', 'forgit.git_checkout')
    def test_mode_fully_qualified_path(self, fake_walk, fake_diff, fake_checkout):
        fake_gen = fake_walk.expects_call().with_args('/somepath/somerepo').returns_fake()
        fake_gen.provides('__iter__').expects_call()
        fake_gen.provides('next').expects_call().returns(
                ('/somepath/somerepo', [], ['.git', 'somemodule.py', 'somemodule.pyc'])
            ).next_call().with_args('/somepath/somerepo/somemodule').returns(
                ('/somepath/somerepo/somemodule', [], ['.git', 'somemodule.py', 'somemodule.pyc'])
            )

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
