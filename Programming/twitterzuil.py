#alle gebruikte imports
import psycopg2
from tkinter.ttk import *
from tkinter import *
import time
import requests
#einde van imports

#database connect
con = psycopg2.connect(
    host='localhost',
    database='NSberichten',
    user='postgres',
    password='tim1325083'
)
cur = con.cursor()
#einde databse connect

time1 = ''

#begin van twitter scherm
master = Tk()
master.title("Sprint 4")
master.iconbitmap('Twitter.ico')
master.configure(bg='#f2f2f2')
master.resizable(False, False)
master.geometry('320x500')

#tijd bovenaan
locatie = requests.get("http://ip-api.com/json/?fields=61439&lang=nl")
if locatie.status_code == 200:
    station = locatie.json()
    clock = Label(master, font=('Tw Cen MT', 20), bg='#f2da0a', pady=25)
    plek = Label(master, text='Station ' + str(station['city']), font=("Arial", 8), bg="#f2da0a", fg="#444444")
    clock.pack(fill=X)
    plek.pack(fill=X)

def tick():
    global time1
    time2 = time.strftime('%H:%M:%S')
    if time2 != time1:
        time1 = time2                           #opmerkingen plaatsenn nog fixen
        clock.config(text=time2)
    clock.after(200, tick)

tick()
#einde tijd

frame = LabelFrame(padx=5, pady=5, width=250, height=80, highlightthickness=0, borderwidth=0)
frame.pack(fill=BOTH)

def tweets():
    for widget in frame.winfo_children():
        widget.destroy()
    master.after(120000, tweets)
    #meest recente tweets laten zien
    cur.execute("select tweet_id, naam, bericht, datum from tweets where keuring = 'goed' AND datum > (NOW() - INTERVAL '2' MINUTE) order by datum DESC")
    rows = cur.fetchmany(3)
    if cur.rowcount > 0:
        for row in rows:
            message_frame = LabelFrame(frame, bg="#F8F8FF", padx=5, pady=5, width=250, height=80)
            message_frame.pack(padx=10, pady=5, side=TOP)
            Label(message_frame, text="@" + row[1], font=("Century Gothic", 12, 'bold'), fg='#1e2d6e', bg="#F8F8FF").grid(row=0, column=0, pady=4, padx=10, sticky=W)
            Label(message_frame, text=row[3], bg="#F8F8FF", font=("Arial", 8), fg="#444444").grid(row=0, column=0, pady=4, padx=4, sticky=E)
            Label(message_frame, text="--------------------------------------------------", bg="#F8F8FF", fg="#F8F8FF", wraplength=260, justify="left").grid(row=1)
            Label(message_frame, text=row[2], font=("Century Gothic", 10), bg="#F8F8FF", wraplength=260, justify="left").grid(row=2, pady=4, padx=4)
    else:
        message_frame = LabelFrame(frame, bg="#F8F8FF", padx=5, pady=5, width=250, height=80)
        message_frame.pack(padx=10, pady=5, side=TOP)
        weer = requests.get("http://api.openweathermap.org/data/2.5/weather?q=Utrecht&lang=nl&units=metric&appid=acfd63edaae0c1dcc5619d1080bebac9")
        if weer.status_code == 200:
            weerbericht = weer.json()
            Label(message_frame, text="Weerbericht", font=("Century Gothic", 12, 'bold'), fg='#1e2d6e', bg="#F8F8FF").grid(row=0, column=0, pady=2, padx=2, sticky=W)
            Label(message_frame, text="-------------------------------------------", bg="#F8F8FF", fg="#F8F8FF", wraplength=260, justify="left").grid(row=1)
            Label(message_frame, text='Weer: ' + str(weerbericht['weather'][0]['description']), font=("Arial", 8), bg="#F8F8FF", fg="#444444").grid(row=1, column=0, pady=4, padx=5, sticky=W)
            Label(message_frame, text='Graden: ' + str(int(weerbericht['main']['temp'])) + " °C", bg="#F8F8FF", font=("Arial", 8), fg="#444444").grid(row=2, column=0, pady=4, padx=5, sticky=W)
            Label(message_frame, text='Windkracht: ' + str(weerbericht['wind']['speed']), font=("Arial", 8), bg="#F8F8FF", fg="#444444").grid(row=3, column=0, pady=4, padx=5, sticky=W)


#einde tweet laten zien
tweets()
mainloop()
cur.close()
con.close()
#einde van alles
