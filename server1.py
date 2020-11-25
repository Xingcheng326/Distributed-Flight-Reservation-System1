# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 17:25:37 2019
@author: dingj
"""

import threading
import json
import socket
import sys
import os 
import pickle
from reservation import Event 
#container = sys.argv[1]


def hasRec(T,eR,i,j):
    return T[i][j] >= eR


## insert a event
def insert(client,flights):
    global C,T
    C += 1
    T[site_id][site_id] = C
    e = Event(C,client,site_id,'insert')
    e.flights =[int(f) for f in flights.split(',')]
    partial_log.append(e)
    e.flights.append(99)
    reservation_dic[client] = e.flights 
    return 

def delete(client,flights):
    global C,T
    C += 1
    T[site_id][site_id] = C
    e = Event(C,client,site_id,'delete')
    e.flights = flights
    partial_log.append(e)
    reservation_dic.pop(client)
    return 
    
 
    
def convert_matrix(T):
    temp = ''
    for i in range(len(T)):
        for j in range(len(T)):
            temp += str(T[i][j])
            temp += ','
    return temp[:-1]

def str_to_matrix(string):
    matrix = [[0 for i in range(ID )] for i in range(ID )]
    
    string = string.split(',')
    count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] = int(string[count])
            count += 1
    return matrix
    

def send(sent_to):
    sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
    for eR in partial_log:
        if not(hasRec(T,eR.time,site_id,id_dic[sent_to])):
            sendmsg = sendmsg + eR.convert_to_string() + "!"
    send_msg(sock,knownhosts,sent_to,sendmsg)
    return

def send_msg(sock,knownhosts,site,msg):
    msg = pickle.dumps(msg)
    IP_address = knownhosts['hosts'][site]['ip_address'] 
    Port = int(knownhosts['hosts'][site]['udp_start_port'])
    sock.sendto(msg, (IP_address, Port))
    
def send_all(sock,knownhosts,msg):
    msg = pickle.dumps(msg)
    
    
    for host in knownhosts['hosts']:
        if host == container:
            continue
        IP_address = knownhosts['hosts'][host]['ip_address'] 
        Port = int(knownhosts['hosts'][host]['udp_start_port'])
        sock.sendto(msg, (IP_address, Port))
        


def confirm_pl(partial_log):
    global C,T, reservation_dic, site_id  
    for eR in partial_log:
        know_eR = True
        for i in range(len(T)):
            if not(hasRec(T,eR.time,site_id,i)):
                know_eR = False
                break
        if know_eR and eR.operation == "insert" :#--------这里就说明所有人都知道eR，所以开始confirm eR
            list_relate_e = {}
            number_confirmed = 0;
            min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            sec_min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            for key, value in reservation_dic.items():#--------这里我要检查所有的dict里面的pair。看看跟eR一样航班的所有pair
                #print(key,'corresponds to',value)
                if value == eR.flights:      #--------这里要双向遍历，就是value可能是1,2，而eR。flight可能是2,3.这个东西我后面写个方程单独干这个事
                    list_relate_e[key] = value
                    if value[-1] == 99:
                        if key < min_client:
                            sec_min_client = min_client
                            min_client = key
                    elif value[-1] == 100:
                        number_confirmed=number_confirmed+1
                    else:
                        print("Something is wrong")


            if number_confirmed <2 and eR.client == min_client:    #------------这里其实只有有一个位置可以confirm eR就可以了。不用管其他。没位置就cancel eR
            #--------------暂时到这，想想是不是confirm 事件 e 的时候，可以confirm dd
            #------------答案是，如果eR是最小的client，就confirm eR，如果eR不是最小的client，就cancel eR
                C += 1
                T[site_id][site_id] = C
                e = Event(C,eR.client,eR.site_id,'confirm')
                e.flights = eR.flights

                partial_log.append(e)
                reservation_dic[eR.client] = e.flights  
                reservation_dic[eR.client][-1] =100                 

            else:

                delete(eR.client,eR.flights)







def receive(receivemsg):
    global C,T, partial_log, reservation_dic, site_id  
    msg1 = receivemsg.split('$$')
    site_id_j = int(msg1[0])
    T_receive = str_to_matrix(msg1[1])
    
    msg2 = msg1[2].split('!')
    
    NP=[]
    for event_str in msg2:
        if event_str != '':
            eR = Event()
            eR.construct_from_string(event_str)
            NP.append(eR)
     
    NE = []
    for fR in NP:
        if not(hasRec(T,fR.time,site_id,site_id)):       #这里全是site_id，因为自己发现不知道
            NE.append(fR)
            
    
   
    for dR in NE:
        if dR.operation == "insert":
            found_delete = False
            for sR in NE:
                if sR.client == dR.client and sR.operation == "delete":
                    found_delete = True
                    break
            if not(found_delete):
                reservation_dic[dR.client] = dR.flights ##这里给reservation_dic这个dictionary添加一个pair
        
        if dR.operation == "confirm":

            for key, value in reservation_dic.items():#--------这里我要检查所有的dict里面的pair。看看跟eR一样航班的所有pair
                #print key,'corresponds to',value
                if value == dR.flights and key == dR.client: 
                    reservation_dic[dR.client][-1] = 100
                    break



    
    for i in range(len(T)):
        T[site_id][i] = max(T[site_id][i], T_receive[site_id_j][i])
    
    
    for i in range(len(T)):
        for j in range(len(T)):
            T[i][j] = max(T[i][j], T_receive[i][j])

   
    
    partial_log.extend(NE)


    confirm_pl(partial_log);
    
    for eR in partial_log:
        know_eR = True
        for i in range(len(T)):
            if not(hasRec(T,eR.time,site_id,i)):
                know_eR = False
                break
        if know_eR:
            
            partial_log.remove(eR)        
    return








        



def recv_msg(sock):
    global T
    while True:
        try:
            data,addr = sock.recvfrom(4096)
            data = pickle.loads(data)
            
            receive(data)
            print(T)
            
        
        except:
            pass
    
    
site_id = int(sys.argv[1])
inputfile = open('knownhosts.json','r')
knownhosts = json.load(inputfile)
reservation_dic = {} ## dictionary to keep the local event
partial_log = []
flight_info = [2 for i in range(20)] ## the local list to store the remaining seats of the flight
T = [[0 for i in range(2)] for i in range(2)]

## determine the site ID
ID = 0
id_dic = {}
for host in knownhosts['hosts']:
    if ID == site_id:
        container = host
    id_dic[host] = ID
    ID += 1

print(id_dic)

##local clock
C = 0 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
UDP_address = knownhosts['hosts'][container]['ip_address'] 
UDP_PORT = int(knownhosts['hosts'][container]['udp_start_port'])
sock.bind((UDP_address, UDP_PORT))

t1 = threading.Thread(target=recv_msg,args=(sock,)).start()
while True:
    msg = input()
    if msg == 'test':
        print(T)
    if msg == 'Q':
        break
    elif msg.startswith('reserve'):
        can_reserve = True
        msg = msg.split(' ')
        for f in msg[2].split(','):
            if flight_info[int(f)] == 0:
                can_reserve = False
                
        if can_reserve:
            insert(msg[1],msg[2])
            print(reservation_dic,C)
        
    elif msg.startswith('send'):
        sent_to = msg.split(' ')[1]
        send(sent_to)
       # send_msg(sock,knownhosts,sent_to,msg)
       
    elif msg.startswith('cancel'):
        client = msg.split(' ')[1]
        if client in reservation_dic:
            delete(client,reservation_dic[client])
            print('Reservation for',client,'cancelled.')
        else:
            print('The client has no reservation.')
        
    elif msg.startswith('view'):
        for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
            print(client,flights)
    
        
        
    elif msg.startswith('sendall'):
        
        send_all(sock,knownhosts,msg)
    

sock.close()
os._exit(1)