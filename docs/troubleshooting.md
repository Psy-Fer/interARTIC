# Troubleshooting

[TOC]

## Submitted job not running

### Job not running after submission

This may be because there are too many Celery tasks running in the background. To rectify this, enter: 

```
ps aux | grep celery
kill -9 <process ID>    # where process ID is the number in the second column
                        # repeat this until all celery processes have been removed
```

### Usage errors

If a usage error is printing in the progress page, this may mean that a particular command has not been implemented, or the read file you have submitted has not been formatted correctly.

An example of a usage error is:

```
usage: artic [-h] [-v] 
```

To rectify this, first check that the read file you have submitted has been formatted correctly i.e. with no header. More information can be found on the usage page of this documentation.

If this does not fix the issue, please let the developers know via GitHub so that the command can be implemented.

## Missing job on Home Page

If a job is missing from the home page, wait a few seconds and refresh the page.

## bin/python3.7: error while loading shared libraries: libnsl.so.1: cannot open shared object file: No such file or directory

This is likely to happen on Fedora. Install the following package.

`sudo dnf install libnsl`

## Any other errors

If there are any other errors, please let the developers know via GitHub so that we can look into it for you.
