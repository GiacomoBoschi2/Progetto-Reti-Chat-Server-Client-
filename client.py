"""Progetto di progettazione di reti,parte client per la realizzazione di una chat.
   Boschi Giacomo.
"""

from socket import AF_INET, socket, SOCK_STREAM , SHUT_RDWR
from threading import Thread
import tkinter as tkt
import re
import os
import random

#ricezione messaggi
def ricevi(): 
    global socket_avviato
    while socket_avviato:
        try:
            #ricezione
            messaggio = client_socket.recv(MASSIMA_DIMENSIONE_BUFFER).decode("utf8")
            #visualizza messaggio
            if socket_avviato:
               for riga in messaggio.split('\n'):
                  lista_messaggi.insert(tkt.END, riga)
        except OSError:  
            break

#se la connessione avviene con successo, nascono le cose non più necessarie
def nascondi_menu_connessioni():
   bottone_per_indirizzo.pack_forget()
   campo_ip.pack_forget()
   campo_porta.pack_forget()
   bottone_per_codice.pack_forget()
   campo_codice.pack_forget()
   msg_label.pack_forget()
   username_label.pack_forget()
   campo_username.pack_forget()
   indirizzo_label.pack_forget()
   porta_label.pack_forget()
   codice_label.pack_forget()

def avvia_interfaccia_messaggi():
   finestra.geometry("900x900")
   messaggi_msg.set("puoi scrivere i tuoi messaggi qui.")
   scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
   lista_messaggi.pack(side=tkt.LEFT, fill=tkt.BOTH)
   lista_messaggi.pack()
   messages_frame.pack()
   campo_messaggi.pack()
   bottone_invio.pack()

#tenta di connettersi alla chat con indirizzo ip e porta
def tenta_connessione_con_ip():
   #procedi solo se c'è uno username:
   if not(username.get() and username.get().strip()):
      mesg_comunica.set("fornire uno username prima.")
      return
   try:
      indirizzo = (indirizzo_ip_msg.get(), int(porta_msg.get()))
      client_socket.connect(indirizzo)
      global socket_avviato
      socket_avviato = True
      nascondi_menu_connessioni()
      avvia_interfaccia_messaggi()
      receive_thread.start()
      #invia il tuo username
      client_socket.send(campo_username.get().encode())
   except Exception as e:
      mesg_comunica.set("qualcosa è andato storto... riprova-->"+str(e))

#transla il codice di invito in indirizzo ip + porta
def tenta_connessione_con_codice():
   #12 cifre esadecimali: 8 per l'ip e 4 per la porta
   codice=campo_codice.get()
   if len(codice)!=12 or not re.match("^[A-Fa-f0-9]+$",codice):
      mesg_comunica.set("Codice di invito non valido")
   else:
      indirizzo=""
      for i in range(0,8,2):
         parte_ip = codice[i]+codice[i+1]
         indirizzo+=str(int(parte_ip,16))+"."
      indirizzo_ip_msg.set(indirizzo[:-1]) # rimuovo il punto in più :)
      porta_msg.set(str(int(codice[8:],16)))
      tenta_connessione_con_ip()

def invia_messaggio():
   try:
      client_socket.send(messaggi_msg.get().encode("utf8"))
      if messaggi_msg.get() == "{quit}":
         chiudi()
      else:
         messaggi_msg.set("")
   except:
      mesg_comunica.set("qualcosa è andato storto... se il problema persiste riavviare l'applicazione.")


#setta posizione elemnti e avvia game_loop
def avvia_finestra():
   finestra.geometry("600x600")
   #pack dei componenti
   username_label.pack()
   campo_username.pack()
   indirizzo_label.pack()
   campo_ip.pack()
   porta_label.pack()
   campo_porta.pack()
   bottone_per_indirizzo.pack()
   codice_label.pack()
   campo_codice.pack()
   bottone_per_codice.pack()
   msg_label.pack()
   finestra.mainloop()

#metodo di chiusura
def chiudi():
   finestra.quit()
   finestra.destroy()
   try:
      global socket_avviato
      if socket_avviato:
         socket_avviato = False
         client_socket.close()
         print("client chiuso")
   except Exception as e:
      print("error occured on closing->"+str(e))
   os._exit(0)

      

#inizializza la parte grafica tramite tkniter

finestra =tkt.Tk()
finestra.title("Progetto chat")

"""variabili di connessione"""
indirizzo_ip_msg=tkt.StringVar()
porta_msg=tkt.StringVar()
codice_invito_msg=tkt.StringVar()
"""Variabile per inviare messaggi e fornire uno username"""
messaggi_msg=tkt.StringVar()
username=tkt.StringVar()

"""valori di default"""
indirizzo_ip_msg.set("127.0.0.1")
porta_msg.set("50002")
codice_invito_msg.set("")
username.set("user"+str(random.randint(1000,9999)))

"""crea i campi di inserimento"""
campo_ip = tkt.Entry(finestra, textvariable=indirizzo_ip_msg)
campo_porta = tkt.Entry(finestra, textvariable=porta_msg)
campo_codice = tkt.Entry(finestra, textvariable=codice_invito_msg)
campo_messaggi = tkt.Entry(finestra, textvariable=messaggi_msg)
campo_username = tkt.Entry(finestra, textvariable=username)

"""Bottoni di invio"""
bottone_per_indirizzo = tkt.Button(finestra, text="Prova a connetterti", command=tenta_connessione_con_ip)
bottone_per_codice = tkt.Button(finestra, text="Prova a connetterti con codice", command=tenta_connessione_con_codice)
bottone_invio = tkt.Button(finestra,text="Invia messaggio",command=invia_messaggio)

"""Altre label utili"""
mesg_comunica = tkt.StringVar()
mesg_comunica.set("nessun errore al momento!")
username_label= tkt.Label(finestra,text="Fornisci uno username")
indirizzo_label= tkt.Label(finestra,text="Indirizzo Ip")
porta_label= tkt.Label(finestra,text="Porta")
codice_label= tkt.Label(finestra,text="Codice d'invito")
msg_label=tkt.Label(finestra,textvariable=mesg_comunica)
MASSIMA_DIMENSIONE_BUFFER = 512

"""visualizzatore per i messaggi"""
messages_frame = tkt.Frame(finestra)
scrollbar = tkt.Scrollbar(messages_frame)
lista_messaggi = tkt.Listbox(messages_frame, height=30, width=200, yscrollcommand=scrollbar.set)

#socket di comunicazione 
client_socket = socket(AF_INET, SOCK_STREAM)

#quando la finestra si chiude devo fermare l'applicazione
finestra.protocol("WM_DELETE_WINDOW", chiudi)

#thread da avviare una volta instaurata la connessione
receive_thread = Thread(target=ricevi)
socket_avviato = False

#create tutte le variabili,avvio la finestra
avvia_finestra()
