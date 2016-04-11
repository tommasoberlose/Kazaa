PORT = "3000"
PORT_SN = "80"
LENGTH_PORT = 5

LENGTH_ITEM_REMOVED = 3

TTL = "2"
TTL_SN = "4"
LENGTH_TTL = 2

ERROR_PKT = "0000"
LIST_PKT = []
LENGTH_PKTID = 16

LENGTH_SESSIONID = 16

ERROR_LOG = "0" * LENGTH_SESSIONID

LENGTH_FILENAME = 100

LENGTH_QUERY = 20

LENGTH_SECTION_IPV4 = 3
LENGTH_SECTION_IPV6 = 4

LENGTH_PACK = 1024
LENGTH_NCHUNK = 5
LENGTH_NCHUNKS = 6

LENGTH_HEADER = 10

CODE_QUERY = "QUER"
CODE_ANSWER_QUERY = "AQUE"

CODE_SEARCH = "FIND"
CODE_ANSWER_SEARCH = "AFIN"

CODE_NEAR = "NEAR"
CODE_ANSWER_NEAR = "ANEA"

CODE_DOWNLOAD = "RETR"
CODE_ANSWER_DOWNLOAD = "ARET"

CODE_SN = "SUPE"
CODE_ANSWER_SN = "ASUP"

CODE_LOGIN = "LOGI"
CODE_ANSWER_LOGIN = "ALGI"

CODE_ADDFILE = "ADFF"
CODE_REMOVEFILE = "DEFF"

CODE_LOGOUT = "LOGO"
CODE_ANSWER_LOGOUT = "ALGO"

CODE_CLOSE = "QUIT"

FILE_COND = "FileCondivisi/"
ERROR_FILE = "FILE_NOT_FOUND"

NUM_NEIGHBOR = 3

START_RED = "\033[91m"
END_RED = "\033[0m"

START_GREEN = "\033[92m"
END_GREEN = "\033[0m"