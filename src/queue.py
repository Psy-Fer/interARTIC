#import queue as q

'''class JobsQueue(q.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)
    
    def getJobByName(self, job_name):
        for job in list(self.queue):
            if job.job_name == job_name:
                return job
        return None
        
    def putJob(self, job):
        #Check if queue is empty - if yes, execute job
        if super().empty():
            job.execute()
        #Call to Queue method to add an item
        super().put(job)
        
    def removeJob(self, job_name):
        #Remove a job from the queue
        job = getJobByName(job_name)'''
        
class JobsQueue:
    def __init__(self, maxsize):
        self._maxsize = maxsize
        self._items = []

    def empty(self):
        if not self._items:
            return True
        else:
            return False
            
    def full(self):
        if len(self._items) == self._maxsize:
            return True
        else:
            return False
            
    def getItems(self):
        return self._items

    def getJobByName(self, job_name):
        #Returns a job with the given name, or None if no match
        for job in self._items:
            if job._job_name == job_name:
                return job
        return None
        
    def putJob(self, job):
        #Check if queue is empty - if yes, execute job
        if self.empty():
            self._items.append(job)
            return True
        #Check if queue is currently at size limit
        if not self.full():
            self._items.append(job)
            return True
            
    def getJob(self):
        #Gets next item in queue if queue not empty
        if not self.empty():
            return self._items.pop(0)
        else:
            return None
        
    def removeJob(self, job_name):
        #Remove a job from the queue
        job = getJobByName(job_name)
        for job in self._items:
            if job.job_name == job_name:
                self._items.remove(job)
                
    def getJobNumber(self, job_name):
        num = 1
        for job in self._items:
            if job._job_name == job_name:
                return num
            num = num + 1
        return None
        
    def getNumberInQueue(self):
        return len(self._items)




