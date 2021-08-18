# -*- coding: utf-8 -*-
from celery import shared_task
import subprocess
from celery.utils.log import get_task_logger
from celery.app.control import Inspect

logger = get_task_logger(__name__)


#@shared_task(bind=True)
@shared_task()
def executeJob():
    logger.info("In tasks.py, executing job...")
    print("IN TASKS PRINTING JOB: ")
    command = "echo running; sleep 4; echo FINISHING JOB"
    print("IN TASKS")
    po = subprocess.Popen(command, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    print("CHECK 1")
    stdout, stderr = po.communicate()
    #self.update_state(state='PROGRESS')
    print("CHECK 2")
    po.wait()
    print("CHECK 3")

    returnCode = po.returncode
    if returnCode != 0:
        raise Exception("Command {} got return code {}.\nSTDOUT: {}\nSTDERR: {}".format(command, returnCode, stdout, stderr))
    print("JOB CMD {} RETURNED: {}".format(command, returnCode))
    print("CHECK 4")


    # Inspect all nodes.
    #i = Inspect()

    # Show the items that have an ETA or are scheduled for later processing
    # i.scheduled()

    # # Show tasks that are currently active.
    # i.active()

    # # Show tasks that have been claimed by workers
    # i.reserved()
    #return returnCode
