# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 17:36:21 2019

@author: dingj
"""
## insert and delete algorithm
class Event:
    def __init__(self,time=None,clients=None,site_id=None,operation=None):
        self.time = time
        self.client = clients
        self.status = 'pending'
        self.flights = []
        self.site_id = site_id
        self.operation = operation
      
    ##serielizr the event class
    def convert_to_string(self):
        temp = str(self.time) + '+' + self.client +'+' + str(self.site_id) + '+' + self.operation + '+' 
        for f in self.flights:
            temp += str(f)
            temp += ','
            
        
        return temp[:-1]
    
    def construct_from_string(self,string):
        temp = string.split('+')
        self.time = int(temp[0])
        self.client = temp[1]
        self.site_id = int(temp[2])
        self.operation = temp[3]
        self.flights = [int(flight) for flight in temp[4].split(',')]
        
        