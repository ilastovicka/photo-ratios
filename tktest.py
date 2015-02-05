#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk
import hashlib
import os
import csv
import binascii

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

        self.savebutton = Button(self.buttonframe, text='Save', command=self.save, state='disabled')
        self.savebutton.grid(row=0, column=2, sticky='w')

        self.canvas = Canvas(self.topframe)
        self.canvas.grid(row=1)

        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'), ('image files',
                                '.jpg')]
        options['parent'] = self.root

        self.grabbed = False
        self.canvasrect = 0

        self.lineid = 0

        # file information
        self.fileinfo = []
        self.saveddir = ''
        self.csvcols = []
        self.linebuttonvar = StringVar()
        self.linedict = {}
        self.labeldict = {}



        try :
            f = open('lastdir.txt', 'r+')
            self.saveddir = f.read()
            f.close()

        except (IOError) :
            print 'No last directory file'

        if self.saveddir != '' :
            self.file_opt['initialdir'] = self.saveddir

        # open previous csv coordinate file

        self.oldheader = []
        self.carhashes = []
        try :
            f = open('carinfo.csv', 'r')
            reader = csv.DictReader(f)
            for row in reader:
                self.oldheader = row.keys()
                self.carhashes.append(row['sha256'])
            f.close()
        except IOError:
            print 'No previous car info available'
        except KeyError:
            print 'Hash not available, car info file is in wrong format'

    # image = Image.open(

    # w = Canvas(frame, width=200, height=100)

    def handler(self):
        self.root.destroy()
        if self.buttonwindow:
            self.buttonwindow.destroy()

    def askopenfilename(self):
        try:
            filename = tkFileDialog.askopenfilename(**self.file_opt)
            image = Image.open(filename)
            newpath = os.path.dirname(filename)
            self.fileinfo.append(carInfo(os.path.basename(filename), binascii.hexlify(hashlib.sha256(open(filename, 'rb').read()).digest())))
        except (AttributeError, IOError):

            return

        with open('lastdir.txt', 'w') as f:
            f.write(newpath)

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

        with open('cargridlines.txt', 'r') as txtfile:
            for row in txtfile:
                self.csvcols.append(row.strip())

        self.linedict = dict.fromkeys(self.csvcols)

        self.buttoncolwidth = 9 * len(max(self.csvcols, key=len))

        self.buttonholder = []
        self.buttonwindow = Tk()
        sizex = self.buttoncolwidth
        sizey = 600
        posx  = 100
        posy  = 100
        self.buttonwindow.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))

        self.buttoncol = Frame(self.buttonwindow, width=100, height=600, bd=1)
        self.buttoncol.pack(fill='y', padx=5, pady=5)

        #self.buttoncol.grid(column=0, row=0, sticky='n')
        self.buttoncanvas = Canvas(self.buttoncol)
        buttonframe = Frame(self.buttoncanvas)
        myscrollbar = Scrollbar(self.buttoncol, orient='vertical', command=self.buttoncanvas.yview)
        self.buttoncanvas.configure(yscrollcommand=myscrollbar.set)

        myscrollbar.pack(side='right', fill='y')
        self.buttoncanvas.pack(side="left", fill='y')
        self.buttoncanvas.create_window((0,0),window=buttonframe, anchor='nw')
        self.linebuttonvar = StringVar(master=self.buttonwindow)
        self.linebuttonvar.set(self.csvcols[0])
        for n in range(len(self.csvcols)):
            self.buttonholder.append(Radiobutton(buttonframe,
                                            text=self.csvcols[n],
                                            variable=self.linebuttonvar,
                                            value=self.csvcols[n],
                                            indicatoron=0,
                                            command=self.setline,
                                            state='disabled'
                                            ))
            self.buttonholder[n].grid(column=0, row=n, sticky='w')

        buttonframe.bind("<Configure>",self.buttonscrollbarfunc)

    def buttonscrollbarfunc(self,event):
        self.buttoncanvas.configure(scrollregion=self.buttoncanvas.bbox("all"),width=self.buttoncolwidth,height=600)

    def setline(self):
        self.line = self.linedict[self.linebuttonvar.get()]
        self.canvas.bind('<ButtonPress-1>', self.linestart)
        self.canvas.bind('<B1-Motion>', self.linemotion)
        self.canvas.bind('<ButtonRelease-1>', self.linerelease)
    
    def linestart(self, event):
        if self.linedict[self.linebuttonvar.get()]:
            self.canvas.delete(self.linedict[self.linebuttonvar.get()])
        try:
            if self.labeldict[self.linebuttonvar.get()]:
                self.canvas.delete(self.labeldict[self.linebuttonvar.get()])
        except KeyError:
            pass

        if self.linebuttonvar.get()[-1] == 'h':
            if event.x > self.rect.x2:
                linex1 = self.rect.x2
                liney1 = self.rect.y1
                linex2 = self.rect.x2
                liney2 = self.rect.y2
            elif event.x < self.rect.x1:
                linex1 = self.rect.x1
                liney1 = self.rect.y1
                linex2 = self.rect.x1
                liney2 = self.rect.y2
            else:
                linex1 = event.x
                liney1 = self.rect.y1
                linex2 = event.x
                liney2 = self.rect.y2
        else:
            if event.y > self.rect.y2:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y2
            elif event.y < self.rect.y1:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y1
            else:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = event.y
        self.linedict[self.linebuttonvar.get()] = self.canvas.create_line(linex1, liney1, linex2, liney2, fill = 'blue')

    
    def linemotion(self, event):
        self.canvas.delete(self.linedict[self.linebuttonvar.get()])
        if self.linebuttonvar.get()[-1] == 'h':
            if event.x > self.rect.x2:
                linex1 = self.rect.x2
                liney1 = self.rect.y1
                linex2 = self.rect.x2
                liney2 = self.rect.y2
            elif event.x < self.rect.x1:
                linex1 = self.rect.x1
                liney1 = self.rect.y1
                linex2 = self.rect.x1
                liney2 = self.rect.y2
            else:
                linex1 = event.x
                liney1 = self.rect.y1
                linex2 = event.x
                liney2 = self.rect.y2
        else:
            if event.y > self.rect.y2:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y2
            elif event.y < self.rect.y1:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y1
            else:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = event.y
        self.linedict[self.linebuttonvar.get()] = self.canvas.create_line(linex1, liney1, linex2, liney2, fill = 'blue')
        
    def linerelease(self, event):
        self.canvas.delete(self.linedict[self.linebuttonvar.get()])
        if self.linebuttonvar.get()[-1] == 'h':
            if event.x > self.rect.x2:
                linex1 = self.rect.x2
                liney1 = self.rect.y1
                linex2 = self.rect.x2
                liney2 = self.rect.y2
            elif event.x < self.rect.x1:
                linex1 = self.rect.x1
                liney1 = self.rect.y1
                linex2 = self.rect.x1
                liney2 = self.rect.y2
            else:
                linex1 = event.x
                liney1 = self.rect.y1
                linex2 = event.x
                liney2 = self.rect.y2
            self.labeldict[self.linebuttonvar.get()] = self.canvas.create_text(linex1, liney1, anchor='s', text=self.linebuttonvar.get()[:-2])
        else:
            if event.y > self.rect.y2:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y2
            elif event.y < self.rect.y1:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = self.rect.y1
            else:
                linex1 = self.rect.x1
                linex2 = self.rect.x2
                liney1 = liney2 = event.y
            self.labeldict[self.linebuttonvar.get()] = self.canvas.create_text(linex1, liney1, anchor='sw', text=self.linebuttonvar.get()[:-2])
        self.linedict[self.linebuttonvar.get()] = self.canvas.create_line(linex1, liney1, linex2, liney2, fill = 'blue')




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
            self.savebutton.config(state = 'active')
            for button in self.buttonholder:
                button.config(state = 'normal')

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

    # save csv file
    def save(self):
        csvdata = {}
        # get all data for all lines in linedict
        for x in self.linedict:
            if self.linedict[x] :
                linecoords = self.canvas.coords(self.linedict[x])
                csvdata[x+'_x1'] = linecoords[0]
                csvdata[x+'_y1'] = linecoords[1]
                csvdata[x+'_x2'] = linecoords[2]
                csvdata[x+'_y2'] = linecoords[3]
            else:
                csvdata[x+'_x1'] = 0
                csvdata[x+'_y1'] = 0
                csvdata[x+'_x2'] = 0
                csvdata[x+'_y2'] = 0
        # add in bounding rectangle data
        csvdata['x1'] = self.rect.x1
        csvdata['y1'] = self.rect.y1
        csvdata['x2'] = self.rect.x2
        csvdata['y2'] = self.rect.y2
        # get the header for the csv file
        csvheader = csvdata.keys()
        csvheader.sort()
        csvheader.insert(0, 'filename')
        csvheader.insert(1, 'sha256')
        csvdata['filename'] = self.fileinfo[0].filename
        csvdata['sha256'] = self.fileinfo[0].shahash
        if self.oldheader:
            with open('carinfo.csv', 'a') as csvfile:
                csvwriter = csv.DictWriter(csvfile, fieldnames=csvheader)
                csvwriter.writerow(csvdata)

        else:
            with open('carinfo.csv', 'w') as csvfile:
                csvwriter = csv.DictWriter(csvfile, fieldnames=csvheader)
                csvwriter.writeheader()
                csvwriter.writerow(csvdata)



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
        id = 0
    ):
        self.id = id
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
