#!/usr/bin/python

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk

def callback(event):
    print "clicked at", event.x, event.y

def callbackrelease(event):
    print "released at", event.x, event.y
    
class App:

  def __init__(self):
    self.root = Tk()
    self.topframe = Frame(self.root)
    self.topframe.grid(row=0)

    self.root.protocol("WM_DELETE_WINDOW", self.handler)
    
    self.button = Button(self.topframe, text="Open Image", command=self.askopenfilename)
    self.button.grid(row=0, column=0, sticky = 'w')

    self.canvas = Canvas(self.topframe)
    self.canvas.grid(row=1)

    self.file_opt = options = {}
    options['filetypes'] = [('all files', '.*'), ('image files', '.jpg')]
    options['parent'] = root

    #image = Image.open(

    #w = Canvas(frame, width=200, height=100)
    
  def handler(self):
    self.root.quit()
  
  def askopenfilename(self):
        
    filename = tkFileDialog.askopenfilename(**self.file_opt)
    #print filename
    image = Image.open(filename)
    scaled = False
    
    #get image dimensions
    imagew = image.size[0]
    imageh = image.size[1]
    
    #check screen size
    if imagew > self.root.winfo_screenwidth() :
        #scale the image down
        scalefactor = float(self.root.winfo_screenwidth()) / imagew
        #print scalefactor
        imagew = int(imagew * scalefactor * .9)
        imageh = int(imageh * scalefactor * .9)
        scaled = True

    if imageh > self.root.winfo_screenheight() :
        scalefactor = float(self.root.winfo_screenheight())/ imageh
        imagew = int(imagew * scalefactor * .9)
        imageh = int(imageh * scalefactor * .9)
        scaled = True
        
    self.canvas = Canvas(self.topframe, width = imagew, height = imageh)
    self.canvas.bind('<ButtonPress-1>', callback)
    self.canvas.bind('<ButtonRelease-1>', callbackrelease)
    self.canvas.grid(row=1)

    if scaled :
        image = image.resize((imagew, imageh), Image.ANTIALIAS)
    
    self.photo = ImageTk.PhotoImage(image)
    self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
    

def main():
    a = App()
    mainloop()

if __name__ == '__main__':
    main()
