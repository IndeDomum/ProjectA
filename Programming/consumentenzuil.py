#alle gebruikte imports
import psycopg2                                 #database import
from datetime import datetime                   #datum import
import tkinter as tk                            #import tkinter voor bepaalde dingen die (volgens de tutorial) moesten
from tkinter import messagebox as mb            #popup voor error of waarschuwing vooral bij het sluiten van de applicatie
from tkinter.ttk import *                       #extra import voor treeview
from tkinter import *                           #import alles van tkinter zonder extra naam
from tkinter import ttk                         #import alleen ttk van tkinter
from PIL import ImageTk, Image     #toevoegen van afbeeldingen, (optioneel)
import tweepy                                   #import voor posten op twitter via tweepy
#einde van imports

#kleuren voor console prints
class bcolors:
    On_IBlack = "\033[0;100m"
    OKBLUE = '\033[94m'
    FAIL = '\033[91m'                       #kleuren voor in de pycharm log (is optioneel, ik vond t wel overzichtelijker)
    ENDC = '\033[0m'
    WARNING = '\033[93m'
#einde van kleuren

#database connect
con = psycopg2.connect(
    host='localhost',
    database='NSberichten',
    user='postgres',                #connecten met de database
    password='tim1325083'
)
con.autocommit = True               #zorgen dat con.commit() niet elke keer hoeft. Wordt gebruikt bij goed en foutkeuren
cur = con.cursor()
#einde databse connect

#twitter api tokens
consumer_key = 'BQ9DGkGuH6VyP3ZKf5KdD03vp'
consumer_secret = '6jovjt9bIMP23AQnSxqRiP5GtbMF2bFuDF07NCC5hdRMqhtjAW'          #tokens voor twitter API
access_token = '1202176711204507648-xkw6KgljtnxJeHQ3U1iDvfZas0UXxU'
access_token_secret = 'S3XUestdmmYdiUUMR78zXlKe3gYdcGILNNAIu6z2LYQoD'
#einde twitter api tokens

#datum en tijd
now = datetime.now()
datum = now.strftime("%Y/%m/%d %H:%M:%S")               #haalt de huidige tijd op
#einde van datum en tijd

#geef error bij knop sluiten
def callback():
    if mb.askyesno('Verify', 'Weet u zeker dat u wilt stoppen?'):           #vragen of ze zeker zijn dat ze af willen sluiten
        mb.showwarning('Yes', exit())
#einde van melding bij sluiten

#twitter auth
def plaatsen():
    def OAuth():
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)            #authentication van twitter inloggegevens
            return auth

        except Exception as e:
            return None
#einde twitter auth

#tweets plaatsen
    oauth = OAuth()
    api = tweepy.API(oauth)

    cur.execute("select naam, bericht, datum from tweets where keuring = 'ja'")
    rows = cur.fetchall()
    for r in rows:
        api.update_status(f"Naam: {r[0]}\nDatum: {r[2]}\nBericht: {r[1]}")
        print("tweets geplaatst")
        cur.execute("UPDATE tweets SET keuring = 'goed' where keuring = 'ja'") #alle berichten met keuring 'ja' vernaderd naar keuring 'goed' zodat hij niet 2x iets met 'ja' post
        print("alle berichten met keuring 'ja' vernaderd naar keuring 'goed'")
#einde tweets plaatsen

#post bericht en naam in de database
def db_post():
    tweet = bericht.get('1.0', END)
    if len(tweet) > 5 and len(tweet) < 140:
        name = naam.get()
        if len(name) == 0:
            name = "anoniem"            #ervoor zorgen dat het bericht tussen de 5 en 140 karakters lang moet zijn en een naam leeg kan zijn
        cur.execute('insert into tweets (naam, bericht, datum) values (%s, %s, %s)', (name, tweet, datum))
        con.commit()
        naam.delete(0, 'end')                               #posten van berichten door reizigers naar de databse om gekeurd te worden
        bericht.delete('1.0', END)
    else:
        mb.showerror("Error", "Het bericht moet tussen de 5 en 140 karakters lang zijn.")
#einde van database post

#annuleer knop om entry te verwijderen
def Clear():
    naam.delete(0, 'end')
    bericht.delete('1.0', END)
#einde van clear

def sluit():
    exit() #sluit "Lwindow" na 3sec als er geen berichten meer zijn om te keuren

#begin van de login
def openNewWindow():

    #admin scherm
    def moderate_messages(id):
        Lwindow.title("Admin")              #ingelogde moderator
        Lwindow.resizable(False, False)
        Lwindow.iconbitmap('Twitter.ico')
        newWindow.destroy()

        def goedkeuren(tweet_id, id):
            print("Tweet goedgekeurd")
            now = datetime.now()
            tijd = now.strftime("%Y/%m/%d %H:%M:%S")
            data = (id, tijd, tweet_id)
            goed = ("UPDATE tweets SET keuring = 'ja', moderator_id = %s, updated_at = %s WHERE tweet_id = %s")
            cur.execute(goed, data)                         #goedkeuren van berichten door moderator die de keuring verandert naar "ja" in de database
            message_frame.destroy()
            plaatsen()
            moderate_messages(id)

        def foutkeuren(tweet_id, id):
            op = Toplevel(Lwindow)  #foutkeuren van berichten door moderator die de keuring naar "nee" veranderd in de database na opmerking
            op.title("Opmerking plaatsen")
            op.iconbitmap('Twitter.ico')
            op.resizable(False, False)          #maken van opmerking window

            def annul():
                op.destroy()

            Label(op, text="Opmerking: ").grid(row=0, column=0)
            opmerkingtext = tk.Text(op, width=25, height=5, wrap=WORD)          #labels in opmerking window
            opmerkingtext.grid(row=0, column=1)
            tk.Button(op, text="Plaatsen", command=lambda: opmerkingbericht(tweet_id, id)).grid(row=1, column=1, sticky=tk.W, pady=4)
            tk.Button(op, text="Annuleer", command=annul).grid(row=1, column=1, sticky=tk.E, pady=4)

            def opmerkingbericht(tweet_id, id):
                print("Tweet foutgekeurd")
                merking = opmerkingtext.get('1.0', END)
                now = datetime.now()
                tijd = now.strftime("%Y/%m/%d %H:%M:%S")                #tijd,moderator_id,bericht_id etc posten in database
                if len(merking) > 5:
                    data = (merking, id, tijd, tweet_id)
                    fout = ("UPDATE tweets SET keuring = 'nee', opmerking = %s, moderator_id = %s, updated_at = %s WHERE tweet_id = %s")
                    cur.execute(fout, data)
                    op.destroy()
                    message_frame.destroy()
                    moderate_messages(id)
                else:
                    mb.showerror("Error", "Het bericht moet langer zijn dan 5 karakters")

        def opmerking():
            merk = Toplevel(Lwindow)
            merk.title("Opmerkingen")
            merk.iconbitmap('Twitter.ico')              #window voor treeview

            def view():
                cur.execute("SELECT tweet_id, naam, bericht, datum, keuring, opmerking, moderator_id, updated_at FROM tweets ORDER BY tweet_id ASC")
                rows = cur.fetchall()
                for row in rows:                    #alle berichten zowwel gekeurd als niet gekeurd
                    tree.insert("", tk.END, values=row)

            def goedview():
                tree.delete(*tree.get_children())
                cur.execute("SELECT tweet_id, naam, bericht, datum, keuring, opmerking, moderator_id, updated_at FROM tweets WHERE keuring = 'goed' ORDER BY tweet_id ASC")
                rows = cur.fetchall()
                for row in rows:                #alle goedgekeurde berichten
                    tree.insert("", tk.END, values=row)

            def foutview():
                tree.delete(*tree.get_children())
                cur.execute("SELECT tweet_id, naam, bericht, datum, keuring, opmerking, moderator_id, updated_at FROM tweets WHERE keuring = 'nee' ORDER BY tweet_id ASC")
                rows = cur.fetchall()
                for row in rows:            #alle foutgekeurde berichten
                    tree.insert("", tk.END, values=row)

            tree = ttk.Treeview(merk, column=("column1", "column2", "column3", "column4", "column5", "column6", "column7", "column8"), show='headings')
            tree.heading("#1", text="Tweet_id")
            tree.heading("#2", text="Naam")
            tree.heading("#3", text="Bericht")
            tree.heading("#4", text="Datum")
            tree.heading("#5", text="Keuring")
            tree.heading("#6", text="Opmerking")                #treeview van tabellen
            tree.heading("#7", text="Moderator_id")
            tree.heading("#8", text="Updated_at")
            tree.pack(fill=BOTH, expand=True)

            b2 = tk.Button(merk, text="Goede berichten", command=goedview)
            c2 = tk.Button(merk, text="Foute berichten", command=foutview)          #knoppen om goed of fout te filteren
            b2.pack(side=LEFT, fill=X, expand=True)
            c2.pack(side=LEFT, fill=X, expand=True)
            view()

        message = cur.execute("select tweet_id, naam, bericht, datum from tweets where keuring is null order by datum ASC")
        rows = cur.fetchone()
        message_frame = LabelFrame(Lwindow, bg="#F8F8FF", padx=5, pady=5, width=250, height=80)         #goed of foutkeur label
        message_frame.pack(padx=10, pady=5)
        if rows is not None:
            tk.Label(message_frame, text="@" + rows[1], font=("Comic Sans MS", 12), bg="#F8F8FF").grid(row=0, column=0, pady=4, padx=4, sticky=tk.W)
            tk.Label(message_frame, text=rows[3], bg="#F8F8FF", font=("Arial", 8), fg="#444444").grid(row=0, column=0, pady=4, padx=4, sticky=tk.E)
            tk.Label(message_frame, text="----------------------------------------------------", bg="#F8F8FF", fg="#F8F8FF", wraplength=260, justify="left").grid(row=1)
            tk.Label(message_frame, text=rows[2], font=("Century Gothic", 10), bg="#F8F8FF", wraplength=260, justify="left").grid(row=2, pady=4, padx=4)
            tk.Button(message_frame, text="Goedkeuren", command=lambda: goedkeuren(rows[0], id), bg="#4f42ff", fg="#F8F8FF").grid(row=3, column="0", pady=4, padx=4, sticky=tk.W)
            tk.Button(message_frame, text="Foutkeuren", command=lambda: foutkeuren(rows[0], id), bg="#ffae42").grid(row=3, column="0", pady=4, padx=4, sticky=tk.E)

            tk.Button(message_frame, text="Opmerkingen", command=opmerking, bg="#42f2ff", width=19).grid(sticky=tk.S)
            tk.Button(message_frame, text="Sluiten", command=callback, width=38).grid(sticky=tk.S)

        else:
            tk.Label(message_frame, text="Geen berichten meer om te laten zien").grid(sticky=tk.N)              #als er geen berichten meer zijn om te keuren
            tk.Button(message_frame, text="Opmerkingen", command=opmerking, bg="#42f2ff", width=19).grid(sticky=tk.S)
            tk.Button(message_frame, text="Sluiten", command=callback, width=38).grid(sticky=tk.S)
    #einde admin scherm

    #begin login check
    def validateLogin(username, password):
        data = (username, password)             #"backend" van de inlog van moderators
        get_moderator = 'SELECT moderator_id FROM gebruikers where naam = %s AND wachtwoord = %s'

        cur.execute(get_moderator, data)
        if cur.rowcount > 0:
            moderator_id = cur.fetchone()[0]
            global Lwindow
            Lwindow = Toplevel(master)
            moderate_messages(moderator_id)         #neemt ID mee om later in de databse in te voegen bij het foutkeuren
            print(f"Ingelogde moderator_id: {moderator_id}")
        else:
            mb.showerror("Error", "De ingevoerde gegevens komen niet overeen met een bestaand account.")
    #einde login check

    #exit uit deze window
    def sluiten():
        master.deiconify()              #sluiten van window en nieuwe laten zien zodat je er niet meerdere open hebt
        newWindow.destroy()
        #hetzelfde als exit() alleen dan alleen voor deze ene window
    #einde exit

    #settings van nieuwe window, titel en grootte
    master.withdraw()
    newWindow = Toplevel(master)
    newWindow.title("Login")            #window voor inloggen voor moderator
    newWindow.geometry("300x80")
    newWindow.iconbitmap('Twitter.ico')
    newWindow.resizable(False, False)
    #einde van settings

    #entry fields
    usernameLabel = Label(newWindow, text="Gebruikersnaam: ").grid(row=0, column=0)
    username = StringVar()
    usernameEntry = tk.Entry(newWindow, textvariable=username).grid(row=0, column=1)
                                                                                        #invoer voor het inloggen
    passwordLabel = Label(newWindow, text="Wachtwoord: ").grid(row=1, column=0)
    password = StringVar()
    passwordEntry = tk.Entry(newWindow, textvariable=password, show='*').grid(row=1, column=1)
    #einde entry fields

    #knoppies om de inlogcheckt te doen of te sluiten
    tk.Button(newWindow, text="Login", command=lambda: validateLogin(username.get(), password.get())).grid(row=2, column=1, sticky=tk.W, pady=4)
    tk.Button(newWindow, text="Sluiten", command=sluiten).grid(row=2, column=1, sticky=tk.E, pady=4)
    #einde van de knoppies

# login einde

#het woord voor entry field
master = tk.Tk()
tk.Label(master,
         text="Naam:").grid(row=0)
tk.Label(master,
         text="Bericht:").grid(row=1)
#einde van tekst voor entry

#entry field
naam = tk.Entry(master)
bericht = tk.Text(master, width=25, height=5, wrap=WORD)                #invoer velden voor het plaatsen van berichten
#einde van entry field

#positie van entry field
naam.grid(row=0, column=1, sticky=tk.W)
bericht.grid(row=1, column=1, pady=5)
#einde positie

#knoppen onder entry field
tk.Button(master, text='Login', command=openNewWindow).grid(row=3, column=3, sticky=tk.W, pady=4)
tk.Button(master, text='Plaatsen', command=db_post).grid(row=3, column=0, sticky=tk.W, pady=4)
tk.Button(master, text="Annuleer", command=Clear).grid(row=3, column=1, sticky=tk.W, pady=4)            #knoppen op main window
tk.Button(master, text='Sluiten', command=callback).grid(row=3, column=2, sticky=tk.W, pady=4)
#einde van knoppen

#einde van file wat alles runt en closed enzo
master.title("Sprint 4")                                #main window voor de reizigers
master.iconbitmap('Twitter.ico')
master.resizable(False, False)
tk.mainloop()
cur.close()
con.close()
#einde van alles
