"""
ForGit

Usage:
    forgit mode [<repo_path>]
    forgit contained-by [<branch>...]

Options:
    -h, --help
    -v, --version
    <path>              Path of repository to reset filemode changes.
    <branch>            Branch(es) to verify contained-by. [default: master]
"""
import os
import subprocess
import re
from docopt import docopt


def git_diff(path):
    return subprocess.check_output(['git','diff', path])


def git_checkout(path):
    return subprocess.check_call(['git','checkout', path])


def mode(repo_path=None, **kw):
    if not repo_path:
        # default to script execution location
        repo_path = os.getcwd()

    for path, dirs, files in os.walk(repo_path):

        if path.startswith('.git') or path.endswith('.git'):
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


def contained_by(**kw):
    pass


def normalize(arguments):
    del arguments['--version']
    del arguments['--help']
    command = {}
    options = {}

    """
    If the key of the argument is in the global namespace its a command.
    If the value of that key is True its the command to execute.
    Delete all other commands.

    Normalize options in the arguments dictionary by removing <> and --.
    """
    for k, v in arguments.iteritems():
        cmd = '_'.join(k.split('-'))
        if cmd in globals():
            if v:
                command['command'] = cmd
        else:
            options[k.lstrip('-').\
                lstrip('<').rstrip('>')] = v

    command.update(options)
    return command


def handle_command_line():
    arguments = normalize(docopt(__doc__, version='ForGit 0.0.1'))
    command = globals().get(arguments['command'])

    if not command:
        print('Unrecognized command')

    assert callable(command), '{} is not a callable'.format(command)
    command(**arguments)
