import tkinter as tk
from tkinter import *
from tkinter import filedialog
import sys
import os
from datetime import datetime
import pandas as pd
root = tk.Tk()
frame = tk.Frame(root)
frame.pack(pady = 10, padx = 10)
root.title("Extract from Email")


global email_dir
email_dir = StringVar()



#Choose Path
def fileNameToEntry():
    print("test one")


    filename = filedialog.askdirectory()
    filename = filename.strip()

    #User select cancel
    if (len(filename) == 0):
        messagebox.showinfo("show info", "you must select a file")       
        return
    #selection go to Entry widget
    else:
        email_dir.set(filename)
        print(email_dir.get())
        tpath.insert(tk.END, filename) # add this

        validation()


def validation():
    print("two")
    if len(email_dir.get())== 0:
        lerror.config(text="Choose the folder",font=('Arial', 14))


def runfunction():
    print("three")
    first_line='''Rinex START DecimalYear North_UTM(m) North_SPC(m) East_UTM(m) East_SPC(m) V_ORTH(m) V_ELIP(m)  USED% AMB% RMS(m) \n'''
    current_directory = os.getcwd()
    if os.path.exists("OPUS.out.txt"):
        os.remove("OPUS.out.txt")
    f_out= open("OPUS.out.txt", 'a')
    f_out.write(first_line)


    opus_list=[]

    os.chdir(email_dir.get())
    for tmp in os.listdir(email_dir.get()):
        if tmp.endswith('txt'):
            opus_list.append(tmp)
    for opus_file in opus_list:
        os.chdir(email_dir.get())
        f = open(opus_file)
        lines=f.readlines()
        line_count = 0
        for line in lines:
            line_count = line_count + 1
            if line.find('NGS OPUS SOLUTION REPORT')>-1:
                print ("Start a day!"+line)
            elif line.find('RINEX FILE:')>-1:
                lst = line.split()
                rinex_file=lst[2]
                print (rinex_file)
            elif line.find('START:')>-1:
                lst = line.split()
                date=lst[6]
                print (datetime.strptime(date,"%Y/%m/%d"))
                time1=datetime.strptime(date,"%Y/%m/%d")
                time=time1.strftime( '%Y-%m-%d')
                time2=time1.year+float((time1.month-1)*30+time1.day)/365
            #print 'time is '+time1
                print (date,time2)
            elif line.find('USED:')>-1:
                lst = line.split()
                used = lst[9].rstrip('%')
            elif line.find('AMB:')>-1:
                lst = line.split()
                amb = lst[11].rstrip('%')
            elif line.find('RMS:') > -1:
                lst = line.split()
                rms = lst[5].rstrip('(m)')
            elif line.find('EL HGT:') > -1:
                lst = line.split()
                el_height = lst[2].rstrip('(m)')
            elif line.find('ORTHO HGT:') > -1:
                lst = line.split()
                orth_height = lst[2].rstrip('(m)')
            elif line.find('Northing')>-1:
                lst = line.split()
                north_utm=lst[3]
                north_spc = lst[4]

            elif line.find('Easting')>-1:
                lst = line.split()
                east_utm = lst[3]
                east_spc = lst[4]
                print (rinex_file,time,time2,north_utm,north_spc,east_utm,east_spc,orth_height,el_height,used,amb,rms)
                os.chdir(current_directory)
                f_out.write(rinex_file+" "+time+" "+str(time2)+" "+north_utm+" "+north_spc+" "+east_utm+" "+east_spc+" "+orth_height+" "+el_height+" "+used+" "+amb+" "+rms+"\n")
    f.close() # close the file
    f_out.close()

    df = pd.read_csv("OPUS.out.txt", sep = '\s+', usecols=[2,3,5,7,0], names=['stationname','DecimalYear', 'NS(cm)', 'EW(cm)', 'UD(cm)'], skiprows=1)
    df = df.sort_values(by=['DecimalYear'], ignore_index= True)

    df['NS(cm)'] = df['NS(cm)']*100
    df['EW(cm)'] = df['EW(cm)']*100
    df['UD(cm)'] = df['UD(cm)']*100
    #print (df)
    name = df['stationname'].str[0:4]
    df['stationname'] = name
    #print (df)
    n = df['stationname'].unique().tolist()
    for x in range(len(n)):
        dfx = df[df['stationname'] == n[x]]
        #print (dfx)
        dfx.to_csv(str(n[x])+'_OPUS_Result.txt', index=False, sep = ' ')

    filelist = []
    for f in os.listdir(current_directory):
        if f.endswith('_OPUS_Result.txt'):
            filelist.append(f)
        

    for file in filelist:
        df = pd.read_csv(file, sep = '\s+', usecols=[1,2,3,4] ,names=['DecimalYear', 'NS(cm)', 'EW(cm)', 'UD(cm)'], skiprows=1)
        #print (df)
        #print (file[0:9])
        Year=df['DecimalYear']
        firstrow= df.iloc[[0]].values[0]
        df1=df.apply(lambda row: row - firstrow, axis=1)
        df1['DecimalYear'] = Year
        df1.to_csv(str(file[0:9])+'_neu_cm.col', index=False, sep = ' ')
        os.remove(file)

    if os.path.exists("OPUS.out.txt"):
        os.remove("OPUS.out.txt")

#Choose Path
tpath = Entry(frame)
tpath.insert(0, "") 
tpath.grid(row = 1, column = 0, padx = 2, pady = 5)

button1 = tk.Button(frame, text = "Choose Path",command = fileNameToEntry)
button1.grid(row = 1, column = 1, pady = 5)

lerror = tk.Label(frame, text='',font=('Arial', 12),width= 40)
lerror.grid(row = 2, column = 0,columnspan = 2, padx = 5)


button3 = tk.Button(frame, text = "Submit",width =25, height = 2, command=runfunction)
button3.grid(row = 3, column = 0,columnspan = 2, padx = 5, pady = 5)


label1 = tk.Label(frame, text='Dr. Guquan Wang')
label1.grid(row = 4, column = 0, padx = 5, pady = 5)

root.mainloop()