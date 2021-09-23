## texteditor: https://www.codespeedy.com/create-a-text-editor-in-python/
## menubar: https://stackoverflow.com/questions/36415606/adding-a-menu-inside-of-a-menubutton-python
## comport selected: https://stackoverflow.com/questions/65528065/dynamic-menu-tabs-tkinter-serialport-selection
## window frame: https://stackoverflow.com/questions/40764168/resize-parts-of-a-python-tkinter-grid
## syntax color: https://www.youtube.com/watch?v=WgI_j1utXFM
## line number: https://python-forum.io/thread-33314.html
## line number: https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
## subprocess realtime output: https://www.endpoint.com/blog/2015/01/getting-realtime-output-using-python/
## serialTerminal: https://github.com/pyserial/pyserial/blob/master/examples/wxTerminal.py
## avrdude.conf: https://www.instructables.com/Program-8051-With-Arduino/
## remove the newline at the end of the Text widget: https://stackoverflow.com/questions/48220788/how-can-i-remove-newline-character-n-at-the-end-of-text-widget
## program settings file: https://stackoverflow.com/questions/64179035/creating-and-using-a-preferences-file-in-python
## non-blocking reading from stdout: https://gist.github.com/mckaydavis/e96c1637d02bcf8a78e7

# Importing Required libraries & Modules
from tkinter import *
from tkinter import font
#from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import serial
import serial.tools.list_ports
import subprocess
#import threading
#import queue
#import time
import os
import select
import TKlighter
#import fcntl
import json
import platform

CONFIG_FILE='simple51ide_config.json'

class TextLineNumbers(Canvas):
  def __init__(self, *args, **kwargs):
    Canvas.__init__(self, *args, **kwargs)
    self.textwidget = None

  def attach(self, text_widget):
    self.textwidget = text_widget
        
  def redraw(self, *args):
    '''redraw line numbers'''
    self.delete("all")

    i = self.textwidget.index("@0,0")
    while True :
      dline= self.textwidget.dlineinfo(i)
      if dline is None: break
      y = dline[1]
      linenum = str(i).split(".")[0]
      self.create_text(2,y,anchor="nw", text=linenum)
      i = self.textwidget.index("%s+1line" % i)
    self.configure(width=(len(str(self.textwidget.index(END)))-2)*font.Font(family="Courier", size=15, weight="normal").measure("m"))
    
class CustomText(Text):
  def __init__(self, *args, **kwargs):
    Text.__init__(self, *args, **kwargs)

    # create a proxy for the underlying widget
    self._orig = self._w + "_orig"
    self.tk.call("rename", self._w, self._orig)
    self.tk.createcommand(self._w, self._proxy)
    
  def _proxy(self, *args):
    ## https://stackoverflow.com/questions/65228477/text-doesnt-contain-any-characters-tagged-with-sel-tkinter
    if args[0] == 'get' and (args[1] == 'sel.first' and args[2] == 'sel.last') and not self.tag_ranges('sel'): return
    if args[0] == 'delete' and (args[1] == 'sel.first' and args[2] == 'sel.last') and not self.tag_ranges('sel'): return
    #print(args[0])
    
    # let the actual widget perform the requested action
    cmd = (self._orig,) + args
    result = self.tk.call(cmd)


    # generate an event if something was added or deleted,
    # or the cursor position changed
    if (args[0] in ("insert", "replace", "delete") or 
      args[0:3] == ("mark", "set", "insert") or
      args[0:2] == ("xview", "moveto") or
      args[0:2] == ("xview", "scroll") or
      args[0:2] == ("yview", "moveto") or
      args[0:2] == ("yview", "scroll")
    ):
      self.event_generate("<<Change>>", when="tail")



    # return what the actual widget returned
    return result

# Defining TextEditor Class
class TextEditor:

  # Defining Constructor
  def __init__(self,root):




    # Assigning root
    self.root = root
    # Title of the window
    self.root.title("Simple 51 IDE")
    # Window Geometry
    self.root.geometry("1024x640+200+150")
    # Initializing filename
    self.filename = None
    # Declaring Title variable
    self.title = StringVar()
    # Declaring Status variable
    self.status = StringVar()

    # Creating Titlebar
    self.titlebar = Label(self.root,textvariable=self.title,font=("Courier",15,"bold"),bd=2,relief=GROOVE)
    # Packing Titlebar to root window
    self.titlebar.pack(side=TOP,fill=BOTH)
    # Calling Settitle Function
    self.settitle()

    # Creating Statusbar
    self.statusbar = Label(self.root,textvariable=self.status,font=("Courier",15,"bold"),bd=2,relief=GROOVE)
    # Packing status bar to root window
    self.statusbar.pack(side=BOTTOM,fill=BOTH)
    # Initializing Status
    self.status.set("")

    # Creating Menubar
    self.menubar = Menu(self.root,font=("Courier",15,"bold"),activebackground="skyblue")
    # Configuring menubar on root window
    self.root.config(menu=self.menubar)

    # Creating File Menu
    self.filemenu = Menu(self.menubar,font=("Courier",12,"bold"),activebackground="skyblue",tearoff=0)
    # Adding New file Command
    self.filemenu.add_command(label="New",accelerator="Ctrl+N",command=self.newfile)
    # Adding Open file Command
    self.filemenu.add_command(label="Open",accelerator="Ctrl+O",command=self.openfile)
    # Adding Save File Command
    self.filemenu.add_command(label="Save",accelerator="Ctrl+S",command=self.savefile)
    # Adding Save As file Command
    self.filemenu.add_command(label="Save As",command=self.saveasfile)
    # Adding Seprator
    self.filemenu.add_separator()
    # Adding Exit window Command
    self.filemenu.add_command(label="Exit",accelerator="Ctrl+E",command=self.exit)
    # Cascading filemenu to menubar
    self.menubar.add_cascade(label="File", menu=self.filemenu)

    # Creating Edit Menu
    self.editmenu = Menu(self.menubar,font=("Courier",12,"bold"),activebackground="skyblue",tearoff=0)
    # Adding Cut text Command
    self.editmenu.add_command(label="Cut",accelerator="Ctrl+X",command=self.cut)
    # Adding Copy text Command
    self.editmenu.add_command(label="Copy",accelerator="Ctrl+C",command=self.copy)
    # Adding Paste text command
    self.editmenu.add_command(label="Paste",accelerator="Ctrl+V",command=self.paste)
    # Adding Seprator
    self.editmenu.add_separator()
    # Adding Undo text Command
    self.editmenu.add_command(label="Undo",accelerator="Ctrl+U",command=self.undo)
    # Cascading editmenu to menubar
    self.menubar.add_cascade(label="Edit", menu=self.editmenu)

    
    self.menu8051 = Menu(self.menubar,font=("Courier",12,"bold"),activebackground="skyblue",tearoff=0)
    #
    self.comPortsMenu = Menu(self.menu8051, tearoff=0)
    self.menu8051.add_cascade(label="ComPort",menu=self.comPortsMenu)
#    self.menu8051.add_cascade(label="ComPort",menu=self.menu8051)
    portList = self.getPorts()
    for i in range(len(portList)):
    #    #pass a parameter with lambda
    #    Tool_portSub.add_command(label=str(portList[i]),command=lambda: selectPort(str(portList[i])))
      self.port = portList[i]
      self.comPortsMenu.add_command(label=self.port,command=lambda port=self.port: self.selectPort(port))
    #
    self.menu8051.add_command(label="sdcc",command=self.pickup_sdcc)
    self.menu8051.add_command(label="avrdude",command=self.pickup_avrdude)    
    self.menu8051.add_command(label="Build",accelerator="Ctrl+B",command=self.build)
    self.menu8051.add_command(label="Build & Upload",accelerator="Ctrl+P",command=self.upload)
    self.menu8051.add_command(label="SerialTerminal",accelerator="Ctrl+T",command=self.terminal)
    self.menu8051.add_command(label="SerialPlotter",accelerator="Ctrl+L",command=self.plotter)
    self.menubar.add_cascade(label="8051", menu=self.menu8051)

    # Creating Help Menu
    self.helpmenu = Menu(self.menubar,font=("Courier",12,"bold"),activebackground="skyblue",tearoff=0)
    # Adding About Command
    self.helpmenu.add_command(label="About",command=self.infoabout)
    # Cascading helpmenu to menubar
    self.menubar.add_cascade(label="Help", menu=self.helpmenu)

    
    framesWindow = PanedWindow(bg='lightgray',orient="vertical",sashwidth=20,relief=GROOVE)
    frame_top = Frame(framesWindow);
    frame_bottom = Frame(framesWindow);
    
    # coding area
    self.txtarea = CustomText(frame_top)
    self.vsb = Scrollbar(frame_top, orient="vertical", command=self.txtarea.yview)
    self.txtarea.configure(yscrollcommand=self.vsb.set)
    self.txtarea.configure(font=("Courier", "15", ""))
    self.txtarea.configure(state="normal",relief=GROOVE)
    self.txtarea.configure(insertbackground='black',fg='black',bg='white')
    #self.txtarea.tag_configure("", font=("Courier", "15", ""))
    self.linenumbers = TextLineNumbers(frame_top)
    self.linenumbers.attach(self.txtarea)

    self.vsb.pack(side="right", fill="y")
    self.linenumbers.pack(side="left", fill="y")
    self.txtarea.pack(side="right", fill="both", expand=True)

    self.txtarea.bind("<<Change>>", self._on_change)
    self.txtarea.bind("<Configure>", self._on_change)
    
    self.txtarea.pack(side=TOP, fill=BOTH, expand=True)
        
    # shell output area
    scrol_y = Scrollbar(frame_bottom,orient=VERTICAL)
    self.outputarea = Text(frame_bottom,yscrollcommand=scrol_y.set,fg="white",bg='black',font=("Courier",15,""),state="disabled",relief=GROOVE)
    scrol_y.pack(side=RIGHT,fill=Y)
    scrol_y.config(command=self.outputarea.yview)
    self.outputarea.pack(side=BOTTOM, fill=BOTH, expand=True)
    frame_bottom.pack()
    
    framesWindow.add(frame_top)
    framesWindow.add(frame_bottom)

    framesWindow.pack(expand=True, fill=BOTH)
    # Calling shortcuts funtion
    self.shortcuts()
    self.outputarea.configure(state='normal')
    self.outputarea.insert(END,"Welcome.\n")
    self.outputarea.configure(state='disabled')
    
    self.txtarea.bind_all('<KeyRelease>', self.light)
    self.txtarea.bind_all('<<KeyRelease>>', self.light)
    
    self.portDeviceName = "comport"
    
    # read program prefernce
    self.prevFileName = None
    try:
        JSON_FILE = open(CONFIG_FILE,'r+').read()
        JSON_DATA = json.loads(JSON_FILE)
        # prev file neme
        try:
            self.prevFileName = JSON_DATA["prevFileName"]
            print(self.prevFileName)
            self.filename = self.prevFileName
            self.openfile(self.filename)
        except:
            pass
        # port device name
        try:
            self.portDeviceName = JSON_DATA["portDeviceName"]
            self.menu8051.entryconfig(0,label="ComPort: "+self.portDeviceName)            
        except:
            pass
        # sdcc path
        try:
            self.sdccPath = JSON_DATA["sdccPath"]
            self.menu8051.entryconfig(1,label="sdcc: "+self.sdccPath)            
        except:
            pass
        # avrdude path
        try:
            self.avrdudePath = JSON_DATA["avrdudePath"]
            self.menu8051.entryconfig(2,label="avrdude: "+self.avrdudePath)            
        except:
            pass
    except FileNotFoundError:
        JSON_FILE = open(CONFIG_FILE,'w')
        JSON_DUMP = json.dumps({"prevFileName":"","portDeviceName":""})
        JSON_FILE.write(JSON_DUMP)
    #
    #
    self.txtarea.focus_set()
  def _on_change(self, event):
    self.linenumbers.redraw()
    self.txtarea.focus_set() # FIXME not working
    
  def getPorts(self):
    return list(serial.tools.list_ports.comports())

  def selectPort(self, port):
    self.menu8051.entryconfig(0,label="ComPort: "+str(port))
    self.portDeviceName = port.name
    # write the prev file name
    JSON_FILE = open(CONFIG_FILE,'r+').read()
    JSON_DATA = json.loads(JSON_FILE)
    JSON_DATA["portDeviceName"] = self.portDeviceName
    JSON_DUMP = json.dumps(JSON_DATA)
    JSON_FILE = open(CONFIG_FILE,'w')
    JSON_FILE.write(JSON_DUMP)
    #
    print(port.name)
        #do port selection

  def light(self, event):
    #print(event)
    if event == None:
      return
    if event.keysym:
      if event.keysym == "Up" or event.keysym == "Down" or event.keysym == "Left" or event.keysym == "Right":
        return
    
    control_color = 'orange'
    type_color = 'blue'
    storage_color = 'yellow'
    modify_color = 'magenta'
    TKlighter.custom_h(self.txtarea,'auto',storage_color)
    TKlighter.custom_h(self.txtarea,'break',control_color)
    TKlighter.custom_h(self.txtarea,'case',control_color)
    TKlighter.custom_h(self.txtarea,'char',type_color)
    TKlighter.custom_h(self.txtarea,'const',modify_color)
    TKlighter.custom_h(self.txtarea,'continue',control_color)
    TKlighter.custom_h(self.txtarea,'default',control_color)
    TKlighter.custom_h(self.txtarea,'do',control_color)
    TKlighter.custom_h(self.txtarea,'double',type_color)
    TKlighter.custom_h(self.txtarea,'else',control_color)
    TKlighter.custom_h(self.txtarea,'enum',type_color)
    TKlighter.custom_h(self.txtarea,'extern',storage_color)

    TKlighter.custom_h(self.txtarea,'float',type_color)
    TKlighter.custom_h(self.txtarea,'for',control_color)
    TKlighter.custom_h(self.txtarea,'goto','red')
    TKlighter.custom_h(self.txtarea,'if',control_color)
    TKlighter.custom_h(self.txtarea,'inline',modify_color)
    TKlighter.custom_h(self.txtarea,'int',type_color)
    TKlighter.custom_h(self.txtarea,'long',type_color)
    TKlighter.custom_h(self.txtarea,'register',storage_color)
    TKlighter.custom_h(self.txtarea,'restrict',modify_color)
    TKlighter.custom_h(self.txtarea,'return',control_color)
    TKlighter.custom_h(self.txtarea,'short',type_color)

    TKlighter.custom_h(self.txtarea,'signed',type_color)
    TKlighter.custom_h(self.txtarea,'sizeof','red')
    TKlighter.custom_h(self.txtarea,'static',storage_color)
    TKlighter.custom_h(self.txtarea,'struct',type_color)
    TKlighter.custom_h(self.txtarea,'switch',control_color)
    TKlighter.custom_h(self.txtarea,'typedef',type_color)
    TKlighter.custom_h(self.txtarea,'union',type_color)
    TKlighter.custom_h(self.txtarea,'unsigned',modify_color)
    TKlighter.custom_h(self.txtarea,'void',type_color)
    TKlighter.custom_h(self.txtarea,'volatile',modify_color)
    TKlighter.custom_h(self.txtarea,'while',control_color)

    TKlighter.custom_h(self.txtarea,'ifdef','red')
    TKlighter.custom_h(self.txtarea,'ifndef','red')
    TKlighter.custom_h(self.txtarea,'define','red')
    TKlighter.custom_h(self.txtarea,'undef','red')
    TKlighter.custom_h(self.txtarea,'include','red')
    TKlighter.custom_h(self.txtarea,'line','red')
    TKlighter.custom_h(self.txtarea,'error','red')
    TKlighter.custom_h(self.txtarea,'pragma','red')
    TKlighter.custom_h(self.txtarea,'defined','red')

    TKlighter.custom_h(self.txtarea,'asm','red')
    TKlighter.custom_h(self.txtarea,'__asm','red')
    TKlighter.custom_h(self.txtarea,'__endasm','red')
    TKlighter.custom_h(self.txtarea,'__data','red')
    TKlighter.custom_h(self.txtarea,'__near','red')
    TKlighter.custom_h(self.txtarea,'__xdata','red')
    TKlighter.custom_h(self.txtarea,'__far','red')
    TKlighter.custom_h(self.txtarea,'__idata','red')
    TKlighter.custom_h(self.txtarea,'__pdata','red')
    TKlighter.custom_h(self.txtarea,'__code','red')
    TKlighter.custom_h(self.txtarea,'__bit','red')
    TKlighter.custom_h(self.txtarea,'__sfr','red')
    TKlighter.custom_h(self.txtarea,'__sfr16','red')
    TKlighter.custom_h(self.txtarea,'__sfr32','red')
    TKlighter.custom_h(self.txtarea,'__sbit','red')
    TKlighter.custom_h(self.txtarea,'__reentrant','red')
    TKlighter.custom_h(self.txtarea,'__interrupt','red')
    #TKlighter.custom_regex_h(self.txtarea,r'"',"red")
    #
    #TKlighter.custom_regex_h(self.txtarea,r'"(\\"|[^"]*)"','lightgreen')
    TKlighter.custom_regex_h(self.txtarea,r"['\"].*?['\"]","darkgreen")
    #
    #TKlighter.custom_regex_h(self.txtarea,r"/\*.*?\*/","gray")
    TKlighter.custom_regex_h(self.txtarea,r"(//[^\n]*$|/(?!\\)\*[\s\S]*?\*(?!\\)/)","gray")
    #
    TKlighter.custom_regex_h(self.txtarea,r"//.*","gray")
    
  # Defining settitle function
  def settitle(self):
    # Checking if Filename is not None
    if self.filename:
      # Updating Title as filename
      self.title.set(self.filename)
    else:
      # Updating Title as Untitled
      self.title.set("Untitled")

  # Defining New file Function
  def newfile(self,*args):
    # Clearing the Text Area
    self.txtarea.delete("1.0",END)
    # Updating filename as None
    self.filename = None
    # Calling settitle funtion
    self.settitle()
    # updating status
    self.status.set("New File Created")
    self.txtarea.focus_set()
    #
    self.txtarea.event_generate('<<KeyRelease>>')
  # Defining Open File Funtion
  def openfile(self,*args):
    # Exception handling
    try:
      # Asking for file to open
      if len(args) > 0:
        self.filename = args[0]
      else:    
        self.filename = filedialog.askopenfilename(title = "Select file",filetypes = (("All Files","*.*"),("Text Files","*.txt"),("C Files","*.c")))
      
      # checking if filename not none
      if self.filename:
        # Clearing text area
        self.txtarea.delete("1.0",END)


        # opening file in readmode
        infile = open(self.filename,"r")
        
        
        #self.txtarea.delete('end-1l',END)
        s=self.txtarea.get("1.0",END)
        str=":".join("{:02x}".format(ord(c)) for c in s)
        print(str)
        # Inserting data Line by line into text area
        #for line in infile:
        #  self.txtarea.insert(END,line)
        
        data = infile.read()
        self.txtarea.insert(END,data)
        
        
        # Closing the file  
        infile.close()
        # Calling Set title
        self.settitle()
        # Updating Status
        self.status.set("Opened Successfully")
        self.outputarea.after(1,self.root.update_idletasks())
        #self.txtarea.after(1,
        self.txtarea.event_generate('<<KeyRelease>>')
        #self.light()
        # write the prev file name
        JSON_FILE = open(CONFIG_FILE,'r+').read()
        JSON_DATA = json.loads(JSON_FILE)
        JSON_DATA["prevFileName"] = self.filename
        JSON_DUMP = json.dumps(JSON_DATA)
        JSON_FILE = open(CONFIG_FILE,'w')
        JSON_FILE.write(JSON_DUMP)
        # FIXME cut the tail newline
        s=self.txtarea.get("1.0",END)
        str=":".join("{:02x}".format(ord(c)) for c in s)
        print(str)
    except Exception as e:
      messagebox.showerror("Exception",e)    
  # Defining Save File Funtion
  def savefile(self,*args):
    # Exception handling
    try:
      # checking if filename not none
      if self.filename:
        # Reading the data from text area
        data = self.txtarea.get("1.0",END)
        # opening File in write mode
        outfile = open(self.filename,"w")
        # Writing Data into file
        outfile.write(data)
        # Closing File
        outfile.close()
        # Calling Set title
        self.settitle()
        # Updating Status
        self.status.set("Saved Successfully")
        self.txtarea.focus_set()
      else:
        self.saveasfile()
    except Exception as e:
      messagebox.showerror("Exception",e)

  # Defining Save As File Funtion
  def saveasfile(self,*args):
    # Exception handling
    try:
      # Asking for file name and type to save
      untitledfile = filedialog.asksaveasfilename(title = "Save file As",defaultextension=".c",initialfile = "Untitled.c",filetypes = (("All Files","*.*"),("Source Files","*.c"),("Header Files","*.h")))
      # Reading the data from text area
      data = self.txtarea.get("1.0",END)
      # opening File in write mode
      outfile = open(untitledfile,"w")
      # Writing Data into file
      outfile.write(data)
      # Closing File
      outfile.close()
      # Updating filename as Untitled
      self.filename = untitledfile
      # Calling Set title
      self.settitle()
      # Updating Status
      self.status.set("Saved Successfully")
      self.txtarea.focus_set()
      # write the prev file name
      JSON_FILE = open(CONFIG_FILE,'r+').read()
      JSON_DATA = json.loads(JSON_FILE)
      JSON_DATA["prevFileName"] = self.filename
      JSON_DUMP = json.dumps(JSON_DATA)
      JSON_FILE = open(CONFIG_FILE,'w')
      JSON_FILE.write(JSON_DUMP)
    except Exception as e:
      messagebox.showerror("Exception",e)

  # Defining Exit Funtion
  def exit(self,*args):
    op = messagebox.askyesno("WARNING","Your Unsaved Data May be Lost!!")
    if op>0:
      self.root.destroy()
    else:
      return

  # Defining Cut Funtion
  def cut(self,*args):
    self.txtarea.event_generate("<<Cut>>")

  # Defining Copy Funtion
  def copy(self,*args):
    self.txtarea.event_generate("<<Copy>>")

  # Defining Paste Funtion
  def paste(self,*args):
    self.txtarea.event_generate("<<Paste>>")

  # Defining Undo Funtion
  def undo(self,*args):
    # Exception handling
    try:
      # checking if filename not none
      if self.filename:
        # Clearing Text Area
        self.txtarea.delete("1.0",END)
        # opening File in read mode
        infile = open(self.filename,"r")
        # Inserting data Line by line into text area
        for line in infile:
          self.txtarea.insert('1.0',line)
        # Closing File
        infile.close()
        # Calling Set title
        self.settitle()
        # Updating Status
        self.status.set("Undone Successfully")
      else:
        # Clearing Text Area
        self.txtarea.delete("1.0",END)
        # Updating filename as None
        self.filename = None
        # Calling Set title
        self.settitle()
        # Updating Status
        self.status.set("Undone Successfully")
    except Exception as e:
      messagebox.showerror("Exception",e)
  def pickup_sdcc(self):
    self.sdccPath = filedialog.askopenfilename(title = "Select sdcc")
    if self.sdccPath:
      self.menu8051.entryconfig(1,label="sdcc: "+self.sdccPath)
      # write the prev file name
      JSON_FILE = open(CONFIG_FILE,'r+').read()
      JSON_DATA = json.loads(JSON_FILE)
      JSON_DATA["sdccPath"] = self.sdccPath
      JSON_DUMP = json.dumps(JSON_DATA)
      JSON_FILE = open(CONFIG_FILE,'w')
      JSON_FILE.write(JSON_DUMP)
  def pickup_avrdude(self):
    self.avrdudePath = filedialog.askopenfilename(title = "Select avrdude")
    if self.avrdudePath:
      self.menu8051.entryconfig(2,label="avrdude: "+self.avrdudePath)
      # write the prev file name
      JSON_FILE = open(CONFIG_FILE,'r+').read()
      JSON_DATA = json.loads(JSON_FILE)
      JSON_DATA["avrdudePath"] = self.avrdudePath
      JSON_DUMP = json.dumps(JSON_DATA)
      JSON_FILE = open(CONFIG_FILE,'w')
      JSON_FILE.write(JSON_DUMP)
  def comport(self):
    pass
  def shell_output_insert_end(self, output):
    self.outputarea.insert(END, output)
    self.outputarea.see(END)
    self.outputarea.after(1,self.root.update_idletasks())
  
  def enqueue_output(self, out, queue):
    for line in iter(out.readline, b''):
      queue.put(line)
    out.close()
    
  def execute_tool(self, cmd):
    self.shell_output_insert_end(cmd+"\n")
    
#     ON_POSIX = 'posix' in sys.builtin_module_names    
#     p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, close_fds=ON_POSIX)
#     q=queue.Queue()
#     t=threading.Thread(target=self.enqueue_output, args=(p.stdout, q))
#     t.daemon = True
#     t.start()
#         
#     line=''
#     while True:
#       try:
#         line = q.get_nowait()
#       except queue.Empty:
#         if line == '' and p.poll() is not None:
#           break
#       else:
#         self.shell_output_insert_end(line)
    (pipe_r, pipe_w) = os.pipe()
    p=subprocess.Popen(cmd, shell=True, stdout=pipe_w, stderr=pipe_w, bufsize=1, universal_newlines=True)
    while p.poll() is None:
      # Loop long as the selct mechanism indicates there
      # is data to be read from the buffer
      #while len(select.select([pipe_r], [], [], 0)[0]) == 1:
        # Read up to a 1 KB chunk of data
      buf = os.read(pipe_r, 1024)
        # Stream data to our stdout's fd of 0
        #os.write(0, buf)
      self.shell_output_insert_end(buf)

    #flags = fcntl.fcntl(p.stdout, fcntl.F_GETFL) # get current p.stdout flags
    #fcntl.fcntl(p.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
#     try:
#       while True:
#         output = p.stdout.readline()
#         if output == '' and p.poll() is not None:
#           break
#         if output:
#           self.shell_output_insert_end(output)
#     except EOFError:
#         pass
    
    if p.returncode != 0:
      self.shell_output_insert_end("\nSomething wrong...\n")
      return 1
    else:
      return 0  
    
  def build(self,*args):
    self.outputarea.configure(state='normal')
    self.outputarea.delete("1.0",END)
    self.shell_output_insert_end(str(self.filename)+" saved.\n\n")
    self.savefile()
    ## echo \"\nsdcc $file\n\" && sdcc --verbose \"$file\"
    cmd = "\""+self.sdccPath+"\"" + " --verbose -o \""+os.path.dirname(self.filename)+"/\" \""+str(self.filename)+"\""
    if self.execute_tool(cmd):
      return
    
    self.shell_output_insert_end("\nOK\n")
  def upload(self,*args):
    self.outputarea.configure(state='normal')
    self.outputarea.delete("1.0",END)
    self.shell_output_insert_end(self.filename+" saved.\n\n")
    self.savefile()
    
    cmd = "\""+self.sdccPath+"\"" + " --verbose -o \""+os.path.dirname(self.filename)+"/\" \""+str(self.filename)+"\""
    if self.execute_tool(cmd):
      return
    self.shell_output_insert_end("\nOK\n")
    
    #cmd = "stty -f /dev/"+str(self.portDeviceName)+" ispeed 1200 ospeed 1200"
    #if self.execute_tool(cmd):
    #  return
    #self.shell_output_insert_end("\nOK\n")
    ## open and close the com port
    self.shell_output_insert_end("\nOpening the com port...\n")
    try:
      with serial.Serial("/dev/"+str(self.portDeviceName), 1200, timeout=1) as ser:
        ser.close()
    except serial.SerialException as e:
      self.shell_output_insert_end(e)
      self.shell_output_insert_end("\nSomething wrong...\n")
      return
    
    self.shell_output_insert_end("Reseting ISP...\n")
    # waiting for the arduinoAsISP's 8 secends.
    for i in range(9):
      self.outputarea.insert(END, ".")
      self.outputarea.see(END)
      self.outputarea.after(1000,self.root.update_idletasks())
    self.shell_output_insert_end("\n")
    
    uploadPathFileName = str(self.filename).split('.')[0]+".ihx"
    cmd = self.avrdudePath + " -Cavrdude.conf -v -p89s52 -cstk500v1 -P/dev/"+self.portDeviceName+" -b19200 -Uflash:w:"+uploadPathFileName
    if self.execute_tool(cmd): 
      return
    
    self.outputarea.configure(state='disabled')
    pass
  def terminal(self,*args):
    subprocess.check_output("python3 miniterm.py "+self.portDeviceName, stderr=subprocess.STDOUT, shell=True)
  def plotter(self,*args):
    pass
  
  # Defining About Funtion
  def infoabout(self):
    messagebox.showinfo("About Simple 51 IDE","A Simple 8051 IDE\nCreated using Python.")

  # Defining shortcuts Funtion
  def shortcuts(self):
    # Binding Ctrl+n to newfile funtion
    self.txtarea.bind("<Control-n>",self.newfile)
    # Binding Ctrl+o to openfile funtion
    self.txtarea.bind("<Control-o>",self.openfile)
    # Binding Ctrl+s to savefile funtion
    self.txtarea.bind("<Control-s>",self.savefile)
    # Binding Ctrl+a to saveasfile funtion
    #self.txtarea.bind("<Control-a>",self.saveasfile)
    # Binding Ctrl+e to exit funtion
    self.txtarea.bind("<Control-e>",self.exit)
    # Binding Ctrl+x to cut funtion
    self.txtarea.bind("<Control-x>",self.cut)
    # Binding Ctrl+c to copy funtion
    self.txtarea.bind("<Control-c>",self.copy)
    # Binding Ctrl+v to paste funtion
    self.txtarea.bind("<Control-v>",self.paste)
    # Binding Ctrl+u to undo funtion
    self.txtarea.bind("<Control-u>",self.undo)

    self.txtarea.bind("<Control-b>",self.build)
    self.txtarea.bind("<Control-p>",self.upload)
    self.txtarea.bind("<Control-t>",self.terminal)
    self.txtarea.bind("<Control-l>",self.plotter)

    if platform.system() == "Darwin":
      self.txtarea.bind("<Command-n>",self.newfile)
      self.txtarea.bind("<Command-o>",self.openfile)
      self.txtarea.bind("<Command-s>",self.savefile)
      #self.txtarea.bind("<Command-a>",self.saveasfile)
      self.txtarea.bind("<Command-e>",self.exit)
      #self.txtarea.bind("<Command-x>",self.cut)
      #self.txtarea.bind("<Command-c>",self.copy)
      #self.txtarea.bind("<Command-v>",self.paste)
      #self.txtarea.bind("<Command-u>",self.undo)
      self.txtarea.bind("<Command-b>",self.build)
      self.txtarea.bind("<Command-p>",self.upload)
      self.txtarea.bind("<Command-t>",self.terminal)
      self.txtarea.bind("<Command-l>",self.plotter)
# Creating TK Container
root = Tk()
# Passing Root to TextEditor Class
TextEditor(root)
# Root Window Looping
root.mainloop()