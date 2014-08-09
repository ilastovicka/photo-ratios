#!/usr/bin/python

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk

def callback(event):
    print "clicked at", event.x, event.y

def callbackrelease(event):
    print "released at", event.x, event.y
    
class App:

  def __init__(self, master):
    
    frame = Frame(master)
    frame.pack()


    
    self.button = Button(frame, text="Open Image", command=self.askopenfilename)
    self.button.pack()

    self.file_opt = options = {}
    options['filetypes'] = [('all files', '.*'), ('image files', '.jpg')]
    options['parent'] = root

    #image = Image.open(

    #w = Canvas(frame, width=200, height=100)
      
  def askopenfilename(self):
        
    filename = tkFileDialog.askopenfilename(**self.file_opt)
    #print filename
    image = Image.open(filename)
    scaled = False
    frame = Frame()
    frame.bind('<Button-1>', callback)
    frame.pack()
    #get image dimensions
    imagew = image.size[0]
    imageh = image.size[1]
    
    #check screen size
    if imagew > root.winfo_screenwidth() :
        #scale the image down
        scalefactor = float(root.winfo_screenwidth()) / imagew
        #print scalefactor
        imagew = int(imagew * scalefactor * .9)
        imageh = int(imageh * scalefactor * .9)
        scaled = True

    if imageh > root.winfo_screenheight() :
        scalefactor = float(root.winfo_screenheight())/ imageh
        imagew = int(imagew * scalefactor * .9)
        imageh = int(imageh * scalefactor * .9)
        scaled = True
        
    self.canvas = Canvas(frame, width = imagew, height = imageh)
    self.canvas.bind('<ButtonPress-1>', callback)
    self.canvas.bind('<ButtonRelease-1>', callbackrelease)
    self.canvas.pack()

    if scaled :
        image = image.resize((imagew, imageh), Image.ANTIALIAS)
    
    self.photo = ImageTk.PhotoImage(image)
    self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
    
def handler():
  root.quit()
  
root = Tk()

root.protocol("WM_DELETE_WINDOW", handler)

app = App(root)

root.mainloop()
root.destroy()
