#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk


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

    # image = Image.open(

    # w = Canvas(frame, width=200, height=100)

    def handler(self):
        self.root.quit()

    def askopenfilename(self):
        try:
            filename = tkFileDialog.askopenfilename(**self.file_opt)
            image = Image.open(filename)
        except (AttributeError, IOError):

            return

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
        if self.rect:
            self.grabbed = False
            for grab in self.grabs :
                if self.grabs[grab].inside(event.x, event.y):
                    print type(self.grabs[grab]), grab
                    self.grabbed = True
            if not self.grabbed:
                self.canvas.delete(self.rect)
        if not self.grabbed:
            self.rectorigx = event.x
            self.rectorigy = event.y
        
        #else :
            

     # create initial rectangle

            self.rect = self.canvas.create_rectangle(event.x, event.y,
                event.x + 1, event.y + 1, outline='red')

    def callbackmotion(self, event):
        if not self.grabbed:
            self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(self.rectorigx,
                    self.rectorigy, event.x, event.y, outline='red')

    def callbackrelease(self, event):
        if not self.grabbed:
            self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(self.rectorigx,
                    self.rectorigy, event.x, event.y, outline='red')
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
            self.creategrabs()
            self.linebutton.config(state = 'active')

    def creategrabs(self):
        self.grabs = {}
        self.grabs['nw'] = grabhandle(self.rectorigx, self.rectorigy)
        self.grabs['n'] = grabline(self.rectorigx, self.rectorigy, self.rectendx, self.rectorigy)
        self.grabs['ne'] = grabhandle(self.rectendx, self.rectorigy)
        self.grabs['e'] = grabline(self.rectendx, self.rectorigy, self.rectendx, self.rectendy)
        self.grabs['se'] = grabhandle(self.rectendx, self.rectendy)
        self.grabs['s' ] = grabline(self.rectorigx, self.rectendy, self.rectendx, self.rectendy)
        self.grabs['sw'] = grabhandle(self.rectorigx, self.rectendy)
        self.grabs['w'] = grabline(self.rectorigx, self.rectorigy, self.rectorigx, self.rectendy)


class grabhandle:

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


class grabline(grabhandle):

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


def main():
    a = App()
    mainloop()


if __name__ == '__main__':
    main()
