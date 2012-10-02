import os
import subprocess
import re
import sys

def git_diff(path):
    return subprocess.Popen(['git','diff', path],\
        stdout=subprocess.PIPE).communicate()[0]

def git_checkout(path):
    subprocess.call(['git','checkout', path])

def mode(repo_path=None):
    if not repo_path:
        # default to script execution location
        repo_path = os.getcwd()
    print 'path is {}'.format(repo_path)
    for path, dirs, files in os.walk(repo_path):
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
            if tmp.startswith(repo_path):
                tmp = tmp[len(repo_path)+1:]

            gitout = git_diff(tmp)

            re_filemode = re.compile('^diff --git a/{0} b/{0}\nold mode \d+\nnew mode \d+\n$'.format(tmp))
            if re_filemode.match(gitout):
                git_checkout(tmp)

def handle_command_line():
    if len(sys.argv) == 1:
        # need to add help message.
        print 'Help'
        return

    command = globals().get(sys.argv[1], None)
    args = sys.argv[2:]

    if not command:
        print('Unrecognized command')
        return

    assert callable(command), '{} is not a callable'.format(command)
    command(*args)
