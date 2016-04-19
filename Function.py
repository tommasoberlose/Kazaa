import string
import random
import socket
import shutil
import os
import sys
import hashlib
import time
import Constant as const
import Function as func
import Package as pack

####### STRINGHE

# Format string completa text con char per ottenere una stringa di lunghezza length
# Tested, fondamentale che il text passato sia stringa e la length un numero.
def format_string(text, length, char):
	l = len(text)
	dif = length - l
	return char * dif + text 

def reformat_string(text):
	return text.strip()

def	write_right_text(text):
	print("")
	print(str(text).rjust(shutil.get_terminal_size((80, 20))[0]))

def write_daemon_error(host, addr, text):
	write_right_text(">>> " + host + " [" + addr + "]: " + const.START_RED + "ERROR: " + text + const.END_RED)

def write_daemon_success(host, addr, text):
	write_right_text(">>> " + host + " [" + addr + "]: " + const.START_GREEN + "SUCCESS: " + text + const.END_GREEN)

def write_daemon_text(host, addr, text):
	write_right_text(">>>  " + host + " [" + addr + "]: " + text)

def error(text):
	print (const.START_RED + "Error: " + text + const.END_RED)

def success(text):
	print (const.START_GREEN + "Success: " + text + const.END_GREEN)

def warning(text):
	print (const.START_YELLOW + text + const.END_YELLOW)

def gtext(text):
	print (const.START_GREY + text + const.END_GREY)

# Random Functions
def random_pktid(length):
   return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length))

def random_sessionID(length):
   return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length))

def writeHelp():
	func.warning("\nPOSSIBILI ARGOMENTI:")
	print("Super Nodo\t-sn")
	print("Set Default Ip\t-ip group identifier")
	print("Change Port\t-p port")
	print("Change Port SN\t-pSN port")
	print("Change time\t-t time")
	print("Change ttl\t-ttl ttl")
	print("")
	sys.exit(-1)

####### SOCKET

def create_socket_server(myHost, port):
	s = None
	for res in socket.getaddrinfo(None, int(port), socket.AF_UNSPEC,socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
	    af, socktype, proto, canonname, sa = res
	    try:
	    	s = socket.socket(af, socktype, proto)
	    except socket.error as msg:
	    	s = None
	    	continue
	    try:
	    	s.bind(sa)
	    	s.listen(10)
	    except socket.error as msg:
	    	s.close()
	    	s = None
	    	continue
	    break
	return s

def create_socket_client(myHost, port):
	s = None
	for res in socket.getaddrinfo(myHost, int(port), socket.AF_UNSPEC, socket.SOCK_STREAM):
	    af, socktype, proto, canonname, sa = res
	    try:
	        s = socket.socket(af, socktype, proto)
	    except socket.error as msg:
	        s = None
	        continue
	    try:
	        s.connect(sa)
	    except socket.error as msg:
	        s.close()
	        s = None
	        continue
	    break
	return s

def forward(pk, addr, l): # Non andrebbe fatto generico?
	if pk != bytes(const.ERROR_PKT, "ascii"):
		for x in l:
			if addr != x[0]:
				s = func.create_socket_client(func.roll_the_dice(x[0]), x[1])
				if not(s is None):
					s.sendall(pk)
					s.close()

###### IP

def roll_the_dice(ip):
	return random.choice([ip[0:15], ip[16:55]])

def get_ipv4(ip):
	return ip[0:15]

def get_ipv6(ip):
	return ip[16:55]


###### SEARCH FILE

#funzione di ricerca file all'interno della cartella FileCondivisi
def search_file(query): # Da modificare, la ricerca va fatta sui file miei ma anche dei miei peer
	file_list = []
	file_found_list = []
	file_list = os.listdir(const.FILE_COND)
	check = 0
	for file in file_list:
		# Ricerca match nel nome
		if file.lower().find(query.lower()) == 0:
			if not file.endswith('~'):
				check = 1
				md5File = hashlib.md5(open(const.FILE_COND + file,'rb').read()).hexdigest()
				file_found = [md5File, file]
				file_found_list.append(file_found)
	#if check == 0:
		#func.error("File not exists")

	#print(file_found_list)
	return file_found_list

def add_pktid(pktid, list_pkt):
	list_pkt = clear_pktid(list_pkt)
	for lista in list_pkt:
		if pktid == lista[0]:
			return False
	pkTime = time.time() * 1000
	add_list = [pktid, pkTime]
	list_pkt.append(add_list)
	return True

def clear_pktid(list_pkt):
	x = 0
	for i in list_pkt:
		pkTime = i[1]
		nowtime = time.time() * 1000
		diff = nowtime - pkTime
		if diff >= const.MAX_TIME:
			del list_pkt[x]
			x -= 1
		x += 1
	return list_pkt

def check_query(pktid, list_pkt):
	list_pkt = clear_pktid(list_pkt)
	for lista in list_pkt:
		if pktid == lista[0]:
			return True
	return False

def check_sn(pktid, list_pkt):
	list_pkt = clear_pktid(list_pkt)
	for lista in list_pkt:
		if pktid == lista[0]:
			return True
	return False

def remove_pktid(pktid, list_pkt):
	i = 0
	for lista in list_pkt:
		if pktid == lista[0]:
			del list_pkt[i]
			i -= 1
		i += 1


###### UPLOAD FILE 

def upload(nomeFile, ss):
	f = open((const.FILE_COND + nomeFile), 'rb')

	fileLength = os.stat(const.FILE_COND + nomeFile).st_size
	nChunk = int(fileLength / const.LENGTH_PACK) + 1 

	nChunk = format_string(str(nChunk), const.LENGTH_NCHUNKS, "0")
	pk = bytes(const.CODE_ANSWER_DOWNLOAD, "ascii") + bytes(nChunk, "ascii")
	ss.sendall(pk)

	i = 0
	while True:
		line = f.read(const.LENGTH_PACK)
		dimLine = format_string(str(len(line)), const.LENGTH_NCHUNK, "0")
		pk = bytes(dimLine, "ascii") + line
		ss.sendall(pk)
		#print(pack)
		i = i + 1
		if i == int(nChunk):
			break

def find_file_by_md5(md5):
	file_list = os.listdir(const.FILE_COND)
	for filef in file_list:
		if not filef.endswith('~'):
			md5File = hashlib.md5(open(const.FILE_COND + filef,'rb').read()).hexdigest()
			if str(md5, "ascii") == md5File:
				return filef
	return const.ERROR_FILE


###### DOWNLOAD FILE

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

# Scelta random tra Supernodi

def choose_SN(sn_network):
	choose = random.sample(sn_network, 1)
	choose = choose[0]
	for n in sn_network:
		if not n == choose:
			del n
	return choose


####### USERS
def countUserFile(sessionID, listFiles):
	i = 0
	for f in listFiles:
		if f[2] == sessionID:
			i += 1
	return i

def isUserLogged(sessionID, listUsers):
	for user in listUsers:
		if sessionID == user[2]:
			return True
	return False

def reconnect_user(ip, listUsers):
	pk = const.ERROR_PKT
	for user in listUsers:
		if user[0] == ip:
			pk = pack.answer_login()[:4] + user[2]
			break
	return pk

def check_file(listFiles, ricevutoByte):
	fileConfronto = [ricevutoByte[20:52], ricevutoByte[52:152], ricevutoByte[4:20]]
	for file in listFiles:
		if (file[0] == fileConfronto[0]) and (file[2] == fileConfronto[2]):
			return False
	return True

def send_afin(conn, listResultQuery):
	print(listResultQuery)
	print(len(listResultQuery))
	if len(listResultQuery) != 0:
		listaMd5 = []

		while len(listResultQuery) != 0:
			listaCopie = []
			listaCopie = listResultQuery[0][1:]
			listaMd5.append(listaCopie)
			md5 = listResultQuery[0][1]
			del listResultQuery[0]
			
			count = 0
			for i in listResultQuery:
				if md5 == i[1]:
					listaMd5.append(i[1:])
					del listaMd5[count]
					count -= 1
				count += 1

		pk = bytes(const.CODE_ANSWER_SEARCH, "ascii") + bytes(func.format_string(len(listaMd5), const.LENGTH_NIDMD5, "0"), "ascii")

		for i in listaMd5:
			pk = pk + bytes(i[0][0], "ascii") + bytes(i[0][1], "ascii") + bytes(func.format_string(len(i), const.LENGTH_NCOPY, "0"), "ascii")
			for j in i:
				pk = pk + bytes(j[2:], "ascii") 

	else:
		pk = bytes(const.CODE_ANSWER_SEARCH, "ascii") + bytes("0" * const.LENGTH_NIDMD5, "ascii")  

	print(pk)
	conn.sendall(pk)







