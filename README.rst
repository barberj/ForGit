ForGit
======

A set of git convenience command line tools.

forgit
------

forgit mode [path to repository]
    Checkout repository files from index if only change is the filemode.

Due to a hardware malfunction, I had to restore repositories with uncommited
changes onto fresh hardware. After restore all respository files showed a change
in filemode despite my git ignore filemode configuration.

::
    $ git diff setup.py
    diff --git a/setup.py b/setup.py
    old mode 100644
    new mode 100755
