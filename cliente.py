# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:41:48 2017

@author: Nicolàs
"""

import socket
import threading
import time
import os


#Thread para recibir mensajes.
def receving(name, sock):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        try:
            tLock.acquire() 
            while True:
                data, addr = sock.recvfrom(1024)
                data = data.split('/%')
                msg = data[1] +":"+data[3]
             
                if data[0]=='1':
                    if data[1] not in contactos:
                        contactos.append(data[1])
                        chat = {'name': data[1], 'chat': []}
                        chats.append(chat)
                    for c in chats:
                        if data[1]==c['name']:
                            c['chat'].append(msg)
                elif data[0]=='3':
                    if data[2] not in grupos:
                      
                        grupos.append(data[2])
                        chat={'nombre':data[2],'cont':[], 'ides':[], 'chat':[]}
                        chatsg.append(chat)
                    for cg in chatsg:
                        if data[2]==cg['nombre']:
                           cg['chat'].append(msg)
                elif data[0]=='5':
                    aux_msg = data[1] +" te ha enviado un archivo: "+data[3]
                    f = open(data[3],'wb')       
                    l = s.recv(1024)
                    while (l):
                            f.write(l)
                            l = s.recv(1024)
                            if l == "close":
                                break
                    f.close()
                    if data[1] not in contactos:
                        contactos.append(data[1])
                        chat = {'name': data[1], 'chat': []}
                        chats.append(chat)
                    for c in chats:
                        if data[1]==c['name']:
                            c['chat'].append(aux_msg)
                    
        except:
            time.sleep(0.2)
        finally:
            tLock.release()

#Funcion para conseguir ip lan del dispositivo.
def lanip():
    aux = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    aux.connect(("8.8.8.8", 80))
    lan_ip =(aux.getsockname()[0])
    aux.close()
    return lan_ip

#Funcion clear.
clear = lambda: os.system('cls')

#Lista de contactos y respectivos chats.
contactos = []
chats = []
grupos = []
chatsg = []


tLock = threading.Lock()

#Direccion del servidor.
host_ip= raw_input("Ingresar ip de dispositivo con servidor : ")
#host_ip='192.168.0.133'
server = (host_ip,5000)

#Direccion del dispositivo.
host = lanip()
port = 0

#try:
 #   host = lanip()
#except:
 #   host = '127.0.0.1'

#Se crea socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0) #Para que no se quede esperando si no llega nada por el socket.

#Se crea el thread que recibe mensajes.
rT = threading.Thread(target=receving, args=("RecvThread",s))
rT.start()

#Funciones de Menu
#Menu principal
def menu():
    option = -1
    while option !=0:
        print "1. Contactos"
        print "2. Grupos"
        print "0. Salir"
        try:
            option = int(raw_input("opcion: "))
            clear()
        except:
            raw_input('Comando Mal Ingresado')
            clear() 
        if option == 1:
            contact()
        elif option == 2:
            group()
        else:
            raw_input('Opcion fuera de rango')
    return

#chat de contactos
def chatroom(num):
    message=''
    while message!='_b':
        if message != '':
            s.sendto("1/%" +alias + "/%"+chats[num]['name']+"/%" + message, server)
            msg = alias +":"+message
            chats[num]['chat'].append(msg)
        print 'Enviar Mensaje o Apretar enter para actualizar el chat.'
        print 'Enviar _f nombre_archivo para enviar un archivo.'
        print 'Enviar _b para volver.'
        for c in chats[num]['chat']:
            print c
        tLock.acquire()
        message = raw_input(alias + "-> ")
        if "_f" in message:
            file_aux = message.split()
            try:
                if file_aux[0]=="_f":
                        f = open (file_aux[1], "rb")
                        s.sendto("5/%" +alias + "/%"+chats[num]['name']+"/%" + file_aux[1], server)
                        l = f.read(1024)
                        while (l):
                            s.sendto(l, server)
                            l = f.read(1024)
                        s.sendto("close", server)
            except:
                raw_input("Comando Mal Ingresado.")
            message = ""
        tLock.release()
        time.sleep(0.2)
        clear()
    return
#Crear grupos
def create_group(name,contacts):
     ms=''
     for i in range(len(contacts)):
         if i<len(contacts)-1:
             ms+=contacts[i]+","
         else:
             ms+=contacts[i]
     ms+=","+alias
     s.sendto("2/%" +name + "/%"+ms, server)
     time.sleep(0.2)
     return
def chatgroup(num):
    message=''
    while message!='_b':
        if message != '':
            s.sendto("3/%" +alias + "/%"+chatsg[num]['nombre']+"/%" + message, server)
            msg = alias +":"+message
            chatsg[num]['chat'].append(msg)
        print 'Enviar Mensaje o Apretar enter para actualizar el chat.'
        print 'Enviar _b para volver.'
        for c in chatsg[num]['chat']:
            print c
        tLock.acquire()
        message = raw_input(alias + "-> ")
        tLock.release()
        time.sleep(0.2)
        clear()
    return
def delgroup(num):
    s.sendto("4/%" +num, server)
    time.sleep(0.2)
    return
#Menu contactos
def contact():
    option = 1
    while option !=0:
        i = 0
        #Imprime los contactos para poder seleccionarlos.
        for c in contactos:
            i+=1
            print str(i)+" - " + c
        #Opciones.
        print "0 - Volver"
        print "New - Agregar Contacto (Ej: New Nombre_Contacto)"
        print "Del - Eliminar Contacto (Ej: Del Nombre_Contacto)"
        option = raw_input("opcion: ")
        clear()
        try:
            op = int(option)
            norc = 0 #norc= numero o caracter.
        except ValueError:
            
            op = option.split()
            norc = 1
        #Abrir chat con contacto.
        if norc == 0:
            if op > 0 and op <= len(contactos):
                chatroom(op-1)
            elif op > len(contactos):
                raw_input("Contacto fuera de rango.")
                clear()
            else:
                option = 0
        else:
            #Agregar Contacto.
            try :
                if op[0] == "New":
                    
                        if op[1] not in contactos:
                            contactos.append(op[1])
                            chat = {'name': op[1], 'chat': []}
                            chats.append(chat)
                        else:
                            raw_input("Contacto ya existe.")
                            clear()
                  
                #Eliminar Contacto
                elif op[0] == "Del":
                    
                        if op[1] in contactos:
                            contactos.remove(op[1])
                            for ch in chats:
                                if ch['name']==op[1]:
                                    chats.remove(ch)
                                else:
                                    raw_input("No existe contacto.")
                                    clear()
                elif op[0] == "Listar":
                    for ch in chats:
                        print ch['name'] + str(ch['chat'])
                else:
                    raw_input("Comando Desconocido.")
                    clear() 
            except:
                    raw_input("Comando Mal Ingresado.")
                    clear()
                
    return

def group():
    option = 1
    while option !=0:
        ie = 0
        for c in grupos:
            ie+=1
            print str(ie)+" - " + c
        #Opciones.
        print "0 - Volver"
        print "New - Agregar Grupo (Ej: New Nombre_Grupo)"
        print "Del - Eliminar Grupo (Ej: Del Nombre_Grupo)"
        option = raw_input("opcion: ")
        clear()
        try:
            op = int(option)
            norc = 0
        except ValueError:
            op = option.split()
            norc = 1
        #Abrir chat con Grupo.
        if norc == 0:
            if op > 0 and op <= len(grupos):
                chatgroup(op-1)
                        
            elif op > len(grupos):
                raw_input("Grupo fuera de rango.")
                clear()
            else:
                option = 0
        else:
            #Agregar Grupo.
            try:
                if op[0] == "New":
                      
                            print 'Seleccione los contactos para agregar a su grupo\nPesione s para salir'
                            opcion=''
                            if len(contactos)<=1:
                                raw_input('No tiene suficientes contactos para hacer un grupo')
                                return
                            if op[1] not in grupos:
                                grupos.append(op[1])
                                agregar={'nombre':op[1],'cont':[], 'ides':[], 'chat':[]}
                                i=0
                                for c in contactos:
                                    i+=1
                                    print str(i)+" - " + c
                                while opcion!='s' and len(agregar['cont'])<len(contactos):
                                   
                                    opcion=raw_input('Numero de contacto a agregar:')
                                    
                                    try:
                                        opcion=int(opcion)
                                        print opcion
                                        if opcion > 0 and opcion <= len(contactos):
                                            if contactos[opcion-1] not in agregar['cont']:
                                                agregar['cont'].append(contactos[opcion-1])
                                                agregar['ides'].append(opcion-1)
                                            else:
                                                raw_input('Contacto ya agregado al grupo')
                                        else:
                                            raw_input('Numero Fuera de Rango')
                                    except:
                                        continue
                                    print 'Contactos actuales:',agregar['cont']
                                chatsg.append(agregar)
                                create_group(op[1],agregar['cont'])
                                clear() 
                            else:
                                raw_input("Grupo ya existe.")
                                clear()
                      
                #Eliminar Grupo
                elif op[0] == "Del":
                 
                        if op[1] in grupos:
                            delgroup(op[1])
                            grupos.remove(op[1])
                            for ch in chatsg:
                                if ch['nombre']==op[1]:
                                    chatsg.remove(ch)
                        else:
                            raw_input("No existe Grupo.")
                            clear()    
                    
                elif op[0] == "Listar":
                    for ch in chatsg:
                        print ch['nombre'] + str(ch['chat'])
                else:
                    raw_input("Comando Desconocido.")
                    clear() 
            except:
                    raw_input("Comando Mal Ingresado.")
                    clear()
            
    return

alias = raw_input("Nombre: ")
s.sendto("0/%" + alias, server)
clear()

menu()

rT.do_run = False
rT.join()
s.close()
