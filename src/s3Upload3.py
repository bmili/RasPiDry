#!/usr/bin/python


from boto.s3.key import Key
import os
import time
import rewriteFile
global filesize

class s3Upload:
     """An AWS  s3 upload class"""


     def __init__(self,filename, Bucketname,sleep,lock):
        print "s3Upload init file {}, bucket {}, sleep {}  ".format (filename, Bucketname,sleep)
        self.f = filename
        self.b = Bucketname
        self.sleep=sleep
        self.filesize  = 0 # os.path.getsize(str(self.f)+".csv")
        self.lock=lock
 
     def Fileupload(self,tab):
       from csv2json import csv2json
       while True:
         time.sleep(self.sleep+5)
         b = os.path.getsize(str(self.f)+".csv")
         if b > self.filesize:
           print ("Rewrite File "+str(self.f)+".csv")
           self.filesize= b
           x= rewriteFile.rewriteFile(self.f,tab)
           x.rewrite()
           y=csv2json(self.f+"1",tab)
           y.convert()
           self.Upload()
         


     def Upload(self):
        import boto
        import ssl
        import os
        import sys
        import ssl
        from boto.s3.key import Key
        s3 = boto.connect_s3()
        bucket=s3.get_bucket(self.b, validate=False)
        self.lock.acquire()
        print "s3Upload",(self.f+"1.csv")," to ",bucket
        self.lock.release()

        try:
                 k = Key(bucket)
                 print(k)
                 k.key = self.f+"1.csv"
                 k.content_type = 'text/html'
                 k.set_contents_from_filename(str(self.f)+"1.csv")
                 k.set_acl('public-read')
                 k.key = self.f+"1.json"
                 k.content_type = 'text/html'
                 k.set_contents_from_filename(str(self.f)+"1.json")
                 k.set_acl('public-read')
        except IOError as e:
              print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except SSLError as e:
              print "SSL error({0}): {1}".format(e.errno, e.strerror)
        except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

     
if __name__ == '__main__':
     import time

     from multiprocessing import Process,Lock
     global p
     print "main"
   #     Bucketname = 'razmere.si'
     Bucketname = 'iothome'
     myfile='DHT'
     stop=time.time()
     lock=Lock()
     sleep=20
     try:
        x= s3Upload(myfile,Bucketname,sleep,lock)
        print "size",x.filesize
        p = Process(target=x.Fileupload, args=("	", ))
        p.start()
        time.sleep(sleep)
        p.join() # stop all processes in my group
     except KeyboardInterrupt:
         print ("Interrupt! elapsed time:", (time.time()-stop))
     finally:  
         print ("finaly")
       #  p.terminate()

"""
Bucketname = 'razmere.si'
Bucketname = 'iothome'
myfile='DHT'

x= s3Upload (myfile,Bucketname)
print "size",x.filesize
#x.Upload()
#print x.t
"""
