#!usr/bin/env python3
from socket import *
import threading
"""Progetto di programmazione di reti,parte server per la realizzazione di una chat.
   Boschi Giacomo.
"""

"""Piccola classe per contenere le informazioni di uno user (username,address,porta,socket)"""
class User:
    def __init__(self,username:str, sock:socket):
        self.username = username
        self.address = sock.getsockname()[0]
        self.port = sock.getsockname()[1]
        self.socket = sock

    """Invia dati con questo metodo"""
    def inviaMessaggio(self,messaggio):
        try:
            self.socket.send(messaggio)
        except:
            print("Impossibile raggiungere utente "+self.username+",disconnessione in corso...")
            self.disconnetti()

    """Auto gestione dell user.Questo metodo si mette in ascolto per ricevere messaggio e comunicazioni dalla chat"""
    def handle(self):
        while True:
            try:
                messaggio = self.socket.recv(MASSIMA_DIMENSIONE_BUFFER)
                #se il messaggio non è un comando è da inviare a tutta la chat.
                if len(messaggio)<2 or messaggio[0]!=ord('{') or messaggio[-1] !=ord('}'):
                    broadcast(bytes(self.username+": ","utf8")+messaggio)
                else:
                    self.handle_comando(messaggio)
            except OSError:
                if self in users:
                    print("errore avvenuto per utente "+self.username+",connessione interrotta")
                break

    """gestisce un comando fornito dall utente,un comando è identificato dalle graffe a inizio e fine messaggio {}"""
    def handle_comando(self,messaggio):
        if messaggio == b"{help}":
            self.inviaMessaggio(b"{help} per una lista di comandi.\n{users} per vedere gli users online.\n{quit} per uscire.")
        elif messaggio == b"{users}":
            risposta = b"Utenti online:\n"
            for user in users:
                risposta+=user.username.encode("utf8")+b"\n"
            self.inviaMessaggio(risposta)
        elif messaggio == b"{quit}":
            self.disconnetti()
        else:
            self.inviaMessaggio(b"comando non riconosciuto,usa {help} per una lista di comandi.")

    """Permette di disconnettere l'utente e rimuoverlo dagli utenti"""
    def disconnetti(self):
        print(self.username+" si è disconnesso")
        self.socket
        self.socket.close()
        users.remove(self)
        broadcast(bytes(self.username+" si è disconnesso.","utf8"))

#array utenti e dimensione buffer
users = []
MASSIMA_DIMENSIONE_BUFFER = 1024
codice_invito=""

"""Funzioni da chiamare all'inizio"""
#setup per il server
def setup():
    INDIRIZZO_IP = "127.0.0.1"
    PORTA = 50002

    #dai possibilità di cambiare porta/indirizzo
    scelta = input(f"Utilizzare porta e indirizzo di default? ({INDIRIZZO_IP},{PORTA})? S/N\n")

    if(scelta != "S"):
        INDIRIZZO_IP = input("indirizzo IP:")
        PORTA = int(input("porta:"))
    try:
        SERVER = socket(AF_INET, SOCK_STREAM)
        SERVER.bind((INDIRIZZO_IP,PORTA))
    except:
        print("errore imprevisto,riavviare l'applicazione (prova a cambiare indirizzo o porta).")
        exit(0)

    #crea il codice di invito
    global codice_invito
    for parte in INDIRIZZO_IP.split('.'):
        codice_invito+=hex(int(parte))[2:].zfill(2)
    codice_invito+=hex(PORTA)[2:]
    codice_invito = codice_invito.upper()
    return SERVER

#funzione di avvio per il server
def avvia_server(server:socket):
    server.listen(10)
    print("In ascolto per connessioni...")
    #crea thread asincrono per ascoltare connessioni
    thread_per_nuova_connessione = threading.Thread(target=accetta_nuova_connessione,args=[server])
    thread_per_nuova_connessione.start()
    thread_per_nuova_connessione.join()
    #chiudi server quando il thread asincrono termina
    print("Ascolto del server terminato.")
    server.close()

"""Funzioni per il funzionamento del server"""
def accetta_nuova_connessione(server:socket):
    while True:
        #in attesa di una richiesta di connessione.
        client,indirizzo_client = server.accept()
        print("Accettata connessione da %s",indirizzo_client)
        #si attende di ricevere uno username e lo si registra nell'array.
        username = client.recv(MASSIMA_DIMENSIONE_BUFFER).decode("utf8")
        nuovo_user = User(username,client)
        users.append(nuovo_user)
        nuovo_user.inviaMessaggio(b"Benvenuto! usa {help} per una lista di comandi utili\nPuoi utilizzare questo codice per invitare altri utenti:"+codice_invito.encode("utf8")+b'\n')
        broadcast(username.encode("utf8")+bytes(" è entrato in chat.","utf8"))
        threading.Thread(target=nuovo_user.handle).start()

def broadcast(messaggio):
    for user in users:
        user.inviaMessaggio(messaggio)

if __name__ == "__main__":
    server = setup()
    avvia_server(server)
