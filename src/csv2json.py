#!/usr/bin/env python
 

import csv
import json
class csv2json:

        global exampleData
        def __init__(self,filename,delimiter):
          self.filename=filename
          self.delimiter=delimiter

        def convert(self):
          #exampleFile = open('DHT.csv','rU')
          #exampleReader = csv.reader(exampleFile,delimiter='	')
          exampleFile = open(self.filename+".csv",'rU')
          exampleReader = csv.reader(exampleFile,delimiter=self.delimiter)
          self.exampleData = list(exampleReader)
          jsonOutput = json.dumps([row for row in self.exampleData])
          data_to_write = '{"aaData": %s}' % jsonOutput
          new_file = open(self.filename+".json", 'w')
          new_file.write(data_to_write)
          new_file.close()


if __name__ == '__main__':
         
          x=csv2json("DHT1","	")
          x.convert()
          print x.exampleData