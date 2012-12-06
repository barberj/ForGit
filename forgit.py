"""
forgit

Usage:
    forgit mode [<repo_path>]
    forgit contained-by [<branches>...] [-c <config>]

Options:
    -h, --help
    -v, --version
    -c <config>, --config <config>    forgit resource configuration file. [default: .forgitrc]
    <path>                          Path of repository to reset filemode changes.
    <branches>                      Branches to verify contained-by. [default: master]
"""
import os
import subprocess
import re
import sys
from docopt import docopt
import configit


# this can be overwritten if there is a configuration file
def prune_hook(branch): return True


def git_verbose_branch_listing(branch):
    branch_listing = subprocess.check_output(['git','branch', '--list', '-v', '--no-abbrev', branch])
    if not branch_listing:
        raise SystemExit('Invalid existing branch name.\nUsuage:\n\tforgit contained-by [<branch>...]')
    # if branch to verify contained-by is currently checked out
    # it will include an asterisk in the listing.
    # remove the asterisk so our access by index is correct.
    branch_listing = branch_listing.split()
    if '*' in branch_listing: branch_listing.remove('*')
    return branch_listing


def git_diff(path):
    return subprocess.check_output(['git','diff', path])


def git_checkout(path):
    return subprocess.check_call(['git','checkout', path])


def git_merged(commit):
    branches = subprocess.check_output(['git','branch','--merged', commit]).split()
    # remove the * which denotes current branch
    if '*' in branches: branches.remove('*')
    return branches


def git_prune(branch):
    if prune_hook(branch):
        print 'Pruning branch {}'.format(branch)
        #subprocess.check_call(['git', 'branch', '-d', branch])
        #subprocess.check_call(['git', 'push', 'origin', ':{}'.format(branch)])


def delete_branches(branches):
    for branch in branches:
        git_prune(branch)


def mode(repo_path=None, **kw):
    """
    Forget all filemode changes.
    """

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
    """
    Forget all topic branches contained by branches argument.

    In reality this is the inverse of no-merged.
    """

    branches = kw.get('branches')
    if not branches:
        raise SystemExit('Missing the name of an existing branch to find branches '
            'which are not fully contained.\nUsuage:\n\tforgit contained-by [<branch>...]')

    # gather branches contained by commit
    merged = {}
    for branch in branches:
        commit = git_verbose_branch_listing(branch)[1]
        merged[commit] = git_merged(commit)

    # we only want to prune items contained by all the branches.
    # so we need to gather all the merged branches
    # and find the ones common to all.
    prune = set()
    for commit, merged_branches in merged.iteritems():
        # if nothing to prune set current merged branches to be pruned
        if not prune: prune = set(merged_branches)

        # safe to do this regardless of previous conditional
        # b/c it will be intersecting the same set
        prune = prune & set(merged_branches)

    map(prune.discard, branches)
    delete_branches(prune)

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


def load_config(config):
    # default configuration loaded from user home directory
    if config == '.forgitrc':
        config = os.path.expanduser('~/.forgitrc')

    if not os.path.exists(config):
        print('[WARNING] Unable to load configuration file {}'.format(config))
        return
    config = configit.from_file(config)
    globals().update(config)


def handle_command_line():
    arguments = normalize(docopt(__doc__, sys.argv[1:], version='forgit 0.0.1'))
    command = globals().get(arguments['command'])

    if not command:
        print('Unrecognized command')

    config = arguments['config']
    del arguments['config']
    load_config(config)

    assert callable(command), '{} is not a callable'.format(command)
    command(**arguments)
