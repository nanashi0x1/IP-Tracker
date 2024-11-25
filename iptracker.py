import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import folium
import webbrowser
import sqlite3
from datetime import datetime
import os
import re
import tempfile

class iptrackerapp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Address Tracker")
        self.root.geometry("800x600")
        self.databasesetup()
        self.map_file = None
        self.setupui()
        root.protocol("WM_DELETE_WINDOW", self.cleanupandclose)

    def databasesetup(self):
        conn = sqlite3.connect('ip_tracker.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_address TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        result_data TEXT)''')
        conn.commit()
        conn.close()

    def setupui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(sticky=(tk.W, tk.E, tk.N, tk.S))
        self.createsearchsection(main_frame)
        self.createresultssection(main_frame)
        self.createhistorysection(main_frame)
        self.createmapbutton(main_frame)

    def createsearchsection(self, parent):
        search_frame = ttk.LabelFrame(parent, text="Search IP Address")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=5)
        self.ip_entry = ttk.Entry(search_frame, width=40)
        self.ip_entry.grid(row=0, column=0, padx=5, pady=5)
        search_button = ttk.Button(search_frame, text="Track", command=self.trackip)
        search_button.grid(row=0, column=1, padx=5, pady=5)

    def createresultssection(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.grid(row=1, column=0, sticky=tk.NSEW, pady=5)
        self.results = {}
        fields = ['IP', 'City', 'Region', 'Country', 'ISP', 'Timezone', 'Coordinates']
        for index, field in enumerate(fields):
            label = ttk.Label(results_frame, text=f"{field}:")
            label.grid(row=index, column=0, sticky=tk.W, padx=5, pady=2)
            value_label = ttk.Label(results_frame, text="N/A")
            value_label.grid(row=index, column=1, sticky=tk.W, padx=5, pady=2)
            self.results[field.lower()] = value_label

    def createhistorysection(self, parent):
        history_frame = ttk.LabelFrame(parent, text="Search History")
        history_frame.grid(row=1, column=1, sticky=tk.NSEW, pady=5)
        self.history_list = tk.Listbox(history_frame, height=10)
        self.history_list.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_list.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.history_list.configure(yscrollcommand=scrollbar.set)
        self.history_list.bind("<Double-1>", self.loadhistoryitem)
        self.updatehistory()

    def createmapbutton(self, parent):
        map_frame = ttk.Frame(parent)
        map_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.map_button = ttk.Button(map_frame, text="View on Map", command=self.showmap, state=tk.DISABLED)
        self.map_button.pack(pady=5)

    def trackip(self):
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showerror("Error", "Please enter an IP address.")
            return
        if not self.validateip(ip_address):
            messagebox.showerror("Error", "Invalid IP address format.")
            return
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}')
            data = response.json()
            if data['status'] == 'success':
                self.updateresults(data)
                self.storeserachindb(ip_address, data)
                self.createmap(data)
                self.updatehistory()
                self.map_button['state'] = tk.NORMAL
            else:
                messagebox.showerror("Error", data.get('message', 'Unknown API error.'))
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Network error: {e}")

    def validateip(self, ip):
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)

    def updateresults(self, data):
        fields = {
            'ip': 'query',
            'city': 'city',
            'region': 'regionName',
            'country': 'country',
            'isp': 'isp',
            'timezone': 'timezone',
            'coordinates': lambda d: f"{d.get('lat')}, {d.get('lon')}"
        }
        for key, value in fields.items():
            text = data.get(value) if isinstance(value, str) else value(data)
            self.results[key].config(text=text or 'N/A')

    def createmap(self, data):
        lat, lon = data.get('lat'), data.get('lon')
        if lat and lon:
            map_obj = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker([lat, lon], popup=f"{data.get('city')}, {data.get('country')}").add_to(map_obj)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            map_obj.save(temp_file.name)
            self.map_file = temp_file.name

    def showmap(self):
        if self.map_file and os.path.exists(self.map_file):
            webbrowser.open(f'file://{self.map_file}')
        else:
            messagebox.showerror("Error", "Map file is unavailable.")

    def storeserachindb(self, ip, data):
        conn = sqlite3.connect('ip_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO search_history (ip_address, result_data) VALUES (?, ?)", (ip, json.dumps(data)))
        conn.commit()
        conn.close()

    def updatehistory(self):
        conn = sqlite3.connect('ip_tracker.db')
        c = conn.cursor()
        c.execute("SELECT ip_address, timestamp FROM search_history ORDER BY timestamp DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        self.history_list.delete(0, tk.END)
        for ip, timestamp in rows:
            self.history_list.insert(tk.END, f"{ip} - {timestamp}")

    def loadhistoryitem(self, event):
        selection = self.history_list.curselection()
        if not selection:
            return
        selected_item = self.history_list.get(selection[0])
        ip = selected_item.split(" - ")[0]
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, ip)
        self.trackip()

    def cleanupandclose(self):
        if self.map_file and os.path.exists(self.map_file):
            os.remove(self.map_file)
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = iptrackerapp(root)
    root.mainloop()
    