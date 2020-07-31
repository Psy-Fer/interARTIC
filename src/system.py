from .queue import JobsQueue
from .job import Job

class System:
    def __init__(self, queue_size):
        self._queue = JobsQueue(queue_size)
        self._jobs = []
        self._current_job = None
        self._completed = []

    @property
    def queue(self):
        return self._queue

    @property
    def current_job(self):
        return self._current_job

    @property
    def completed(self):
        return self._completed

    def newJob(self, job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data,num_samples, barcode_type):
        return Job(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples, barcode_type)

    def getJobByName(self, job_name):
        #Returns a job with the given name, or None if no match
        return self._queue.getJobByName(job_name)

    # def getJobByName(self, job_name):
    #     #Returns a job with the given name, or None if no match
    #     for job in self._jobs:
    #         if job.job_name == job_name:
    #             return job
    #     return None

    def addJob(self, job):
        self._queue.putJob(job)
        #if not self._current_job:
            # No job is being run, so run the newly added job
            #self.executeNextJob()
        print("IN SYS")
        #job.execute()

    # def addJob(self, job):
    #     self._jobs.append(job)
    #     #if not self._current_job:
    #         # No job is being run, so run the newly added job
    #         #self.executeNextJob()
    #     print("IN SYS")
    #     #job.execute()

    def printQueue(self):
        jobList =[]
        if not self._queue.getItems():
            print("LIST IS EMPTY")
        for job in self._queue.getItems():
            jobList.append(job.job_name)
        return jobList

    # def printQueue(self):
    #     jobList =[]
    #     for job in self._jobs:
    #         jobList.append(job.job_name)
    #     return jobList

    def executeNextJob(self):
        self._queue.executeNextJob()
        #self._current_job = job
        #print("Cur Job: ", self._current_job.job_name)

    def removeQueuedJob(self, job_name):
        self._queue.removeJob(job_name)

    def moveJobToComplete(self, job_name):
        self.removeQueuedJob(job_name)
        job = self.getJobByName(job_name)
        self._completed.append(job)

    def checkForExecution(self): #??????
        while self._current_job == None:
            if self.queue.getJob():
                self._current_job = self.queue.getJob()
                print("current job set to: ", self._current_job.job_name)
                self._current_job.execute()
                self._current_job = None
                #####??????????