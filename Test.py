import Function as func
import Package as pack
import Constant as const
import hashlib
import sys
import Interface as ui
from threading import Thread
import threading
from tkinter import *


class BackgroundUI(Thread):   
	def __init__(self, msg):
		Thread.__init__(self)
		self.msg = msg

	def run(self):
		ui.create_window("Thread 1", self.msg)

print("ok1")
msg = ""
timer = BackgroundUI(msg)
timer.start()



