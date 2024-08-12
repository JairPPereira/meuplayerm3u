import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import vlc
import requests
import re

class M3UPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U Player")
        self.root.geometry("600x400")

        self.playlist = {}
        self.current_category = None
        self.current_index = 0

        self.media_player = vlc.MediaPlayer()

        self.create_widgets()

    def create_widgets(self):
        self.open_button = tk.Button(self.root, text="Open M3U URL", command=self.open_m3u_url)
        self.open_button.pack(pady=10)

        self.category_label = tk.Label(self.root, text="Categories:")
        self.category_label.pack(pady=5)

        self.category_listbox = tk.Listbox(self.root)
        self.category_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        self.channel_label = tk.Label(self.root, text="Channels:")
        self.channel_label.pack(pady=5)

        self.channel_frame = tk.Frame(self.root)
        self.channel_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.channel_listbox = tk.Listbox(self.channel_frame)
        self.channel_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.channel_listbox.bind('<<ListboxSelect>>', self.on_channel_select)

        self.play_button = tk.Button(self.channel_frame, text="Play", command=self.play_selected)
        self.play_button.pack(side=tk.RIGHT, padx=5)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.control_frame, text="Next", command=self.next_track)
        self.next_button.pack(side=tk.LEFT, padx=5)

    def open_m3u_url(self):
        url = simpledialog.askstring("Enter M3U URL", "URL:")
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                self.parse_m3u(response.text)
                self.update_category_listbox()
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to load M3U file: {e}")

    def parse_m3u(self, content):
        self.playlist = {}
        current_category = None
        current_channel = None

        for line in content.splitlines():
            line = line.strip()
            if line.startswith("#EXTINF"):
                match = re.search(r'tvg-name="([^"]*)".*group-title="([^"]*)".*,(.*)', line)
                if match:
                    channel_name = match.group(1)
                    category = match.group(2)
                    display_name = match.group(3)

                    if category not in self.playlist:
                        self.playlist[category] = []

                    current_category = category
                    current_channel = {'name': display_name, 'url': None}
                    self.playlist[category].append(current_channel)
            elif line and not line.startswith('#'):
                if current_channel:
                    current_channel['url'] = line

    def update_category_listbox(self):
        self.category_listbox.delete(0, tk.END)
        for category in self.playlist:
            self.category_listbox.insert(tk.END, category)

    def update_channel_listbox(self, category):
        self.channel_listbox.delete(0, tk.END)
        for channel in self.playlist[category]:
            self.channel_listbox.insert(tk.END, channel['name'])

    def on_category_select(self, event):
        selected_index = self.category_listbox.curselection()
        if selected_index:
            self.current_category = self.category_listbox.get(selected_index)
            self.update_channel_listbox(self.current_category)

    def on_channel_select(self, event):
        selected_index = self.channel_listbox.curselection()
        if selected_index:
            self.current_index = selected_index[0]

    def play_selected(self):
        if self.current_category and self.playlist[self.current_category]:
            self.current_index = self.channel_listbox.curselection()[0]
            self.play()

    def play(self):
        if self.current_category and self.playlist[self.current_category]:
            channel = self.playlist[self.current_category][self.current_index]
            media = vlc.Media(channel['url'])
            self.media_player.set_media(media)
            self.media_player.play()

    def stop(self):
        self.media_player.stop()

    def next_track(self):
        if self.current_category and self.playlist[self.current_category]:
            self.current_index = (self.current_index + 1) % len(self.playlist[self.current_category])
            self.play()

if __name__ == "__main__":
    root = tk.Tk()
    app = M3UPlayer(root)
    root.mainloop()
