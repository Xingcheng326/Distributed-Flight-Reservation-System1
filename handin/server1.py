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
    
 
    
def convert_matrix_row(T):
    temp = ''
    for i in range(len(T)):
        for j in range(len(T)):
            temp += str(T[i][j])
            temp += ','
    return temp[:-1]
    
def convert_matrix(T):
    temp = ''
    for i in range(len(T)):
        for j in range(len(T)):
            temp += str(T[i][j])
            temp += ','
    return temp[:-1]

def str_to_matrix_row(string,row):
	matrix = [[0 for i in range(ID )] for i in range(ID )]
	string = string.split(',')
	count = 0
	for i in range(len(matrix)):
		matrix[row][i] = int(string[count])
		count += 1
	return matrix
	
def str_to_matrix(string):
    matrix = [[0 for i in range(ID )] for i in range(ID )]
    
    string = string.split(',')
    count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] = int(string[count])
            count += 1
    return matrix

def small_send(sent_to):
	sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
	for eR in partial_log:
		if not(hasRec(T,eR,id_dic[sent_to],site_id)):     
			sendmsg = sendmsg + eR.convert_to_string() + "!"
	sendmsg = sendmsg + "$$" + '1'
	send_msg(sock,knownhosts,sent_to,sendmsg)
	return
    


def send_msg(sock,knownhosts,site,msg):
    msg = pickle.dumps(msg)
    
    IP_address = knownhosts['hosts'][site]['ip_address'] 
    Port = int(knownhosts['hosts'][site]['udp_start_port'])
    sock.sendto(msg, (IP_address, Port))

def send(sent_to):
    sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
    for eR in partial_log:
        if not(hasRec(T,eR,id_dic[sent_to],site_id)):      
            sendmsg = sendmsg + eR.convert_to_string() + "!"
    sendmsg = sendmsg + "$$" + '0'
    send_msg(sock,knownhosts,sent_to,sendmsg)
    return
  
def send_all(sock,knownhosts):
    
    
    
    for host in knownhosts['hosts']:
        if host == container:
            
            continue
        sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
        
        for eR in partial_log:
            
            if not(hasRec(T,eR,id_dic[host],site_id)):     
                sendmsg = sendmsg + eR.convert_to_string() + "!"
        
        sendmsg = sendmsg + "$$" + '0'
        
       
        send_msg(sock,knownhosts,host,sendmsg)
        
        
def confirm_pl(partial_log, reservation_dic):
    global C,T, site_id 

    for eR in sorted(partial_log,key = lambda x:x.client):
        know_eR = True
        for i in range(len(T)):
            if not(hasRec(T,eR,i,eR.site_id)):
                know_eR = False
                break
        if not(know_eR):
            # print("other process don't know " + eR.client+ eR.operation)
            continue

        if know_eR and eR.operation == "insert" and eR.site_id == site_id :

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
                continue



            list_relate_e = {}
            number_confirmed = 0;
            min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            sec_min_client = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"

            # print("----------------I check for "+ eR.client)
            # for client,flights in sorted(reservation_dic.items(),key = lambda x:x[0]):
            #     print(client,end = ' ') 
            #     print (','.join([str(f) for f in reservation_dic[client]]))  


            for key, value in reservation_dic.items():
                # print(number_confirmed)
                value_copy = value.copy()
                save = eR.flights.copy() 
                value_copy.pop()
                value_copy.pop()
                save.pop()
                save.pop()                              



                if value_copy == save:     
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



            if number_confirmed <2 and eR.client == min_client:   
            
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



def receive(receivemsg):
    
    global C,T, partial_log, reservation_dic, site_id  
    msg1 = receivemsg.split('$$')
    site_id_j = int(msg1[0])
    
    if msg1[-1] == '0':
        T_receive = str_to_matrix(msg1[1])
    else:
        T_receive = str_to_matrix_row(msg1[1],site_id_j)

  
    msg2 = msg1[2].split('!')
 
    # print("what become PL-----------")
    # print(msg2)

    NP=[]
    for event_str in msg2:
        if event_str != '':
            eR = Event()
            eR.construct_from_string(event_str)
            NP.append(eR)
    
    NE = []
    for fR in NP:
        if not(hasRec(T,fR,site_id,fR.site_id)):       
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

            for key, value in reservation_dic.items():#--------
                #print key,'corresponds to',value
                value_copy = value.copy()
                save = dR.flights.copy() 
                value_copy.pop()
                value_copy.pop()
                save.pop()
                save.pop() 

                if value_copy == save and key == dR.client: 
                    reservation_dic[dR.client][-1] = 100
                    break    

        if dR.operation == "delete":

            for key, value in reservation_dic.items():#--------
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
            
        
        except:
            pass
    
    
container = sys.argv[1]
inputfile = open('knownhosts.json','r')
knownhosts = json.load(inputfile)
reservation_dic = {} ## dictionary to keep the local event
partial_log = []
flight_info = [2 for i in range(20)] ## the local list to store the remaining seats of the flight

clientset = set()

## determine the site ID
ID = 0
id_dic = {}
for host in knownhosts['hosts']:
    id_dic[host] = ID
    ID += 1
site_id = id_dic[container]

T = [[0 for i in range(ID)] for i in range(ID)]

##local clock
C = 0 


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
UDP_address = knownhosts['hosts'][container]['ip_address'] 
UDP_PORT = int(knownhosts['hosts'][container]['udp_start_port'])
sock.bind((UDP_address, UDP_PORT))

t1 = threading.Thread(target=recv_msg,args=(sock,)).start()
while True:
    try:
        msg = input()
        
        if msg == 'quit':
            break
        elif msg.startswith('reserve'):
            can_reserve = True
            msg = msg.split(' ')
            if len(msg) >= 3:
                for f in msg[2].split(','):
                    if flight_info[int(f)] == 0:
                        can_reserve = False
                if msg[1] in clientset:
                    print('This client has reserved before.')
                    can_reserve = False
                    
                if can_reserve:
                    clientset.add(msg[1])
                    insert(msg[1],msg[2])
                    print('Reservation submitted for '+msg[1]+'.')
            else:
                print('Invalid commands')
        elif msg.startswith('sendall'):
            
            send_all(sock,knownhosts)  
            
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
                print (','.join([str(f) for f in reservation_dic[client][:-2]]),end=' ')
                if reservation_dic[client][-1] == 99:
                    print('pending')
                else:
                    print('confirmed')
               
                
        elif msg.startswith('log'):
            for log in partial_log:
                print(log.operation,log.client,end = ' ')
                if log.operation != 'delete':
                    print (','.join([str(f) for f in log.flights[:-2]]))
                else:
                    print('')
        
            
        elif msg.startswith('T'):
            sendmsg = str(site_id)+"$$" + convert_matrix(T) + "$$"
            print(sendmsg)
            
        elif msg.startswith('clock'):
            for row in T:
                print(' '.join([str(i) for i in row]))
    
    
    
        
    except:
        pass
    

sock.close()
os._exit(1)
