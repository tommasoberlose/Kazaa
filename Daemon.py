from threading import Thread
import time
import sys
import socket
import Constant as const
import Function as func
import Package as pack

class Daemon(Thread):

	# Inizializza il thread, prende in ingresso l'istanza e un valore su cui ciclare
	# Tutti i metodi di una classe prendono l'istanza come prima variabile in ingresso
	# __init__ è un metodo predefinito per creare il costruttore
	def __init__(self, host, listNeighbor, listPkt, listResultQuery, host46):
		# Costruttore
		Thread.__init__(self)
		self.host = host
		self.host46 = host46
		self.port = const.PORT
		self.listNeighbor = listNeighbor
		self.listPkt = listPkt
		self.listResultQuery = listResultQuery

	def run(self):
		# Creazione socket
		s = func.create_socket_server(self.host, self.port)

		if s is None:
			func.write_daemon_text(self.name, self.host, 'Error: Daemon could not open socket in upload.')

		else:
			#frame = ui.create_window(self.name)
			while 1:

				conn, addr = s.accept()
				ricevutoByte = conn.recv(const.LENGTH_PACK)
				print("\n")
				func.write_daemon_text(self.name, addr[0], str(ricevutoByte, "ascii"))
				
				if not ricevutoByte:
					func.write_daemon_error(self.name, addr[0], "Pacchetto errato")
					break
				elif (str(ricevutoByte[0:4], "ascii") == const.CODE_LOGO):
					break
				else:
					if str(ricevutoByte[0:4], "ascii") == const.CODE_ANSWER_QUERY:
						if func.check_query(ricevutoByte[4:20], self.listPkt):
							self.listResultQuery.append([len(self.listResultQuery), ricevutoByte[80:112], ricevutoByte[112:], ricevutoByte[20:75], ricevutoByte[75:80]])
							print(str(len(self.listResultQuery)) + "\t" + str(ricevutoByte[112:], "ascii").strip() + "\t" + str(ricevutoByte[20:75],"ascii"))
						else: 
							func.write_daemon_error(self.name, addr[0], "ANSWER QUERY - Ricerca conclusa")

					elif str(ricevutoByte[0:4], "ascii") == const.CODE_QUERY:
						func.write_daemon_text(self.name, addr[0], "QUERY - " + func.reformat_string(str(ricevutoByte[82:],"ascii")))
						if func.add_pktid(ricevutoByte[4:20], self.listPkt) is True:
							# Inoltro
							pk = pack.forward_query(ricevutoByte)
							func.forward(pk, addr[0], self.listNeighbor)

							# Rispondi
							listFileFounded = func.search_file(func.reformat_string(str(ricevutoByte[82:],"ascii")))
							if len(listFileFounded) != 0:
								for x in listFileFounded:
									pk = pack.answer_query(ricevutoByte[4:20], self.host46, x[0], x[1])
									sC = func.create_socket_client(func.roll_the_dice(ricevutoByte[20:75]), ricevutoByte[75:80])
									if sC != None:
										sC.sendall(pk)
										sC.close()
						else:
							func.write_daemon_error(self.name, addr[0], "Pacchetto già ricevuto")

					elif str(ricevutoByte[0:4], "ascii") == const.CODE_NEAR:
						if func.add_pktid(ricevutoByte[4:20], self.listPkt) is True:
							func.write_daemon_text(self.name, addr[0], "NEAR - Response request from" + str(ricevutoByte[20:75], "ascii"))
							# Inoltro
							pk = pack.forward_neighbor(ricevutoByte)
							func.forward(pk, addr[0], self.listNeighbor)

							# Response neighborhood
							pk = pack.answer_neighbor(ricevutoByte[4:20], self.host46)
							sC = func.create_socket_client(func.roll_the_dice(ricevutoByte[20:75]), ricevutoByte[75:80])
							if sC != None:
								sC.sendall(pk)
								sC.close()

							# Aggiungo anche io il Vicino
							if len(self.listNeighbor) < const.NUM_NEIGHBOR:
								if not [ricevutoByte[20:75], ricevutoByte[75:80]] in self.listNeighbor:
									self.listNeighbor.append([ricevutoByte[20:75], ricevutoByte[75:80]])
									func.write_daemon_success(self.name, addr[0], "NEAR - Added neighbor: " + str(ricevutoByte[20:75], "ascii"))
								else:
									func.write_daemon_error(self.name, addr[0], "NEAR - Vicino già presente")
							else:
								func.write_daemon_error(self.name, addr[0], "NEAR - Rete completa: neighbor " + str(ricevutoByte[20:75], "ascii") + " non aggiunto")
						else:
							func.write_daemon_error(self.name, addr[0], "NEAR -  Pacchetto già ricevuto")

					elif str(ricevutoByte[0:4], "ascii") == const.CODE_ANSWER_NEAR:
						if len(self.listNeighbor) < const.NUM_NEIGHBOR:
							if not [ricevutoByte[20:75], ricevutoByte[75:80]] in self.listNeighbor:
								func.write_daemon_success(self.name, addr[0], "ANSWER NEAR - Added neighbor: " + str(ricevutoByte[20:75], "ascii"))
								self.listNeighbor.append([ricevutoByte[20:75], ricevutoByte[75:80]])
							else:
								func.write_daemon_error(self.name, addr[0], "ANSWER NEAR - Vicino già presente")
						else:
							func.write_daemon_error(self.name, addr[0], "ANSWER NEAR - Rete completa: neighbor " + str(ricevutoByte[20:75], "ascii") + " non aggiunto")

					elif str(ricevutoByte[0:4], "ascii") == const.CODE_DOWNLOAD:
						func.write_daemon_text(self.name, addr[0], "UPLOAD")
						filef = func.find_file_by_md5(ricevutoByte[4:])
						if filef != const.ERROR_FILE:
							func.upload(filef, conn)
					else:
						func.write_daemon_error(self.name, addr[0], "Ricevuto pacchetto sbagliato: " + str(ricevutoByte, "ascii"))

			s.close()



