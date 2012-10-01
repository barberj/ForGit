import os
import subprocess
import re
import sys

#__all__ = ["mode"]


def mode(path='.'):
    print 'path is {}'.format(path)
    for path, dirs, files in os.walk(path):
        if path.startswith('.git'):
            continue  # ignore the git config directory
        for _file in files:
            if _file.endswith('pyc'):
                continue  # skip compiled files
            tmp = os.path.join(path, _file)
            '''
            git diff results are from from repo head and do not include
            dot relative paths.

            $ git diff ./scripts/images/image_1.jpg
            diff --git a/scripts/images/image_1.jpg b/scripts/images/image_1.jpg
            old mode 100644
            new mode 100755
            '''
            if tmp.startswith('.'):
                tmp = tmp[2:]  # if you start with the path '.'

            gitout = subprocess.Popen(['git','diff',tmp],\
                stdout=subprocess.PIPE).communicate()[0]

            re_filemode = re.compile('^diff --git a/{0} b/{0}\nold mode \d+\nnew mode \d+\n$'.format(tmp))
            if re_filemode.match(gitout):
                subprocess.call(['git','checkout',tmp])

def handle_command_line():
    if len(sys.argv) == 1:
        # need to add help message.
        print 'HELP'
        sys.exit(0)

    command = globals().get(sys.argv[1], None)
    args = sys.argv[2:]

    if not command:
        print('Unrecognized command')
        sys.exit(0)

    assert callable(command), '{} is not a callable'.format(command)
    command(*args)
