import queue as q

class JobsQueue(q.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)
    
    def getJobByName(self, job_name):
        for job in list(self.queue):
            if job.job_name == job_name:
                return job
        return None
        




