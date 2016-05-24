#!/usr/bin/python

class   rewriteFile:
        import os 
        import sys
        global steps, tab

        def __init__(self,filename,tab):
            self.f = filename
            self.tab="	"
            self.tab=tab
            self.steps=60
            self.interval=3

        def rewrite(self):
            #steps=60
            #tab="	"
            L = list()
            i=0
            f = open(self.f+".csv", 'r+')
            for line in f.readlines():
                 i=i+1
                 line=line.strip().replace(";",self.tab)
                 print i, line
                 if len(line):
                   L.append(line)#[line.index(self.tab):].lstrip())
                 if i == self.steps:
                     break
            f.close()

            fi = open(self.f+"1.csv", 'w')
            k=0
            l=len(L)
            i=0
            for line in xrange(len(L)):
                    i+=1 
                    k=self.interval*(line)
                    strl=str(k)+self.tab+L[l-i]+"\r"
                    print strl
                    fi.write(strl)
            fi.close()

if __name__ == '__main__':
     x= rewriteFile("DHT","	")
     x.rewrite()