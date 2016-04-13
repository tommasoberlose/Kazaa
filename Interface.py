from tkinter import *



def update_text(label, msg):
	def update():
		tx = ""
		for t in msg:
			tx += "\n" + t
		label.config(textvariable=tx)
		label.after(1000, update)
	update()

def create_window(title, msg):

	# Prepara la finestra
	cima = Tk()
	F = Frame(cima)
	F.pack()

	# Rinomina la finestra
	F.master.title(title)

	lCiao = Label(F,  
		justify=LEFT,
        compound = LEFT,
        padx = 10,
        text = "msg")
	lCiao.pack(side = "left")

	#update_text(lCiao, msg)

	# Attiva il ciclo
	cima.mainloop()

