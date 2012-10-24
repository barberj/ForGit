"""
ForGit

Usage:
    forgit (mode <repo_path>|(merged [--with=<branch>...]))

Options:
    -h, --help
    -v, --version
    <path>                           Path of repository to ignore filemode changes. [default: None]
    -w <branch>, --with=<branch>     Specify branch to verify merged. [default: master]
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


def merged(**kw):
    pass


def clean(arguments):
    del arguments['--version']
    del arguments['--help']
    command = {}
    options = {}

    """
    If the key of the argument is in the global namespace its a command.
    If the value of that key is True its the command to execute.
    Delete all other commands.

    Clean up options in the arguments dictionary by removing <> and --.
    """
    for k, v in arguments.iteritems():
        if k in globals():
            if v:
                command['command'] = k
        else:
            options[k.lstrip('-').\
                lstrip('<').rstrip('>')] = v

    command.update(options)
    return command


def handle_command_line():
    arguments = clean(docopt(__doc__, version='ForGit 1.0'))
    command = globals().get(arguments['command'])

    if not command:
        print('Unrecognized command')

    assert callable(command), '{} is not a callable'.format(command)
    command(**arguments)
