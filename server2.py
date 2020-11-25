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
    return T[i][j] >= eR.time       #site i 以为 site j 是不是知道


## insert a event
def insert(client,flights):

    global C,T
    C += 1
    T[site_id][site_id] = C
    e = Event(C,client,site_id,'insert')
    e.flights =[int(f) for f in flights.split(',')]

    e.flights.append(site_id)
    e.flights.append(99)    
    partial_log.append(e)    
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
        if not(hasRec(T,eR,id_dic[sent_to],site_id)):      #这里肯定有问题
            sendmsg = sendmsg + eR.convert_to_string() + "!"
    # print("Do I send c?????????")
    # print(sendmsg)
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
        
def confirm_pl(partial_log, reservation_dic):
    global C,T, site_id 

    # print("Now confirm_pl begins===========, check first")
    # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
    #     print(client,end = ' ') 
    #     print (','.join([str(f) for f in reservation_dic[client]]))

    # for log in partial_log:
    #     print(log.operation,log.client,end = ' ')
    #     print (','.join([str(f) for f in log.flights]))

    for eR in sorted(partial_log,key = lambda x:x.client):
        know_eR = True
        for i in range(len(T)):
            if not(hasRec(T,eR,i,eR.site_id)):#看完动画改这个，我觉得是这个的问题，整个site——id列都知道这个事情了，才能confirm。
                know_eR = False
                break
        if not(know_eR):
            # print("other process don't know " + eR.client+ eR.operation)
            continue

        if know_eR and eR.operation == "insert" and eR.site_id == site_id :#--------这里就说明所有人都知道eR，所以开始confirm eR

            found_delete = False
            for sR in partial_log:
                if sR.client == eR.client and sR.operation == "delete":
                    found_delete = True
                    break
            if found_delete:
                continue

            found_confirm = False
            for mR in partial_log:
                if mR.client == eR.client and mR.operation == "confirm":
                    found_confirm = True
                    break
            if found_confirm:
                reservation_dic[eR.client][-1] =100
                print("-----------------------------wei sha jin bulai?????")
                for index in range(len(reservation_dic[eR.client][-1])-2):
                    print("-----------------------------wei sha jin bulai?????")                    
                    flight_info[reservation_dic[eR.client][index]]  = flight_info[reservation_dic[eR.client][index]] -1
                continue



            list_relate_e = {}
            number_confirmed = 0;
            min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            sec_min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"

            # print("----------------I check for "+ eR.client)
            # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
            #     print(client,end = ' ') 
            #     print (','.join([str(f) for f in reservation_dic[client]]))  


            for key, value in reservation_dic.items():#--------这里我要检查所有的dict里面的pair。看看跟eR一样航班的所有pair
                # print(number_confirmed)
                value_copy = value.copy()
                save = eR.flights.copy() 
                value_copy.pop()
                value_copy.pop()
                save.pop()
                save.pop()                              



                if value_copy == save:      #--------这里要双向遍历，就是value可能是1,2，而eR。flight可能是2,3.这个东西我后面写个方程单独干这个事
                    list_relate_e[key] = value
                    # print("the key is " + key)
                    # print("\nthe value is ")
                    # print(value)

                    if value[-1] == 99:
                        # print("I am get the min client and confirm number:")
                        # print(key+"<<<<<<<<")
                        # print(min_client)                        
                        if key < min_client and value[-2] == eR.site_id:
                            sec_min_client = min_client
                            min_client = key
                            # print("I change min_client into "+ key)
                        elif key < min_client and value[-2] != eR.site_id:
                            number_confirmed=number_confirmed+1

                    elif value[-1] == 100:
                        number_confirmed=number_confirmed+1
                        # print("number_confirmed=number_confirmed+1"+ str(number_confirmed))
                    else:
                        print("Something is wrong")
            # print("------------the min client is"+min_client)
            # print("the confirm number is"+str(number_confirmed))



            if number_confirmed <2 and eR.client == min_client:    #------------这里其实只有有一个位置可以confirm eR就可以了。不用管其他。没位置就cancel eR
            #--------------暂时到这，想想是不是confirm 事件 e 的时候，可以confirm dd
            #------------答案是，如果eR是最小的client，就confirm eR，如果eR不是最小的client，就cancel eR
                # print("I am here to confirm")
                # print(eR.client)
                # print("-------------")
                # print(number_confirmed)                
                C += 1
                T[site_id][site_id] = C
                e = Event(C,eR.client,eR.site_id,'confirm')
                e.flights = eR.flights

                partial_log.append(e)
                reservation_dic[eR.client] = e.flights  
                reservation_dic[eR.client][-1] =100 
                # print("-------------After I change "+ eR.client)
                # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
                #     print(client,end = ' ') 
                #     print (','.join([str(f) for f in reservation_dic[client]]))                                

            else:
                # print("I delete "+ eR.client )
                delete(eR.client,eR.flights)

            # print("every time I change,I check first, to find where I lost the insert d")
            # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
            #     print(client,end = ' ') 
            #     print (','.join([str(f) for f in reservation_dic[client]]))

            # for log in partial_log:
            #     print(log.operation,log.client,end = ' ')
            #     print (','.join([str(f) for f in log.flights]))


def receive(receivemsg):
    # print("Do I receive c")
    # print(receivemsg)
    global C,T, partial_log, reservation_dic, site_id  
    msg1 = receivemsg.split('$$')
    site_id_j = int(msg1[0])
    # print("what become T-----------")
    # print(msg1[1])
    T_receive = str_to_matrix(msg1[1])

    # print("what become PL-----------")
    # print(msg1[2])    
    msg2 = msg1[2].split('!')
 
    # print("what become PL-----------")
    # print(msg2)

    NP=[]
    for event_str in msg2:
        if event_str != '':
            eR = Event()
            eR.construct_from_string(event_str)
            NP.append(eR)
    # print("what is in NP")
    # print(NP)     
    NE = []
    for fR in NP:
        if not(hasRec(T,fR,site_id,fR.site_id)):       #这里全是site_id，因为自己发现不知道
            NE.append(fR)
            
    # print("what is in NE")
    # print(NE)     
   
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
                value_copy = value.copy()
                save = dR.flights.copy() 
                value_copy.pop()
                value_copy.pop()
                save.pop()
                save.pop() 

                if value_copy == save and key == dR.client: 
                    reservation_dic[dR.client][-1] = 100
                    print("-----------------------------wei sha jin bulai?????")
                    for index in range(len(reservation_dic[dR.client][-1])-2):  
                        print("-----------------------------wo lai le me??????????????")
                        print(reservation_dic[dR.client][index])

                        print(flight_info[reservation_dic[dR.client][index]])
                        flight_info[reservation_dic[dR.client][index]]  = flight_info[reservation_dic[dR.client][index]] -1




                    break    

        if dR.operation == "delete":

            for key, value in reservation_dic.items():#--------这里我要检查所有的dict里面的pair。看看跟eR一样航班的所有pair
                #print key,'corresponds to',value
                value_copy = value.copy()
                save = dR.flights.copy() 
                value_copy.pop()
                value_copy.pop()
                save.pop()
                save.pop() 
                
                if value_copy == save and key == dR.client: 
                    reservation_dic.pop(dR.client)
                    break 


    
    for i in range(len(T)):
        T[site_id][i] = max(T[site_id][i], T_receive[site_id_j][i])
    
    
    for i in range(len(T)):
        for j in range(len(T)):
            T[i][j] = max(T[i][j], T_receive[i][j])

   
    
    partial_log.extend(NE)
    # print("Now I plan to confirm_pl, check first")
    # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
    #     print(client,end = ' ') 
    #     print (','.join([str(f) for f in reservation_dic[client]]))

    # for log in partial_log:
    #     print(log.operation,log.client,end = ' ')
    #     print (','.join([str(f) for f in log.flights]))



    confirm_pl(partial_log, reservation_dic);



    temp = []
    for eR in partial_log:
        
        know_eR = True
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@I checking "+ eR.client +eR.operation)
        for i in range(len(T)):
            # print(str(eR.time) + " vs "+str(T[i][site_id]))
            if not(hasRec(T,eR,i,site_id)):
                know_eR = False
                break
        if not(know_eR):
            temp.append(eR)
            # print("I deleting "+ eR.client +eR.operation)

            


    partial_log = temp.copy()
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
    
 
container = sys.argv[1]
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
    id_dic[host] = ID
    ID += 1
site_id = id_dic[container]


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
            print('Reservation submitted for '+msg[1]+'.')
        
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
            print(client,end = ' ') 
            print (','.join([str(f) for f in reservation_dic[client]]))
           
            
    elif msg.startswith('log'):
        for log in partial_log:
            print(log.operation,log.client,end = ' ')
            print (','.join([str(f) for f in log.flights]))
    
        
    elif msg.startswith('T'):
        sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
        print(sendmsg)

    elif msg.startswith('flight_info'):

        print(flight_info)

    elif msg.startswith('sendall'):
        
        send_all(sock,knownhosts,msg)
    

sock.close()
os._exit(1)
