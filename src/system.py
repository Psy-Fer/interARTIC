from .queue import JobsQueue
from .job import Job

class System:
    def __init__(self, queue_size):
        self._queue = JobsQueue(queue_size)
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

    def newJob(self, job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data,num_samples):
        return Job(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data,num_samples)

    def getJobByName(self, job_name):
        #Returns a job with the given name, or None if no match
        return self._queue.getJobByName(job_name)

    def addJob(self, job):
        self._queue.putJob(job)
        #if not self._current_job:
            # No job is being run, so run the newly added job
            #self.executeNextJob()
        print("IN SYS")
        #job.execute()

    def executeNextJob(self):
        self._queue.executeNextJob()
        #self._current_job = job
        #print("Cur Job: ", self._current_job.job_name)

    def removeJob(self, job_name):
        self._queue.removeJob(job_name)

    def checkForExecution(self):
        while self._current_job == None:
            if self.queue.getJob():
                self._current_job = self.queue.getJob()
                print("current job set to: ", self._current_job.job_name)
                self._current_job.execute()
                self._current_job = None
                #####??????????