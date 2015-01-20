#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk
import hashlib
import os

class App:

    def __init__(self):
        self.root = Tk()
        self.topframe = Frame(self.root)
        self.topframe.grid(row=0)

        self.root.protocol('WM_DELETE_WINDOW', self.handler)
        self.buttonframe = Frame(self.topframe)
        self.buttonframe.grid(row=0, sticky='w')
        self.button = Button(self.buttonframe, text='Open Image',
                             command=self.askopenfilename)
        self.button.grid(row=0, column=0, sticky='w')
        self.linebutton = Button(self.buttonframe, text='Line', command = self.setline, state = 'disabled')
        self.linebutton.grid(row=0, column=1, sticky = 'w')

        self.canvas = Canvas(self.topframe)
        self.canvas.grid(row=1)

        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'), ('image files',
                                '.jpg')]
        options['parent'] = self.root


        self.grabbed = False
        self.canvasrect = 0

        # file information
        self.fileinfo = []
        self.saveddir = ''

        try :
            f = open('lastdir.txt', 'r+')
            self.saveddir = f.read()
            f.close()

        except (IOError) :
            print 'No last directory file'

        if self.saveddir != '' :
            self.file_opt['initialdir'] = self.saveddir

    # image = Image.open(

    # w = Canvas(frame, width=200, height=100)

    def handler(self):
        self.root.quit()

    def askopenfilename(self):
        try:
            filename = tkFileDialog.askopenfilename(**self.file_opt)
            image = Image.open(filename)
            newpath = os.path.dirname(filename)
            self.fileinfo.append(carInfo(filename, hashlib.sha256(open(filename, 'rb').read()).digest()))
        except (AttributeError, IOError):

            return

        with open('lastdir.txt', 'w') as f:
            f.write(newpath)

        f.closed


    # print filename
    # image = Image.open(filename)

        scaled = False

    # get image dimensions

        imagew = image.size[0]
        imageh = image.size[1]

    # check screen size

        if imagew > self.root.winfo_screenwidth():

        # scale the image down

            scalefactor = float(self.root.winfo_screenwidth()) / imagew

        # print scalefactor

            imagew = int(imagew * scalefactor * .9)
            imageh = int(imageh * scalefactor * .9)
            scaled = True

        if imageh > self.root.winfo_screenheight():
            scalefactor = float(self.root.winfo_screenheight()) / imageh
            imagew = int(imagew * scalefactor * .9)
            imageh = int(imageh * scalefactor * .9)
            scaled = True

    # reset window - downsizes window if opening smaller image after large

        self.canvas.grid_forget()
        self.button.grid_forget()
        self.button.grid(row=0, column=0, sticky='w')

        self.rect = 0
        self.grabbed = False

        self.canvas = Canvas(self.topframe, width=imagew, height=imageh)
        self.canvas.bind('<ButtonPress-1>', self.callback)
        self.canvas.bind('<B1-Motion>', self.callbackmotion)
        self.canvas.bind('<ButtonRelease-1>', self.callbackrelease)
        self.canvas.grid(row=1)

        if scaled:
            image = image.resize((imagew, imageh), Image.ANTIALIAS)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        
    def setline(self):
        self.line = 0
        self.canvas.bind('<ButtonPress-1>', self.linestart)
        self.canvas.bind('<B1-Motion>', self.linemotion)
        self.canvas.bind('<ButtonRelease-1>', self.linerelease)
    
    def linestart(self, event):
        if self.line:
            self.canvas.delete(self.line)
        self.line = self.canvas.create_line(event.x, self.rectorigy, event.x, self.rectendy, fill = 'blue')
    
    def linemotion(self, event):
        self.canvas.delete(self.line)
        self.line = self.canvas.create_line(event.x, self.rectorigy, event.x, self.rectendy, fill = 'blue')
        
    def linerelease(self, event):
        self.canvas.delete(self.line)
        self.line = self.canvas.create_line(event.x, self.rectorigy, event.x, self.rectendy, fill = 'blue')

    def callback(self, event):
        if self.canvasrect:
            # check if we are grabbing and resizing the bounding rectangle
            self.grabbed = False
            for grab in self.grabs :
                if self.grabs[grab].inside(event.x, event.y):
                    print type(self.grabs[grab]), grab
                    self.grabbed = True
                    self.grabbing = (grab, self.grabs[grab])

            if not self.grabbed:
                self.canvas.delete(self.canvasrect)
                self.rectorigx = event.x
                self.rectorigy = event.y
                self.rect = GrabbableRectangle(event.x, event.y,
                    event.x + 1, event.y + 1)
                self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')

        else :
            self.rectorigx = event.x
            self.rectorigy = event.y

        # create initial rectangle

            self.rect = GrabbableRectangle(event.x, event.y,
                event.x + 1, event.y + 1)
            self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')

    def callbackmotion(self, event):
        if not self.grabbed:
            self.canvas.delete(self.canvasrect)
            self.rect = GrabbableRectangle(self.rectorigx, self.rectorigy,
                event.x, event.y)

            self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')

        # resize the rectangle
        else:
            if isinstance(self.grabbing[1], GrabHandle) :
                self.canvas.delete(self.canvasrect)
                self.rect.resizebycorner(self.grabbing, event.x, event.y)
                self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')
            elif isinstance(self.grabbing[1], GrabLine) :
                self.canvas.delete(self.canvasrect)
                self.rect.resizebyside(self.grabbing, event.x, event.y)
                self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')



    def callbackrelease(self, event):
        if not self.grabbed :
            self.canvas.delete(self.canvasrect)
            #self.rect = self.canvas.create_rectangle(self.rectorigx,
            #       self.rectorigy, event.x, event.y, outline='red')

            # this should all be moved to the file saving method
            if self.rectorigx > event.x :
                self.rectendx = self.rectorigx
                self.rectorigx = event.x
            else :
                self.rectendx = event.x
            if self.rectorigy > event.y:
                self.rectendy = self.rectorigy
                self.rectorigy = event.y
            else :
                self.rectendy = event.y
            self.rect = GrabbableRectangle(self.rectorigx, self.rectorigy, self.rectendx, self.rectendy)
            self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline = 'red')
            self.creategrabs()
            self.linebutton.config(state = 'active')

        else :
            # resize the rectangle
            if isinstance(self.grabbing[1], GrabHandle) :
                self.canvas.delete(self.canvasrect)
                self.rect.resizebycorner(self.grabbing, event.x, event.y)
                self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')
            elif isinstance(self.grabbing[1], GrabLine) :
                self.canvas.delete(self.canvasrect)
                self.rect.resizebyside(self.grabbing, event.x, event.y)
                self.canvasrect = self.canvas.create_rectangle(self.rect.bounds(), outline='red')

            self.grabs = self.rect.grabs



    def creategrabs(self):
        self.grabs = {}
        self.grabs['nw'] = GrabHandle(self.rectorigx, self.rectorigy)
        self.grabs['n'] = GrabLine(self.rectorigx, self.rectorigy, self.rectendx, self.rectorigy)
        self.grabs['ne'] = GrabHandle(self.rectendx, self.rectorigy)
        self.grabs['e'] = GrabLine(self.rectendx, self.rectorigy, self.rectendx, self.rectendy)
        self.grabs['se'] = GrabHandle(self.rectendx, self.rectendy)
        self.grabs['s' ] = GrabLine(self.rectorigx, self.rectendy, self.rectendx, self.rectendy)
        self.grabs['sw'] = GrabHandle(self.rectorigx, self.rectendy)
        self.grabs['w'] = GrabLine(self.rectorigx, self.rectorigy, self.rectorigx, self.rectendy)


class GrabHandle:

    def __init__(
        self,
        x1,
        y1,
        ):
        widthpix = 4
        self.x1 = x1 - widthpix
        self.y1 = y1 - widthpix
        self.x2 = x1 + widthpix
        self.y2 = y1 + widthpix

    def inside(self, x, y):
        return x < self.x2 and x > self.x1 and y < self.y2 and y > self.y1


class GrabLine:

    def __init__(
        self,
        x1,
        y1,
        x2,
        y2,
        ):
        widthpix = 4
        if x1 == x2:
            self.x1 = x1 - widthpix
            self.y1 = y1 + widthpix
            self.x2 = x2 + widthpix
            self.y2 = y2 - widthpix
        else:
            self.x1 = x1 + widthpix
            self.y1 = y1 - widthpix
            self.x2 = x2 - widthpix
            self.y2 = y2 + widthpix

    def inside(self, x, y):
        return x < self.x2 and x > self.x1 and y < self.y2 and y > self.y1


class GrabbableRectangle:

    def __init__(self, x1, y1, x2, y2):
        self.grabs = {}
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.creategrabs()

    def bounds(self):
        return (self.x1, self.y1, self.x2, self.y2)

    def creategrabs(self):
        self.grabs['nw'] = GrabHandle(self.x1, self.y1)
        self.grabs['n'] = GrabLine(self.x1, self.y1, self.x2, self.y1)
        self.grabs['ne'] = GrabHandle(self.x2, self.y1)
        self.grabs['e'] = GrabLine(self.x2, self.y1, self.x2, self.y2)
        self.grabs['se'] = GrabHandle(self.x2, self.y2)
        self.grabs['s' ] = GrabLine(self.x1, self.y2, self.x2, self.y2)
        self.grabs['sw'] = GrabHandle(self.x1, self.y2)
        self.grabs['w'] = GrabLine(self.x1, self.y1, self.x1, self.y2)

    def resizebycorner(self, corner, newx, newy):
        if corner[0] == 'nw':
            self.x1 = newx
            self.y1 = newy
        elif corner[0] == 'ne' :
            self.x2 = newx
            self.y1 = newy
        elif corner[0] == 'se' :
            self.x2 = newx
            self.y2 = newy
        elif corner[0] == 'sw' :
            self.x1 = newx
            self.y2 = newy

        self.creategrabs()

        return self.bounds()

    def resizebyside(self, side, newx, newy):
        if side[0] == 'n' :
            self.y1 = newy
        elif side[0] == 's' :
            self.y2 = newy
        elif side[0] == 'w' :
            self.x1 = newx
        elif side[0] == 'e' :
            self.x2 = newx

        self.creategrabs()
        return self.bounds()

class carInfo :

    def __init__(self, fname, fhash):
        self.filename = fname
        self.shahash = fhash
        self.points = []



def main():
    a = App()
    mainloop()


if __name__ == '__main__':
    main()
