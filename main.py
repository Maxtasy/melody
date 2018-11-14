import tkinter.messagebox
import os
import time
import threading
from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from tkinter import filedialog
from mutagen.mp3 import MP3
from pygame import mixer

# function to get info on current_id
def get_info(current_id):
    try:
        file_path = playlist[current_id]
        file_name = playlist[current_id].split("/")[-1][:-4]
        file_type = playlist[current_id][-4:]
        
        if file_type == ".mp3":
            track_length = MP3(file_path).info.length
        else:
            print("Unknown file_type encountered.")
        
        return file_path, file_name, track_length
    except:
        print("No files to get info from.")

# resets the play time counter
def reset_current_time():
    global current_time
    current_time = 0

# lets us browse the file system to add songs to playlist
def add_file_to_playlist():
    global playlist
    global current_id
    filepath = filedialog.askopenfilename(title = "Select File", filetypes = (("mp3 files","*.mp3"),))
    if filepath:
        filename = filepath.split("/")[-1][:-4]
        playlist_box.insert(len(playlist), filename)
        playlist.append(filepath)
        playlist_box.selection_clear(0, END)
        if not current_id:
            current_id = 0
        playlist_box.selection_set(current_id)

# Lets us add all files in a directory to the playlist
def add_dir_to_playlist():
    global playlist
    global current_id
    directory = filedialog.askdirectory(title = "Select Directory")
    if directory:
        files = os.listdir(directory)
        for file in files:
            filetype = file[-4:]
            if (filetype == ".mp3" or filetype == ".wav"):
                filename = file[:-4]
                playlist_box.insert(len(playlist), filename)
                playlist.append(directory + "/" + file)
        if not current_id:
            current_id = 0
        playlist_box.selection_clear(0, END)
        playlist_box.selection_set(current_id)

# function to remove selected song from playlist
def remove_from_playlist():
    global playlist
    global current_id

    try:
        selected_ids = list(playlist_box.curselection())
        selected_ids.sort(reverse = True)
        
        for selected_id in selected_ids:
            playlist_box.delete(selected_id)
            del playlist[selected_id]
        
        current_id = 0
        playlist_box.selection_clear(0, END)
        playlist_box.selection_set(current_id)
    except:
        tkinter.messagebox.showerror("Delete Error", "No song selected.")

def clear_playlist():
    global playlist
    global current_id
    playlist = []
    current_id = None
    playlist_box.delete(0, END)

def save_playlist():
    global playlist
    if len(playlist) > 0:
        playlist_name = filedialog.asksaveasfilename(title = "Save Playlist", filetypes = (("melody playlist","*.mldpl"),))
        if playlist_name:
            with open(playlist_name + ".mldpl", "w") as f:
                for list_item in playlist:
                    f.write(list_item + "\n")
    else:
        tkinter.messagebox.showerror("Playlist Save Error", "No songs in playlist, can't save.")

def load_playlist():
    global playlist
    global current_id
    playlist_file = filedialog.askopenfilename(title = "Select Playlist", filetypes = (("melody playlist","*.mldpl"),))
    if playlist_file:
        with open(playlist_file, "r") as f:
            list_items = f.read().strip().split("\n")
        # clear playlist
        playlist = []
        playlist_box.delete(0, END)
        for list_item in list_items:
            filename = list_item.split("/")[-1][:-4]
            playlist_box.insert(len(playlist), filename)
            playlist.append(list_item)
        playlist_box.selection_clear(0, END)
        current_id = 0
        playlist_box.selection_set(current_id) 

# play/pause button logic
def play_pause_button_action():
    global playback_status
    global current_id
    if playback_status == "Stopped":
        if len(playlist) == 0:
            add_file_to_playlist()
        else:
            current_id = playlist_box.curselection()[0]
            play(current_id)
    elif playback_status == "Paused":
        resume()
    elif playback_status == "Playing":
        pause()
    else:
        print("Unknown playback_status encountered.")
    update_track_current_time()

# play action logic
def play(current_id):
    global playlist
    global playback_status
    mixer.music.stop()
    mixer.music.load(playlist[current_id])
    mixer.music.play()
    playback_status = "Playing"
    play_pause_button["image"] = pause_button_image
    update_track_length(current_id)
    status_bar["text"] = "Currently playing: " + get_info(current_id)[1]
    progressbar.configure(value = 0)
    progressbar.configure(maximum = get_info(current_id)[2])
    progressbar.start(interval = 1000)
    reset_current_time()

def update_track_current_time():
    global current_id
    track_length = get_info(current_id)[2]
    t1 = threading.Thread(target = counter, args = (track_length,))
    t1.start()

# update track current time
def counter(track_length):
    global playback_status
    global current_time
    while current_time <= track_length and playback_status == "Playing":
        mins, secs = divmod(current_time, 60)
        hours, mins = divmod(mins, 60)
        track_current_time_text["text"] = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), int(round(secs)))
        time.sleep(1)
        current_time += 1
    if playback_status == "Playing":
        play_next_song()

#resume action logic
def resume():
    global playback_status
    global current_time
    mixer.music.unpause()
    play_pause_button["image"] = pause_button_image
    status_bar["text"] = "Currently playing: " + get_info(current_id)[1]
    playback_status = "Playing"
    progressbar.config(value = current_time, maximum = get_info(current_id)[2])
    progressbar.start(interval = 1000)

# pause action logic
def pause():
    global playback_status
    progressbar.stop()
    mixer.music.pause()
    play_pause_button["image"] = play_button_image
    status_bar["text"] = "Paused: " + get_info(current_id)[1]
    playback_status = "Paused"

# play next song in playlist
def play_next_song():
    global playlist
    global current_id
    if current_id != None:
        if current_id >= len(playlist) - 1:
            print("Can't go forward. Already on last track in playlist.")
        else:
            current_id += 1
            update_track_length(current_id)
            playlist_box.selection_clear(0, END)
            playlist_box.selection_set(current_id)
            play(current_id)
            reset_current_time()
    else:
        print("Can't go forward. Playlist is empty.")
    
# play previous song in playlist
def play_previous_song():
    global playlist
    global current_id
    if current_id != None:
        if current_id < 1:
            print("Can't go back. Already on first track in playlist.")
        else:
            current_id -= 1
            update_track_length(current_id)
            playlist_box.selection_clear(0, END)
            playlist_box.selection_set(current_id)
            play(current_id)
            reset_current_time()
    else:
        print("Can't go back. Playlist is empty.")

# rewind to the beginning of the song and play
def rewind():
    global current_id
    if current_id:
        play(current_id)
    else:
        print("Can't rewind. Playlist is empty.")

# stops music playback
def stop():
    global playback_status
    mixer.music.stop()
    play_pause_button["image"] = play_button_image
    status_bar["text"] = "Playback stopped."
    playback_status = "Stopped"
    reset_current_time()
    track_current_time_text["text"] = "00:00:00"
    

# gets value from volume_scale. set_value takes values from 0 - 1
def update_volume(val):
    global is_muted
    global volume
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    if volume == 0:
        toggle_mute_button["image"] = volume_none_button_image
    elif volume < 0.34:
        is_muted = False
        toggle_mute_button["image"] = volume_low_button_image
        is_muted = False
    elif volume < 0.67:
        toggle_mute_button["image"] = volume_mid_button_image
        is_muted = False
    else:
        toggle_mute_button["image"] = volume_high_button_image
        is_muted = False

# mute/unmute logic
def toggle_mute():
    global is_muted
    global volume
    global volume_saved
    if is_muted:
        mixer.music.set_volume(volume_saved)
        volume_scale.set(int(volume_saved * 100))
        if volume < 0.34:
            toggle_mute_button["image"] = volume_low_button_image
        elif volume < 0.67:
            toggle_mute_button["image"] = volume_mid_button_image
        else:
            toggle_mute_button["image"] = volume_high_button_image
        is_muted = False
    else:
        volume_saved = volume
        mixer.music.set_volume(0)
        volume_scale.set(0)
        toggle_mute_button["image"] = volume_none_button_image
        is_muted = True 

# update track total time
def update_track_length(current_id):
    track_length = get_info(current_id)[2]
    
    mins, secs = divmod(track_length, 60)
    hours, mins = divmod(mins, 60)
    track_length_text["text"] = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), int(round(secs)))

# opens info box
def about():
    about_text = "Melody v0.1 by Maxtasy\nBuilt with python, tkinter and pygame.\nIcons from flaticon.com\n\nmaxtasy.me"
    tkinter.messagebox.showinfo("About Melody", about_text)

# stop music and close window
def quit_app():
    global volume
    stop()
    with open("config.cfg", "w") as f:
        f.write(str(volume))
    root.destroy()

# -- main code --

# global variables
playback_status = "Stopped" # Stopped, Playing, Paused
playlist = [] # list of all tracks in the playlist
current_time = 0 # time in current track
current_id = None
is_muted = False # True, False

try:
    with open("config.cfg", "r") as f:
        volume = float(f.read())
        mixer.music.set_volume(volume)
except:
    volume = 0.5 # volume at program start
volume_saved = 0.5 # saved volume for restoring on unmute action

# initialize mixer
mixer.pre_init(44100, -16, 2, 4096)
mixer.init()

# create window (contains menu, main_frame, status_bar)
root = tk.ThemedTk()
root.get_themes()
root.set_theme("arc")

# set window size, add title and logo
#root.geometry("300x300")
root.title("Melody")
root.iconbitmap("img/logo.ico")

# menu bar
menu_bar = Menu(root)
root.config(menu = menu_bar)

# sub menus
sub_menu = Menu(menu_bar, tearoff = 0)
menu_bar.add_cascade(label = "File", menu = sub_menu)
sub_menu.add_command(label = "Add file to playlist...", command = add_file_to_playlist)
sub_menu.add_command(label = "Add directory to playlist...", command = add_dir_to_playlist)
sub_menu.add_separator()
sub_menu.add_command(label = "Save playlist...", command = save_playlist)
sub_menu.add_command(label = "Load playlist...", command = load_playlist)
sub_menu.add_command(label = "Clear playlist...", command = clear_playlist)
sub_menu.add_separator()
sub_menu.add_command(label = "Exit", command = quit_app)

sub_menu = Menu(menu_bar, tearoff = 0)
menu_bar.add_cascade(label = "Help", menu = sub_menu)
sub_menu.add_command(label = "About", command = about)

# add main frame (contains player_frame, playlist_frame)
main_frame = Frame(root)
main_frame.pack()

# add frame for player frame (contains top_frame, middle_frame, bottom_frame)
player_frame = Frame(main_frame)
player_frame.grid(row = 0, column = 1)

# add frame for top part
top_frame = Frame(player_frame)
top_frame.grid(row = 0, column = 0, padx = 10, pady = 10)

# add track current time
track_current_time_text = ttk.Label(top_frame, text = "--:--:--")
track_current_time_text.grid(row = 0, column = 0)

# add progress bar
progressbar = ttk.Progressbar(top_frame, cursor = "hand2")
progressbar.grid(row = 0, column = 1, padx = 10)

# add track total time
track_length_text = ttk.Label(top_frame, text = "--:--:--")
track_length_text.grid(row = 0, column = 2)

# add frame for middle part (main buttons)
middle_frame = Frame(player_frame)
middle_frame.grid(row = 1, column = 0, padx = 10, pady = 10)

# add previous song button
previous_song_button_image = PhotoImage(file = "img/previous_song.png")
previous_song_button = ttk.Button(middle_frame, image = previous_song_button_image, command = play_previous_song)
previous_song_button.grid(row = 0, column = 0)

# add play/pause button
play_button_image = PhotoImage(file = "img/play.png")
pause_button_image = PhotoImage(file = "img/pause.png")
play_pause_button = ttk.Button(middle_frame, image = play_button_image, command = play_pause_button_action)
play_pause_button.grid(row = 0, column = 1)

# add stop button
stop_button_image = PhotoImage(file = "img/stop.png")
stop_button = ttk.Button(middle_frame, image = stop_button_image, command = stop)
stop_button.grid(row = 0, column = 2)

# add next song button
next_song_button_image = PhotoImage(file = "img/next_song.png")
next_song_button = ttk.Button(middle_frame, image = next_song_button_image, command = play_next_song)
next_song_button.grid(row = 0, column = 3)

# add rewind button
rewind_button_image = PhotoImage(file = "img/rewind.png")
rewind_button = ttk.Button(middle_frame, image = rewind_button_image, command = rewind)
rewind_button.grid(row = 1, column = 2)

# add frame for bottom part (mute and volume slider)
bottom_frame = Frame(player_frame)
bottom_frame.grid(row = 2, column = 0, padx = 10, pady = 10)

# add mute button
volume_none_button_image = PhotoImage(file = "img/volume_none_1.png")
volume_low_button_image = PhotoImage(file = "img/volume_low_1.png")
volume_mid_button_image = PhotoImage(file = "img/volume_mid.png")
volume_high_button_image = PhotoImage(file = "img/volume_high.png")

toggle_mute_button = ttk.Button(bottom_frame, image = volume_mid_button_image, command = toggle_mute)
toggle_mute_button.grid(row = 0, column = 0)

# add volume scale and set default volume
volume_scale = ttk.Scale(bottom_frame, from_ = 0, to = 100, orient = HORIZONTAL, command = update_volume)
volume_scale.set(volume*100) # default values are defined at the top
mixer.music.set_volume(volume) # same here
volume_scale.grid(row = 0, column = 1)

# add playlist frame (contains playlist, button_add, button_remove)
playlist_frame = Frame(main_frame)
playlist_frame.grid(row = 0, column = 0, padx = 20)

# add playlist
playlist_box_frame = Frame(playlist_frame)
playlist_box_frame.pack()

scrollbar = Scrollbar(playlist_box_frame, orient=VERTICAL)
scrollbar.pack(side=LEFT, fill=Y, pady = 10)

playlist_box = Listbox(playlist_box_frame, yscrollcommand=scrollbar.set, selectmode=EXTENDED, width = 30)
playlist_box.pack(pady = 5)

scrollbar.config(command=playlist_box.yview)

# button for adding songs to playlist
add_button_image = PhotoImage(file = "img/add.png")
button_add = ttk.Button(playlist_frame, image = add_button_image, command = add_file_to_playlist)
button_add.pack(side = LEFT, padx = 30)

#button for removing playlist items
remove_button_image = PhotoImage(file = "img/remove.png")
button_remove = ttk.Button(playlist_frame, image = remove_button_image, command = remove_from_playlist)
button_remove.pack(side = RIGHT, padx = 10)

# status bar
status_bar = ttk.Label(root, text = "Welcome to Melody v0.1", relief = RIDGE, anchor = W, font = "Arial 10")
status_bar.pack(side = BOTTOM, fill = X)

# overrise default closing (X) button
root.protocol("WM_DELETE_WINDOW", quit_app)

# run main loop
root.mainloop()