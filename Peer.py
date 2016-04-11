import Function as func
import Constant as const
import Package as pack
import Daemon as daemon
import os

def updateNeighbor(myHost, listNeighbor):
	del listNeighbor[:]
	pk = pack.neighbor(myHost)
	# Se avevo già dei vicini vado a testare se sono ancora attivi
	"""if len(listNeighbor) != 0:
		for neighbor in listNeighbor:
			s = func.create_socket_client(func.roll_the_dice(neighbor[0]), neighbor[1]);
			# Se non sono più attivi lo segnalo e li cancello dalla lista
			if s is None:
				func.error(str(neighbor[0], "ascii") + " non è più attivo.")
				del neighbor
			else:
				func.success(str(neighbor[0], "ascii") + " ancora attivo.")
				s.close()
		# Se prima ero al completo e sono ancora tutti attivi lo segnalo e esco
		if len(listNeighbor) == const.NUM_NEIGHBOR:
			func.success("Lista vicini completa!")
		# Se invece dopo il controllo ho meno vicini del numero massimo mando a ogni vicino una richiesta di vicinato
		elif len(listNeighbor) > 0:
			for neighbor in listNeighbor:
				s = func.create_socket_client(func.roll_the_dice(neighbor[0]), neighbor[1]);
				if s is None:
					func.error("Mamma che sfiga, sto vicino è andato giù proprio ora.")
				else:
					s.sendall(pk)
					s.close()	
	
	# Alla fine gestisco la possibilità che tutti i vicini che avevo siano andati giù e quindi passo all'inserimento manuale.
	if len(listNeighbor) == 0: 		"""
	while True:
		print ("\n>>> SCELTA PEER VICINO")
		nGroup = input("Numero del gruppo: ")
		if nGroup is 0:
			break
		nElement = input("Numero dell'elemento del gruppo: ")
		if nElement is 0:
			break
		nPort = input("Inserire la porta su cui il vicino è in ascolto: ")
		if nPort is 0:
			break
		hostN = func.roll_the_dice("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
																"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
																"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
																":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))
		s = func.create_socket_client(hostN, nPort);
		if s is None:
			func.error("Errore nella scelta del primo peer vicino, scegline un altro.")
			break
		else:
			s.sendall(pk)
			s.close()
			break

def search(myHost, query, listNeighbor, listPkt):
	pk = pack.query(myHost, query)
	if len(listNeighbor) is 0:
		func.error("Nessun vicino presente, crea prima una rete virtuale")
	else:
		func.add_pktid(pk[4:20], listPkt)
		i = 0
		for x in listNeighbor:
			s = func.create_socket_client(func.roll_the_dice(x[0]), x[1]);
			if s is None:
				func.error("Peer non attivo: " + str(x[0], "ascii"))
			else:
				func.success("Peer attivo: " + str(x[0], "ascii"))
				s.sendall(pk)
				s.close()
				i = i + 1
		if i is 0:
			func.error("Nessun peer vicino attivo")
		else:
			print("\nScegli file da quelli disponibili (0 per uscire): \n")
			print("ID\tFILE\t\tIP\n")
			f = False
			while not f:
				try:
					print("\n")
					choose = int(input())
					if choose != 0:
						if choose <= len(listResultQuery):
							f = True
							func.remove_pktid(pk, listPkt)
							download(listResultQuery[choose - 1])
							del listResultQuery[:]
						else: 
							func.error("Spiacente, numero inserito non valido.")
					else:
						break
				except ValueError:
					func.error("Spiacente, inserisci un numero.")

			func.remove_pktid(pk, listPkt)
			del listResultQuery[:]

	

# Funzione di download
def download(selectFile):	
	print ("\n>>> DOWNLOAD")

	md5 = selectFile[1]
	nomeFile = selectFile[2].decode("ascii").strip()
	ip = selectFile[3]
	port = selectFile[4]

	# Con probabilità 0.5 invio su IPv4, else IPv6
	ip = func.roll_the_dice(ip.decode("ascii"))
	print("Connessione con:", ip)

	# Mi connetto al peer

	sP = func.create_socket_client(ip, port)
	if sP is None:
	    print ('Error: could not open socket in download')
	else:
		pk = pack.dl(md5)
		sP.sendall(pk)

		nChunk = int(sP.recv(const.LENGTH_HEADER)[4:10])
					
		ricevutoByte = b''

		i = 0
		
		while i != nChunk:
			ricevutoLen = sP.recv(const.LENGTH_NCHUNK)
			while (len(ricevutoLen) < const.LENGTH_NCHUNK):
				ricevutoLen = ricevutoLen + sP.recv(const.LENGTH_NCHUNK - len(ricevutoLen))
			buff = sP.recv(int(ricevutoLen))
			while(len(buff) < int(ricevutoLen)):
				buff = buff + sP.recv(int(ricevutoLen) - len(buff))
			ricevutoByte = ricevutoByte + buff
			i = i + 1

		sP.close()
		
		# Salvare il file data
		open((const.FILE_COND + nomeFile),'wb').write(ricevutoByte)
		print("File scaricato correttamente, apertura in corso...")
		try:
			os.system("open " + const.FILE_COND + nomeFile)
		except:
			try:
				os.system("start " + const.FILE_COND + nomeFile)
			except:
				print("Apertura non riuscita")

def logout(ip):
	print ("\n>>> LOGOUT")
	i = 0
	pk = pack.logout()
	s = func.create_socket_client(func.get_ipv4(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone:" + func.get_ipv4(ip))
	else:
		s.sendall(pk)
		s.close()
		i = i + 1
	s = func.create_socket_client(func.get_ipv6(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone:" + func.get_ipv6(ip))
	else:
		s.sendall(pk)
		s.close()
		i = i + 1
	if i is 2:
		print ("Logout eseguito con successo.")

####### VARIABILI 

listNeighbor = []	
listPkt = []
listResultQuery = []

####### INIZIO CLIENT #######
nGroup = input("Inserire il numero del gruppo: ")
nElement = input("Inserire il numero dell'elemento del gruppo: ")
host = ("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
				"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
				"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
				":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))

print ("IP:", host)

####### DEMONI

daemonThreadv4 = daemon.Daemon(func.get_ipv4(host), listNeighbor, listPkt, listResultQuery, host)
daemonThreadv6 = daemon.Daemon(func.get_ipv6(host), listNeighbor, listPkt, listResultQuery, host)
daemonThreadv4.setName("DAEMON IPV4")
daemonThreadv6.setName("DAEMON IPV6")
daemonThreadv4.start()	
daemonThreadv6.start()

# Menù di interazione
while True:
	choice = input("\n\nScegli azione:\nupdate\t - Update Neighborhood\ndelete\t - Delete Neighborhood\nview\t - View Neighborhood\nsearch\t - Search File\nquit\t - Quit\n\n")

	if (choice == "update" or choice == "u"):
		updateNeighbor(host, listNeighbor)

	elif (choice == "delete" or choice == "d"):
		del listNeighbor[:]

	elif (choice == "view" or choice == "v"):
		print ("\n>>> VIEW NEIGHBORHOOD")
		if len(listNeighbor) != 0:
			for n in listNeighbor:
				print(str(n[0], "ascii") + "\t" + str(n[1], "ascii"))
		else:
			print("Nessun vicino salvato")

	elif (choice == "search" or choice == "s"):
		print ("\n>>> RICERCA")
		query = input("\nInserisci il nome del file da cercare: ")
		while(len(query) > const.LENGTH_QUERY):
			func.error("Siamo spiacenti ma accettiamo massimo 20 caratteri.")
			query = input("\nInserisci il nome del file da cercare: ")
		search(host, query, listNeighbor, listPkt)

	elif (choice == "quit" or choice == "q"):
		logout(host)
		daemonThreadv4.join()
		daemonThreadv6.join()
		break

	else:
		func.error("Wrong Choice!")