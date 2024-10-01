import tkinter as tk
from tkinter import *
from selenium import webdriver
import time
import sys
import os
import time
import math
#import chunks
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#Import the Tkinter library
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from selenium.common.exceptions import TimeoutException
 
root = tk.Tk()
frame = tk.Frame(root)
frame.pack(pady = 10, padx = 10)
root.title("Data Upload")
global myfold


myfold = StringVar()


#------------------------------------------------------------------------------------------
###Step1: Zip your data files
current_directory = os.getcwd()

total = 0
cnt = 0
zip_list = []
name_count = 0
zip_files=[]
upload_list=[]
chunks = []
zip_num= 2
#os.chdir(data_dir)


driver = webdriver.Chrome()
driver.get('https://www.ngs.noaa.gov/OPUS/')


#------------------------------------------------------------------------------------------
def statupload():
    validation()
    if len(temail.get()) == 0:
        lerror.config(text="please enter your email",font=('Arial', 14))
    else:

        upload4 = driver.find_element(By.NAME,'email_address')
        upload4.send_keys(myemail)
        
        os.chdir(myfold.get())

        for f in os.listdir(myfold.get()):
            if f.endswith('.Z'):
                upload_list.append(f)
                print(f,upload_list)


        for upload_file in upload_list:
            upload_to_opus(myfold.get(), upload_file)

###Step2: Upload Zip files to OPUS
def upload_to_opus(getdir,file):   

    #driver = webdriver.Chrome(os.path.join(str(current_directory),'chromedriver'))
    #open opus website
 
    #select upload file
    upload1 = driver.find_element(By.NAME,'uploadfile')
    upload1.send_keys('%s' % (str(getdir) + "/" + str(file)))  # send_keys
    #select antenna type
    #wait = WebDriverWait(driver, 15)
    # wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="select2-selection__arrow"]'))).click()

    upload5 = driver.find_element(By.NAME,'Static')
    upload5.click()


    try:
        WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.XPATH,'//*'),"Upload successful!"))
        print(file + " is uploaded successfully")
        os.remove(getdir+os.sep+file)
        
    except TimeoutException as ex:
        os.remove(getdir+os.sep+file)
        print(file + " error uploading files"+str(ex))
        pass
    driver.back()

    


    

    #driver.back()

    # ##select method
    # all_antenna_options = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li[@class="select2-results__option"]')))
    # for x in all_antenna_options:
    #     if myanten in x.text:
    #         x.click()

            
    #         os.remove(getdir+os.sep+file)
    #         driver.back()
    #         #driver.quit()
    #         break
#-------------------------------------------------------------------------------------------




#Choose Path
def fileNameToEntry():
    if  button3["state"] == DISABLED:
        button3["state"] = NORMAL
    filename = filedialog.askdirectory()
    filename = filename.strip()


    #User select cancel
    if (len(filename) == 0):

        messagebox.showinfo("show info", "you must select a file")       
        return
    #selection go to Entry widget
    else:

        myfold.set(filename)
        tpath.insert(tk.END, filename) # add this
        validation()

            # for f in os.listdir(myfold.get()):
            #     if f.endswith('d.Z'):
            #         zip_list.append(f)

            # for item in range(0,len(zip_list),zip_num):
            #     chunks.append(zip_list[item: item + zip_num])

            # for index,chunk_1 in enumerate(chunks):
            #     with ZipFile(str(index) + '.zip', 'w') as myzip:
            #         for files in chunk_1:
            #             myzip.write(files)

            # for file in os.listdir(myfold.get()):
            #     if file.endswith('.Z'):
            #         os.remove(file)

    


def validation():
    if len(thei.get())== 0 and len(temail.get()) == 0:
        lerror.config(text="fill all the inputs",font=('Arial', 14))
    else:
        global myheight,myemail,myanten
        myheight =thei.get()
        myemail=temail.get()
        myanten=tant.get()




#Anteena name
tant = Entry(frame)
tant.insert(0, "NONE") 
tant.grid(row = 0, column = 0, padx = 5, pady = 5)

lant = tk.Label(frame, text='Enter Anteena Name',font=('Arial', 8))
lant.grid(row = 1, column = 0, padx = 5)


#Anteena Height
thei = Entry(frame)
thei.insert(0,0) 
thei.grid(row = 0, column = 1, padx = 5, pady = 5)

lhei = tk.Label(frame, text='Enter Height',font=('Arial', 8))
lhei.grid(row = 1, column = 1, padx = 5)

#EnterEmail
temail = Entry(frame,width= 40)

temail.grid(row = 2, column = 0, columnspan = 2, padx = 5, pady = 5)

lemail = tk.Label(frame, text='Enter Email',font=('Arial', 8),width= 40)
lemail.grid(row = 3, column = 0,columnspan = 2, padx = 5)

#choose Path
tpath = Entry(frame)

tpath.grid(row = 4, column = 0, padx = 2, pady = 5)

button1 = tk.Button(frame, text = "Choose Path",command = fileNameToEntry)
button1.grid(row = 4, column = 1, pady = 5)

lerror = tk.Label(frame, text='',font=('Arial', 12),width= 40)
lerror.grid(row = 6, column = 0,columnspan = 2, padx = 5)

button3 = tk.Button(frame, text = "Submit",width =25, height = 2, command=statupload,state="disabled")
button3.grid(row = 5, column = 0,columnspan = 2, padx = 5, pady = 5)

label1 = tk.Label(frame, text='Dr. Guquan Wang')
label1.grid(row = 7, column = 0, padx = 5, pady = 5)


root.mainloop()
