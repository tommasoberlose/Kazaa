import Function as func
import Constant as const
import Package as pack
import Daemon as daemon
import os
import sys
import time
import hashlib

def login(host, SN, SN_host, listPkt):
	s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1])
	pk = pack.request_login(host)
	if s is None:
		func.error("Errore nell'apertura della socket per il login")
		update_network(host, SN, listPkt)
	else:
		s.sendall(pk)
		ricevutoByte = s.recv(const.LENGTH_PACK)
		sessionID = ricevutoByte[4:20]
		s.close()
		return sessionID

def progress():
	print("|||", end = "")

def update_network(host, SN, listPkt):
	func.warning("\nP2P >> CREATION NETWORK")

	while True:
		nGroup = input("Inserire il numero del gruppo: ")
		nElement = input("Inserire il numero dell'elemento del gruppo: ")
		nPort = input("Inserire il numero della porta: ")
		Fhost = [("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
					"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
					"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
					":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0")), nPort]


		if SN:
			pk = pack.request_sn(host, const.PORT_SN)
			func.add_pktid(pk[4:20], listPkt, const.PORT_SN)
		else:
			pk = pack.request_sn(host, const.PORT)
			func.add_pktid(pk[4:20], listPkt, const.PORT)

		s = func.create_socket_client(func.roll_the_dice(Fhost[0]), Fhost[1]);
		if s is None:
			func.error("Errore nella scelta del primo nodo vicino, scegline un altro.")
		else:
			s.sendall(pk)
			s.close()
			break

	# Caricamento
	print("Loading...")

	for i in range(0, int(const.MAX_TIME / 1000)):
		print("|", end = "")
		print("|||" * i + " " * ((int(const.MAX_TIME / 1000) * 3) - (i * 3)) + "|")
		time.sleep(1)

	print("|" + "|||" * int(const.MAX_TIME / 1000) + "|")

	if SN:
		func.success("NETWORK CREATED:")
		for h in sn_network:
			func.gtext(h[0] + " - " + h[1])

	if SN:
		SN_host = [host, const.PORT_SN]
	else:
		SN_host = func.choose_SN(sn_network)

	return SN_host


def search(sessionID, query, SN, SN_host, host, listPkt):
	ricevutoByteRam = b''
	ricevutoByte = b''
	pk = pack.request_search(sessionID, query)
	s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1]);
	if s is None:
		func.error("Super nodo non attivo.")
		update_network(host, SN, listPkt)
	else:
		s.sendall(pk)

		ricevutoByte = s.recv(4 * const.LENGTH_PACK)

		if str(ricevutoByte[0:4],"ascii") == const.CODE_ANSWER_SEARCH:
			print(ricevutoByte)
			nIdmd5 = int(ricevutoByte[4:7])
			if(nIdmd5 != 0):
				func.success("Ricerca completata.")
				pointer = 7
				id = 0
				listFile = []
				for j in range(0, nIdmd5):
					md5 = ricevutoByte[pointer:pointer + 32]
					nomeFile = ricevutoByte[pointer + 32:pointer + 132]
					nCopy = int(ricevutoByte[pointer + 132:pointer + 135])

					pointer = pointer + 135

					for i in range(0, nCopy):
						ip = ricevutoByte[pointer:pointer + 55]
						port = ricevutoByte[pointer + 55:pointer + 60]
						id = id + 1
						pointer = pointer + 60
						fixList = [id, md5, nomeFile, ip, port]
						listFile.append(fixList)

				print("\nScegli file da quelli disponibili (0 per uscire): \n")
				print("FILE    \t\tID\tIP\n")
				lastFileName = b''
				for row in listFile:
					if lastFileName != row[2]:
						nomeFile = func.reverse_format_string((str(row[2], "ascii").strip() + ":"), const.LENGTH_FORMAT, " ")
						print(nomeFile + str(row[0]) + "\t" + str(row[3], "ascii"))
					else:
						print("\t\t\t" + str(row[0]) + "\t" + str(row[3], "ascii"))
					lastFileName = str(row[2], "ascii")
				
				selectId = input("\nInserire il numero di file che vuoi scaricare (0 per uscire): ")
				
				if(selectId != "0"):
					for i in range (0, id):
						if listFile[i][0] == int(selectId):
							selectFile = listFile[i]
							break

					func.download(selectFile)

			else:
				func.error("Non sono presenti file con questa query nel nome: " + query)
		s.close()

# Funzione di aggiunta file
def add_file(fileName, sessionID, SN, SN_host, host, listPkt):
	if os.path.exists("FileCondivisi/" + fileName):
		md5File = hashlib.md5(open(("FileCondivisi/" + fileName),'rb').read()).hexdigest()
		pk = pack.request_add_file(sessionID, md5File, func.format_string(fileName, const.LENGTH_FILENAME, " "))
		s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1]);
		if s is None:
			func.error("Errore, super nodo non attivo.")
			update_network(host, SN, listPkt)
		else:
			s.sendall(pk)
			s.close()
	else:
		func.error("Errore: file non esistente.")

# Funzione di rimozione del file
def remove_file(fileName, sessionID, SN, SN_host, host, listPkt):
	if os.path.exists("FileCondivisi/" + fileName):
		md5File = hashlib.md5(open(("FileCondivisi/" + fileName),'rb').read()).hexdigest()
		pk = pack.request_remove_file(sessionID, md5File)
		s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1]);
		if s is None:
			func.error("Errore, super nodo non attivo.")
			update_network(host, SN, listPkt)
		else:
			s.sendall(pk)
			s.close()
	else:
		func.error("Errore: file non esistente.")
	

def logout(ip, sessionID, SN, SN_host):
	print ("\n>>> LOGOUT")
	pk = pack.request_logout(sessionID)
	s = func.create_socket_client(func.roll_the_dice(SN_host[0]), SN_host[1]);
	if s is None:
		func.error("Errore nel logout dal super nodo, vabbè")
	else:
		s.sendall(pk)
		ricevutoByte = s.recv(const.LENGTH_PACK)
		nDelete = ricevutoByte[4:]
		func.success("Logout eseguito con successo dal super nodo, eliminati " + str(nDelete, "ascii") + " elementi")
		s.close()

	pk = pack.close()
	s = func.create_socket_client(func.roll_the_dice(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone")
	else:
		s.sendall(pk)
		s.close()
		print ("Chiusura del peer eseguito con successo, arrivederci.\n\n")

	if SN:
		s = func.create_socket_client(func.roll_the_dice(ip), const.PORT_SN);
		if s is None:
			func.error("Errore nella chiusura del demone super nodo")
		else:
			s.sendall(pk)
			s.close()
			print ("Chiusura del supernodo eseguita con successo, arrivederci.\n\n")



####### VARIABILI 

SN = False
sessionID = ""

sn_network = []
listPkt = [] # [pktid, time, port]
listUsers = [] # [ip, port, sessionID]
listFiles = [] # [md5, fileName, sessionID]

host = ""

####### INIZIALIZZAZIONE

for i in range(len(sys.argv)):

	if sys.argv[i] == "-sn":
		SN = True

	elif sys.argv[i] == "-ip":
		try:
			nGroup = sys.argv[i + 1]
			nElement = sys.argv[i + 2]
		
			host = ("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
						"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
						"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
						":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))
		except:
			func.error("Errore inserimento dati")
			func.writeHelp()

	elif sys.argv[i] == "-p":
		try:
			const.PORT = sys.argv[i + 1]
		except:
			func.error("Errore inserimento dati")
			func.writeHelp()

	elif sys.argv[i] == "-pSN":
		try:
			const.PORT_SN = sys.argv[i + 1]
		except:
			func.error("Errore inserimento dati")
			func.writeHelp()

	elif sys.argv[i] == "-t":
		try:
			const.MAX_TIME = int(sys.argv[i + 1]) * 1000
		except:
			func.error("Errore inserimento dati")
			func.writeHelp()

	elif sys.argv[i] == "-ttl":
		try:
			const.TTL = sys.argv[i + 1]
		except:
			func.error("Errore inserimento dati")
			func.writeHelp()

	elif sys.argv[i] == "-h":
		func.writeHelp()


if SN:
	func.warning("\nP2P >> INIZIALIZZAZIONE COME SUPER NODO")
else:
	func.warning("\nP2P >> INIZIALIZZAZIONE COME PEER")


if host == "":
	nGroup = input("Inserire il numero del gruppo: ")
	nElement = input("Inserire il numero dell'elemento del gruppo: ")
	host = ("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
					"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
					"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
					":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))
func.gtext("IP: " + host)

####### DEMONI

if SN:
	daemonThreadSN = daemon.Daemon(host, True, sn_network, listPkt, listUsers, listFiles, True)
	daemonThreadSN.setName("DAEMON SN")
	daemonThreadSN.start()

	daemonThreadP = daemon.Daemon(host, True, sn_network, listPkt, listUsers, listFiles, False)
	daemonThreadP.setName("DAEMON PEER")
	daemonThreadP.start()

else:
	daemonThreadP = daemon.Daemon(host, False, sn_network, listPkt, listUsers, listFiles, False)
	daemonThreadP.setName("DAEMON PEER")
	daemonThreadP.start()	

####### INIZIALIZZAZIONE NETWORK

SN_host = update_network(host, SN, listPkt)

func.gtext("SN HOST: " + SN_host[0])

####### LOGIN AUTOMATICO PEER

func.warning("\nP2P >> PEER LOGIN")
print(SN_host)
sessionID = login(host, SN, SN_host, listPkt)
if sessionID is not const.ERROR_LOG:
	func.success("Session ID: " + str(sessionID, "ascii"))

	# MENU

	while True:
		if SN:
			print ("\n\nScegli azione SN:\nuser\t - View Users\nfile\t - View Files")
		print ("\n\nScegli azione PEER:\nadd\t - Add File\nremove\t - Remove File\nsearch\t - Search File\nquit\t - Quit\n\n")
		choice = input()

		if (choice == "add" or choice == "a"):
			func.warning("\n>>> ADD FILE")
			fileName = input("Quale file vuoi inserire?\n")
			if fileName is not "0":
				add_file(fileName, sessionID, SN, SN_host, host, listPkt)

		elif (choice == "remove" or choice == "r"):
			func.warning("\n>>> REMOVE FILE")
			fileName = input("Quale file vuoi rimuovere?\n")
			if fileName is not "0":
				remove_file(fileName, sessionID, SN, SN_host, host, listPkt)

		elif (choice == "user" or choice == "u"):
			func.warning("\n>>> USER LIST")
			print ("USER IP\t\t\tSESSIONID")
			for user in listUsers:
				print(str(user[0], "ascii") + " " + str(user[1], "ascii") + "\t" + str(user[2], "ascii") + "\t" + str(func.countUserFile(user[2], listFiles)))

		elif (choice == "file" or choice == "f"):
			func.warning("\n>>> FILES LIST")
			print ("MD5\tFILENAME\tSESSIONID")
			for file in listFiles:
				print(str(file[0], "ascii") + "\t" + str(file[1].strip(), "ascii") + "\t" + str(file[2], "ascii"))

		elif (choice == "search" or choice == "s"):
			func.warning("\n>>> SEARCH")
			query = input("\nInserisci il nome del file da cercare: ")
			while(len(query) > const.LENGTH_QUERY):
				func.error("Siamo spiacenti ma accettiamo massimo 20 caratteri.")
				query = input("\nInserisci il nome del file da cercare: ")
			search(sessionID, query, SN, SN_host, host, listPkt)

		elif (choice == "quit" or choice == "q"):
			logout(host, sessionID, SN, SN_host)
			if SN:
				daemonThreadSN.join()
			daemonThreadP.join()
			break

		else:
			func.error("Wrong Choice!")
else:
	func.error("Errore Login")