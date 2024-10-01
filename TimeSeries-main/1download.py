import tkinter as tk
from tkinter import *
from selenium import webdriver
import time

#Import the Tkinter library
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
 
root = tk.Tk()

#padding the frame
frame = tk.Frame(root)
frame.pack(pady = 10, padx = 10)
root.title("GPS Download")

#Defining variable and browser
running = False



driver = webdriver.Chrome()
driver.get("https://data.unavco.org/archive/gnss/rinex/obs/2015/001/")

#Function to check login and select text file

def fileNameToEntry():
    if (driver.current_url == 'https://data.unavco.org/archive/gnss/rinex/obs/2015/001/'):

        if  button2["state"] == DISABLED:
            button2["state"] = NORMAL

        
        files = [('Text Document', '*.txt')]
        filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = files,
                                          defaultextension = files)
        filename = filename.strip()
        txname.insert(tk.END, filename)


    #User select cancel
        if (len(filename) == 0):
            messagebox.showinfo("show info", "you must select a file")       
            return
    #selection go to Entry widget
        else:
            global myStrVar
            myStrVar = StringVar()
            myStrVar.set(filename.split('/')[-1])
            with open(myStrVar.get()) as file:
                lines = len(file.readlines())
                label.config(text = "Total Files ="+str(lines))
            global running
            running = True

    else:
        label.config(text = "Please login first")

 
#Function to Download Files
def download_file():

     if running:
        with open(myStrVar.get()) as file:
            for i,line in enumerate(file, start=1):
                print(i)
                count.config(text = str(i))
                driver.get(line.strip())
                
            #[driver.get(line.strip()) for line in file]


 
button1 = tk.Button(frame, text = "Select File",command = fileNameToEntry)
button1.grid(row = 0, column = 1, padx = 5, pady = 5)

txname = tk.Text(frame, height=2, width=30)
txname.grid(row = 0, column = 0, padx = 5, pady = 5)

label = tk.Label(frame, text='')
label.grid(row = 1, column = 0, padx = 5, pady = 5)
 
button2 = tk.Button(frame, text = "Start Download",state="disabled", command=download_file)
button2.grid(row = 2, column = 0, padx = 5, pady = 5)

button3 = tk.Button(frame, text = "Exit",width = 15,command = root.destroy)
button3.grid(row = 2, column = 1, padx = 5, pady = 5)

label1 = tk.Label(frame, text='Dr. Guquan Wang')
label1.grid(row = 3, column = 0, padx = 5, pady = 5)

count = tk.Label(frame, text='')
count.grid(row = 4, column = 0, padx = 5, pady = 5)

root.mainloop()