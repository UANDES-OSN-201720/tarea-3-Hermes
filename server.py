# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:41:43 2017

@author: Nicolàs
"""

import socket
import time

#Funcion para conseguir ip lan.
def lanip():
    aux = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    aux.connect(("8.8.8.8", 80))
    ipadd =(aux.getsockname()[0])
    aux.close()
    return ipadd

#Lista con clientes.
clients = []
groups=[]

#Se imprime el ip lan para que los clientes puedan conectarse.
print lanip()

#Se usa host 0.0.0.0 para escuchar localhost y la direccion ip lan al mismo tiempo.
host = '0.0.0.0'
port = 5000

#Se crea socket.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host,port))
s.setblocking(0)

#Variable para terminar el thread.
quitting = False
print "Server Started."
while not quitting:
    try:
        data2, addr = s.recvfrom(1024)
        data = data2.split('/%')
        print data #debug
        #Conexion de cliente.
        if int(data[0])==0:
            included=False
            if len(clients)>0:
                for c in clients:
                    if data[1] == c[0]:
                        included=True
                        if addr!=c[1]:
                            c[1]=addr #Si cliente ya existe, pero tiene direccion diferente, se actualiza.
            if not included: #Si el cliente es nuevo, se registra.
                clients.append([data[1],addr])
            s.sendto(data2, addr)
         
        elif int(data[0])==1:
            print "mensaje"
            for c in clients:
                if c[0]==data[2]:
                    s.sendto(data2, c[1])
        elif int(data[0])==2:
            print 'crear grupo'
            gr=[data[1],data[2].split(',')]
            groups.append(gr)
        elif int(data[0])==3:
            print 'mensaje a grupo'
            exist = False
            for g in groups:
                if data[2]==g[0]:
                    exist = True
                    for c in clients:
                        if c[0] in g[1] and c[0]!=data[1]:
                            s.sendto(data2, c[1])
            if not exist:
                for c in clients:
                        if c[0] ==data[1]:
                            s.sendto("3/%Server/%"+data[2]+"/%ya no existe el grupo.", c[1])
        elif int(data[0])==4:
            print 'eliminar grupo'
            cont=0
            incl=False
            for i in groups:
                if i[0]==data[1]:
                    incl = True
                    break
                cont+=1
            if incl:
                groups.pop(cont)
        elif int(data[0])==5:
            print 'archivo'
            for c in clients:
                if c[0]==data[2]:
                    s.sendto(data2, c[1])
                    l, addr = s.recvfrom(1024)
                    while (l):
                        s.sendto(l, c[1])
                        l, addr = s.recvfrom(1024)
                        if l == "close":
                            break
                    s.sendto("close", c[1])
        else:
            print "error"

    except:
        time.sleep(0.2)
s.close()
