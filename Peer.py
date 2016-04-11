import Function as func
import Constant as const
import Package as pack
import Daemon as daemon
import os
import sys

def login(host, SN_host):
	s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1])
	pk = pack.login(host)
	if s is None:
		func.error("Errore nell'apertura della socket per il login")
	else:
		s.sendall(pk)
		ricevutoByte = s.recv(const.LENGTH_PACK)
		sessionID = ricevutoByte[4:20]
		s.close()
		return sessionID

def update_network(host, sn_network, listPkt):
	del sn_network[:]
	pk = pack.request_sn(host)
	func.add_pktid(pk[4:20], listPkt)
	while True:
		nGroup = input("Numero del gruppo: ")
		if nGroup is 0:
			break
		nElement = input("Numero dell'elemento del gruppo: ")
		if nElement is 0:
			break
		hostN = func.roll_the_dice("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
																"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
																"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
																":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))
		s = func.create_socket_client(hostN, const.PORT_SN);
		if s is None:
			func.error("Errore nella scelta del primo super nodo vicino, scegline un altro.")
		else:
			s.sendall(pk)
			s.close()
			break

def search(sessionID, query, SN_host):
	pk = pack.request_search(sessionID, query)
	s = func.create_socket_client(func.roll_the_dice(x[0]), x[1]);
	if s is None:
		func.error("Super nodo non attivo.")
	else:
		s.sendall(pk)
		s.close()

# Funzione di aggiunta file
def add_file(fileName, sessionID):
	if os.path.exists("FileCondivisi/" + nomeFile):
		md5File = hashlib.md5(open(("FileCondivisi/" + nomeFile),'rb').read()).hexdigest()
		pk = pack.request_add_file(sessionID, md5, func.format_string(fileName, const.LENGTH_FILENAME, " "))
		s = func.create_socket_client(SN_host[0], SN_host[1]);
		if s is None:
			func.error("Errore, super nodo non attivo.")
		else:
			s.sendall(pk)
			s.close()
	else:
		func.error("Errore: file non esistente.")

# Funzione di rimozione del file
def remove_file(fileName, sessionID):
	if os.path.exists("FileCondivisi/" + nomeFile):
		md5File = hashlib.md5(open(("FileCondivisi/" + nomeFile),'rb').read()).hexdigest()
		pk = pack.request_remove_file(sessionID, md5)
		s = func.create_socket_client(SN_host[0], SN_host[1]);
		if s is None:
			func.error("Errore, super nodo non attivo.")
		else:
			s.sendall(pk)
			s.close()
	else:
		func.error("Errore: file non esistente.")
	

def logout(ip, sessionID, SN_host):
	print ("\n>>> LOGOUT")
	pk = pack.request_logout(sessionID)
	s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1]);
	if s is None:
		func.error("Errore nel logout dal super nodo")
	else:
		s.sendall(pk)
		ricevutoByte = s.recv(const.LENGTH_PACK)
		nDelete = ricevutoByte[4:]
		func.success("Logout eseguito con successo dal super nodo, eliminati " + str(nDelete, "ascii") + "elementi")
		s.close()

	pk = pack.close()
	s = func.create_socket_client(func.roll_the_dice(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone")
	else:
		s.sendall(pk)
		s.close()
		print ("Chiusura del programma eseguito con successo, arrivederci.\n\n")



####### VARIABILI 

SN = False
if (len(sys.argv) > 1) and (sys.argv[1] == "-sn"):
	SN = True
	func.warning("\nP2P >> INIZIALIZZAZIONE COME SUPER NODO")
else:
	func.warning("\nP2P >> INIZIALIZZAZIONE COME PEER")

sessionID = ""
SN_host = []

sn_network = []
listPkt = [] # [pktid, time]
listUsers = [] # [ip, port, sessionID]
listFiles = [] # [md5, fileName, sessionID]

####### INIZIALIZZAZIONE

if len(sys.argv) > 2:
	if SN:
		nGroup = sys.argv[2]
		nElement = sys.argv[3]
	else:
		nGroup = sys.argv[1]
		nElement = sys.argv[2]
else:
	nGroup = input("Inserire il numero del gruppo: ")
	nElement = input("Inserire il numero dell'elemento del gruppo: ")

host = ("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
				"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
				"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
				":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))

func.gtext("IP: " + host)

####### DEMONE

daemonThread = daemon.Daemon(host, SN, sn_network, listPkt, listUsers, listFiles)
daemonThread.setName("DAEMON")
#daemonThread.start()	

####### INIZIALIZZAZIONE SN del PEER

if SN:
	SN_host = [host, const.PORT_SN]
else:
	func.warning("\nP2P >> CHOOSE SN")
	SN_nGroup = input("Inserire il numero del super nodo: ")
	SN_nElement = input("Inserire il numero dell'elemento del super nodo: ")
	SN_host = [("172.030." + func.format_string(SN_nGroup, const.LENGTH_SECTION_IPV4, "0") + 
				"." + func.format_string(SN_nElement, const.LENGTH_SECTION_IPV4, "0") + 
				"|fc00:0000:0000:0000:0000:0000:" + func.format_string(SN_nGroup, const.LENGTH_SECTION_IPV6, "0") + 
				":" + func.format_string(SN_nElement, const.LENGTH_SECTION_IPV6, "0")), const.PORT_SN]

func.gtext("SN HOST: " + host)

####### UPDATE NETWORK SN

if SN:
	func.warning("\nP2P >> CREATION SN NETWORK: ")
	update_network(host, sn_network, listPkt)

####### LOGIN AUTOMATICO PEER

func.warning("\nP2P >> PEER LOGIN:")
sessionID = login(host, SN_host)
if sessionID is not const.ERROR_LOG:
	func.success("Session ID: " + sessionID)

	# MENU

	while True:
		print ("\n\nScegli azione SN:\nuser\t - View Users\nfile\t - View Files")
		print ("\n\nScegli azione PEER:\nadd\t - Add File\nremove\t - Remove File\nsearch\t - Search File\nquit\t - Quit\n\n")
		choice = input()

		if (choice == "add" or choice == "a"):
			func.warning("\n>>> ADD FILE")
			fileName = input("Quale file vuoi inserire?")
			if fileName is not "0":
				add_file(fileName, sessionID)

		elif (choice == "remove" or choice == "r"):
			func.warning("\n>>> REMOVE FILE")
			fileName = input("Quale file vuoi rimuovere?")
			if fileName is not "0":
				remove_file(fileName, sessionID)

		elif (choice == "user" or choice == "u"):
			func.warning("\n>>> USER LIST")
			print ("USER IP\t\t\tSESSIONID")
			for user in listUsers:
				print(user[0] + " " + user[1] + "\t" + user[2] + "\t" + func.countUserFile(user[2], listFiles))

		elif (choice == "file" or choice == "f"):
			func.warning("\n>>> FILES LIST")
			print ("MD5\tFILENAME\tSESSIONID")
			for file in listFiles:
				print(file[0] + "\t" + file[1].strip() + "\t" + file[2])

		elif (choice == "search" or choice == "s"):
			func.warning("\n>>> SEARCH")
			query = input("\nInserisci il nome del file da cercare: ")
			while(len(query) > const.LENGTH_QUERY):
				func.error("Siamo spiacenti ma accettiamo massimo 20 caratteri.")
				query = input("\nInserisci il nome del file da cercare: ")
			search(sessionID, query, SN_host)

		elif (choice == "quit" or choice == "q"):
			logout(host, sessionID, SN_host)
			daemonThread.join()
			break

		else:
			func.error("Wrong Choice!")
else:
	func.error("Errore Login")