import glob
import random
import threading
import traceback
from customtkinter import *
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
import spotipy
import pickle
import subprocess
import pytube
import youtube_dl
from functools import partial
import time as t
from better_profanity import profanity
import math

popularity_cache = dict()


if os.path.exists('popularity_cahce.dat'):
    with open('popularity_cahce.dat','rb') as f:
        popularity_cache = pickle.load(f)


def cleanup():
    current_dir = os.getcwd()
    mp4_files = glob.glob(os.path.join(current_dir, '*.mp4'))
    for mp4_file in mp4_files:
        try:
            os.remove(mp4_file)
        except Exception as e:
            print(f"Error deleting {mp4_file}: {e}")


#APP CONSTANTS PROCEED WITH CAUTION
with open("APP.CRED","rb") as f:
    rec = pickle.load(f)
    CLIENT_ID = rec[0]
    CLIENT_SECRET = rec[1]

POPULARITY_CONSTRAINT = 80
PROFANITY_ALLOWED= False
EXCLUDE_WORDS= ["Skit","Version", "Instrumental", "Interlude","Acapella","Extended","Acoustic","Remix","Demo","Intro","Medley", "Original Mix", "Radio Edit", "Extended Mix", "Club Mix", "Dance Remix", "Acoustic Version", "Instrumental Version", "Vocal Version", "Remix Version", "Official Video", "Live Performance", "Studio Recording", "Unplugged Version", "Demo Version", "Karaoke Version", "Single Version", "Album Version", "Explicit Version", "Clean Version", "Radio Version"]
EXCLUDE_REPETITION_OF = {"(":2}
redirect_uri = 'http://localhost:8080/callback/'


#
songnames = []
links = []
artistsSelected = dict()
song_ids_for_seed = list()



client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def check_song_popularity(song_name):
    global sp
    if song_name in popularity_cache:
        popularity = popularity_cache[song_name]
    else:
        results = sp.search(q=song_name, type='track',limit = 1)

        if len(results['tracks']['items']) == 0:
            print("Song not found.")
            return None

        track = results['tracks']['items'][0]
        popularity = track['popularity']
        popularity_cache[song_name] = popularity
    
    return popularity



preference = CTk()
preference.title("Song Selection")


def select_option(option):
    preference.destroy()
    
    if option == "artist":

        root = CTk()
        root.title("Select Artists You Want")

        artistsSelected = dict()
        def select_artist(i,name,uri):
            if name not in artistsSelected:
                artistsSelected[name] = uri
            else:
                del artistsSelected[name]
            refresh_selected_list()

        def refresh_selected_list():

            for child in selectedframe.winfo_children():
                child.destroy()
            
            for i,artist in enumerate(artistsSelected):
                CTkLabel(selectedframe,text = artist ).grid(row =i, column = 0)
            

        def search_spotify():
            global sp
            query = entry.get()
            if query:
                global results
                try:
                    results = sp.search(q=query,type='artist' ,limit=10)
                    
                    for child in resultsframe.winfo_children():
                        child.destroy()
                
                    global checkboxes
                    checkboxes = dict()
                    for i, artist in enumerate(results['artists']['items']):
                        CTkLabel(resultsframe,text = artist["name"] ).grid(row =i, column = 0)
                        checkboxes[i] = CTkCheckBox(resultsframe,text = "" ,command=partial(select_artist,i,artist["name"],artist['uri']))
                        checkboxes[i].grid(row =i, column = 1)
                except Exception as e:
                    print(traceback.format_exception(e))
            else:
                print("")
            

        searchbar = CTkFrame(root,width = 500)
        searchbar.grid(row = 0, column = 0)

        label = CTkLabel(searchbar, text="Enter Artist name:")
        label.grid(row=0, column=0, sticky='W',padx = 15)

        entry = CTkEntry(searchbar)
        entry.grid(row=0, column=1,padx = 15)

        search_button = CTkButton(searchbar, text="Search", command=search_spotify)
        search_button.grid(row=0, column=2, padx = 15)

        mainframe = CTkFrame(root,width=500, height=500)
        mainframe.grid(row = 1, column = 0,padx = 15, pady = 10)

        resultsframe = CTkFrame(mainframe, width = 230,height = 490,)
        resultsframe.grid(row = 0, column =0,  padx = 10, pady =5)

        selectedframe = CTkFrame(mainframe, width = 230,height = 490,)
        selectedframe.grid(row = 0, column = 1, padx = 10, pady =5)

        startgame = CTkButton(root,text="Start Game",command= root.destroy)
        startgame.grid(row =2, column =0)

        root.mainloop()

        wait = CTk()
        wait.title("Loading...")
        wait.eval('tk::PlaceWindow . center')
        wait.attributes('-topmost',True)

        ydl_opts = {
                    'quiet': True,
                    'extract_flat': True,
                    'skip_download': True,
                }


        def get_yt_links():
            global links
            global songnames
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                for song in songnames:
                    result = ydl.extract_info(f'ytsearch:{song}', download=False)
                    videos = result['entries']
                    link = "https://www.youtube.com/watch?v="+videos[0]['url']
                    links.append(link)
                    


        def get_tracks_list(artist, artist_id):
            song_list = []
            global sp
            albums = sp.artist_albums(artist_id[15:])
            song = []
            for album in albums["items"]:
                song += sp.album_tracks(album["id"])["items"]
            
            for i in song:

                song_list.append(i['name'] + " - " + artist)
            return song_list

        def song_proccessing_main():
            global songnames
            for artist, artist_id in artistsSelected.items():
                songnames += get_tracks_list(artist,artist_id)

            for i in songnames:
                pop = check_song_popularity(i)
                if pop < POPULARITY_CONSTRAINT:
                    songnames.remove(i)
                    print("Song -",i,"removed due to low popularity")

            if PROFANITY_ALLOWED == False:
                for i in songnames:
                    if profanity.contains_profanity(i):
                        songnames.remove(i)

            for i in songnames:
                for j in EXCLUDE_WORDS:
                    if j.lower() in i.lower():
                        songnames.remove(i)
                        break
            
            for i in songnames:
                for char, rep in EXCLUDE_REPETITION_OF.items():
                    if (i.lower()).count(char.lower()) >= rep:
                        songnames.remove(i)
                        break
            
            random.shuffle(songnames)

            if len(songnames) > 100:
                songnames = songnames[:100]

            threading.Thread(target = get_yt_links,daemon= True).start()
            t.sleep(10)
            waitlabel.configure(text = "Done! Click Continue")
            kill.configure(state = 'normal')



        wait.after(2000,threading.Thread(target=song_proccessing_main,daemon= True).start)

        waitlabel = CTkLabel(wait,text=" Please Wait as the songs are being processed")
        waitlabel.grid(row = 0, column = 0,pady = 10, padx = 15)

        status = CTkLabel(wait,text = "Status :  Initializing")
        status.grid(row = 1, column = 0)

        kill = CTkButton(wait,text = "continue",command=wait.destroy,state="disabled")
        kill.grid(row = 2, column = 0)

        wait.mainloop()

    elif option == "profile":

        
        root = CTk()
        
        CTkLabel(root,text = "Select number of users that need to login").pack()

        def spotify_auth():
            global songnames
            global song_ids_for_seed
            scope = "user-top-read"
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=redirect_uri,scope=scope,show_dialog= True))
            
            for term in ["long_term","short_term","medium_term"]:
                user_top_tracks = sp.current_user_top_tracks(limit=50,time_range=term)
                songnames += [(track['name'] + " - " + track["artists"][0]["name"]) for track in user_top_tracks['items']]
                song_ids_for_seed += [track['id'] for track in user_top_tracks['items']]
            os.remove(".cache")


        def submit():
            
            n = int(num_users.get())
            for i in range(n):
                spotify_auth()
            root.destroy()

        num_users = CTkEntry(root)
        num_users.pack()
        CTkButton(root,text = "Go",command=submit).pack()
        root.mainloop()

        wait = CTk()
        wait.title("Loading...")
        wait.eval('tk::PlaceWindow . center')
        wait.attributes('-topmost',True)

        ydl_opts = {
                    'quiet': True,
                    'extract_flat': True,
                    'skip_download': True,
                }


        def get_yt_links():
            global links
            global songnames
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                for song in songnames:
                    result = ydl.extract_info(f'ytsearch:{song}', download=False)
                    videos = result['entries']
                    link = "https://www.youtube.com/watch?v="+videos[0]['url']
                    links.append(link)
                    


        def get_tracks_list():
            global songnames
            global song_ids_for_seed
            #gets recomendation from spotify ,dont confuse with the one in the if clause
            
            seed_lists = [song_ids_for_seed[5*i:5*i+5] for i in range(0,math.ceil(len(song_ids_for_seed)/5))]

            print(len(seed_lists))
            
            for seed_list in seed_lists:
                recommendations = sp.recommendations(seed_tracks=seed_list, limit=2)
                recommended_songs = [(track['name'] + " - " + track["artists"][0]["name"]) for track in recommendations['tracks']]
                songnames += recommended_songs
                print("Recomedations Generated")



        def song_proccessing_main():
            global songnames
            songnames = list(set(songnames)) #removes dupicates

            print("Songs before recomendation :",len(songnames))
            get_tracks_list()
            print("Songs after recomendation :",len(songnames))

            if PROFANITY_ALLOWED == False:
                for i in songnames:
                    if profanity.contains_profanity(i):
                        songnames.remove(i)

            songnames = list(set(songnames)) #removes dupicates

            random.shuffle(songnames)

            

            if len(songnames) > 100:
                songnames = songnames[:100]

            threading.Thread(target = get_yt_links,daemon= True).start()
            t.sleep(10)
            waitlabel.configure(text = "Done! Click Continue")
            kill.configure(state = 'normal')



        wait.after(2000,threading.Thread(target=song_proccessing_main,daemon= True).start)

        waitlabel = CTkLabel(wait,text=" Please Wait as the songs are being processed")
        waitlabel.grid(row = 0, column = 0,pady = 10, padx = 15)

        status = CTkLabel(wait,text = "Status :  Initializing")
        status.grid(row = 1, column = 0)

        kill = CTkButton(wait,text = "continue",command=wait.destroy,state="disabled")
        kill.grid(row = 2, column = 0)

        wait.mainloop()        




    
CTkLabel(preference, text="How would you like to select songs?").pack()

option_frame = CTkFrame(preference)
option_frame.pack()
    
artist_button = CTkButton(option_frame, text="Select songs by artist", command=partial(select_option,"artist"))
artist_button.grid(row=0, column=0, padx=10, pady=5)

spotify_button = CTkButton(option_frame, text="Select songs from Spotify profile", command=partial(select_option,"profile"))
spotify_button.grid(row=0, column=1, padx=10, pady=5)

preference.mainloop()


counter = 0
answerShown = False
ffplay_process = None

game = CTk()
game.title("Guess The Song!")
game.attributes("-fullscreen", True)
def play_random_segment(youtube_link):
    global timer
    global ffplay_process
    youtube = pytube.YouTube(youtube_link)
    try:
        audio_stream = youtube.streams.filter(only_audio=True).first()
        audio_stream.download()
        start_time = random.randint(10, int(youtube.length))
        ffplay_process = subprocess.Popen(["ffplay", "-nodisp", "-ss", str(start_time-12), "-t", "12", audio_stream.default_filename])
        timer.stop()
        timer.reset_ticks()
        timer.start()
        t.sleep(2)
    except:
        pass
    nextButton.configure(state = "normal")


def stop_song():
    global ffplay_process
    timer.stop()
    if ffplay_process:
        ffplay_process.terminate()
        ffplay_process.wait()

def play_song():
    global ffplay_process
    global links
    global counter
    global timer
    try:
        x = links[counter]
        play_random_segment(links[counter])
    except IndexError:
        answer.configure(text = "Game Over! Thank You for Playing")
        nextButton.configure(state = "disabled")
        exitButton.configure(command = game.destroy)


    
class TimerThread:
    def __init__(self, interval, ticks):
        self.interval = interval
        self.default_ticks = ticks
        self.ticks = ticks
        self._running = False
        self._thread = None

    
    def _run(self):
        while self._running and self.ticks > 0:
            self.ticks -= 1
            t.sleep(self.interval)
            

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run,daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def reset_ticks(self, value=None):
        if value is None:
            value = self.default_ticks
        self.ticks = value

timer = TimerThread(1,12)

def refresh_time():
    global timer
    counterLabel.configure(text = str(timer.ticks))
    if timer.ticks == 0:
        stop_song()
        timer.stop()
    game.after(100, refresh_time)

def confirm_exit():
    confirmExit = CTk()
    confirmExit.title("Confirmation")
    confirmExit.eval('tk::PlaceWindow . center')
    confirmExit.attributes('-topmost',True)
    confirmExit.geometry("380x150")

    def end_game():
        game.destroy()
        confirmExit.destroy()

    labelFrame = CTkFrame(confirmExit)
    labelFrame.pack(pady =10, padx = 15, fill = X)

    buttonFrame = CTkFrame(confirmExit)
    buttonFrame.pack(pady =10, padx = 15, fill = X)

    label = CTkLabel(labelFrame,text = "Are you sure you want to exit?")
    label.pack(fill = X)

    yes = CTkButton(buttonFrame, text = "Exit",command=end_game)
    yes.grid(row = 0,column = 0,padx = 15, pady =10 )

    no = CTkButton(buttonFrame,text = "Cancel",command=confirmExit.destroy)
    no.grid(row = 0, column = 1, padx = 15,pady = 10)
  
    confirmExit.mainloop()

    del confirmExit

def next():
    global ffplay_process
    global counter
    global answerShown
    global timer
    timer.stop()
    timer.reset_ticks()
    if answerShown == False:

        threading.Thread(target=stop_song,daemon=True).start()
        nextButton.configure(text = "Continue")
        answer.configure(text = songnames[counter])
        answerShown = True
        
    else:
        counter +=1
        nextButton.configure(text = "Show Answer",state = "disabled")
        answer.configure(text = "                                                           ")
        threading.Thread(target = play_song,daemon= True).start()
        answerShown = False

def cleanup_recursive():
    cleanup()
    game.after(60000,cleanup_recursive)


questionframe = CTkFrame(game,height=600)
questionframe.pack(fill = X)

counterLabel = CTkLabel(questionframe,text="12",font=CTkFont(size= 325),width = 1350)
counterLabel.pack(fill = BOTH,expand = True)

answerframe = CTkFrame(game, height = 600)
answerframe.pack(fill = X,pady = 10)

nextButton = CTkButton(answerframe, text = "Show Answer",state="disabled",font=CTkFont(size= 22),width = 210,height=37,command=next)
nextButton.pack(pady = 48)

answer = CTkLabel(answerframe,width = 1350,text = "                                                           ",font=CTkFont(size= 45),height = 60)
answer.pack(fill = BOTH,expand = True,pady = 15)

game.after(2000,(threading.Thread(target=play_song,daemon=True)).start)
game.after(2000,refresh_time)
game.after(60000,cleanup_recursive)

exitButton = CTkButton(answerframe, text = 'Exit',command=confirm_exit,font=CTkFont(size= 22),width = 210,height=37)
exitButton.pack(pady = 48)

game.mainloop()


with open('popularity_cahce.dat','wb') as f:
    pickle.dump(popularity_cache,f)

stop_song()
cleanup()