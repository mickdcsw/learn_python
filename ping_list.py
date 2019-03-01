import multiprocessing
import subprocess
import os

list1 = []
place = 0

with open('/home/mick/Scripts/list.txt',"r") as filehandle:
    for line in filehandle:
        currentPlace = line[:-1]

        list1.append(currentPlace)

listsize = len(list1)

def pinger( job_q, results_q ):
    DEVNULL = open(os.devnull,'w')
    while True:
        ip = job_q.get()
        if ip is None: break

        try:
            subprocess.check_call(['ping','-c1',ip],
                                  stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass

if __name__ == '__main__':

    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [ multiprocessing.Process(target=pinger, args=(jobs,results))
             for i in range(listsize) ]

    for p in pool:
        p.start()

    for i in range(listsize):
        hostx = list1[place]
#        print(hostx)
        place = place + 1
        jobs.put(hostx)

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    while not results.empty():
        ip = results.get()
        print(ip)
