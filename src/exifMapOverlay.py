#!"D:/Conda/envs/osm/python.exe"

from tkinter import ttk
from PIL import Image
from PIL.ExifTags import TAGS
from staticmap import StaticMap, CircleMarker
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.cachingStrategy import CachingStrategy, JSON
import tempfile
import tkinter as tk
from tkinter import PhotoImage

import os
import sys

AppName = 'ExifMapOverlay'
result_language = 'de-DE'

def get_coordinates(filename):
    # ToDp: handle missing file and missing exif data
    image = Image.open(filename)
    exifdict = image._getexif()
    gps_dict = exifdict[34853]
    lat_sign = gps_dict[1]
    lat = gps_dict[2][0] + 1/60. * gps_dict[2][1] + 1/3600. * gps_dict[2][2]
    lon_sign = gps_dict[3]
    lon = gps_dict[4][0] + 1/60. * gps_dict[4][1] + 1/3600. * gps_dict[4][2]
    if "-" == lat_sign:
        lat = -lat
    if "-" == lon_sign:
        lon = -lon
    return (lat, lon)

def print_image(lat: float, lon: float, zoom_factor: int) -> str:
    file_path = get_temp_map_name(lat, lon, zoom_factor)
    if not os.access(os.path.join(tempfile.gettempdir(), AppName), os.R_OK):
        os.mkdir(os.path.join(tempfile.gettempdir(), AppName))
    if not os.access(file_path, os.R_OK):
        native_tiles_url = 'http://a.tile.osm.org/{z}/{x}/{y}.png'
        german_tiles_url = 'https://tile.openstreetmap.de/{z}/{x}/{y}.png'  # for a list, see https://wiki.openstreetmap.org/wiki/Raster_tile_providers
        m = StaticMap(200, 200, url_template=german_tiles_url)
        marker = CircleMarker((lon, lat), "#0037FFFF", 12)
        m.add_marker(marker)
        image = m.render(zoom=zoom_factor)
        image.save(file_path)
    return file_path

def get_temp_map_name(lat, lon, zoom_factor):
    temp_dir = os.path.join(tempfile.gettempdir(), AppName)
    file_name = f"{lat:.6f}_{lon:.6f}_zoom{zoom_factor}.png"  # 6 decimally ~ 0.1m
    file_path = os.path.join(temp_dir, file_name)
    return file_path
    

def get_name_from_coordinates(lat, lon) -> str:
    temp_dir = os.path.join(tempfile.gettempdir(), AppName)
    CachingStrategy.use(JSON, cacheDir=temp_dir)
    nominatim = Nominatim()
    nomQuery = nominatim.query(lat, lon, reverse=True, params={'accept-language': result_language})
    hamlet = ""
    village = ""
    town = ""
    city = ""
    country = ""
    try:
        hamlet = nomQuery.address()['hamlet']
    except KeyError:
        pass
    try:
        village = nomQuery.address()['village']
    except KeyError:
        pass
    try:
        town = nomQuery.address()['town']
    except KeyError:
        pass
    try:
        city = nomQuery.address()['city']
    except KeyError:
        pass
    try:
        country = nomQuery.address()['country']
    except KeyError:
        pass
    city_or_town = city if city!="" else town  # town may be empty still
    village_or_hamlet = village if village!="" else hamlet  # hamlet may be empty still
    return village_or_hamlet + " " + city_or_town + "\n" + country  # ToDo: make some distinctions on what to display - show country below
    # ToDo: parse some more info and handle more fields, like country, town, neighourhood
    # ToDo: query existence of different fields and display accordung to that

class FloatingWindow(tk.Toplevel):
    # https://stackoverflow.com/questions/4055267/tkinter-mouse-drag-a-window-without-borders-eg-overridedirect1#
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")


def borderless(image_path, place_name):
    root = tk.Tk()
    root.attributes('-alpha', 0.0) #For icon
    root.iconify()
    window = FloatingWindow(root)
    window.attributes("-topmost", True)
    # ToDo: save position of window in inifile
    # ToDo: make osm credits below image nicer
    # toDo: possibly add small worldmap in corner (separate panel in front of normal map)

        # Load the image
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return
    try:
        img = PhotoImage(file=image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    #####
    # progressbar
    # frame
    frame = ttk.Frame(window, width=img.width(), height=4)  # set your desired dimensions here
    # frame.pack(expand=True, fill='none')
    frame.pack_propagate(False)  # allows you to explicitly set the dimensions of the frame
    pb = ttk.Progressbar(
        frame,
        orient='horizontal',
        mode='determinate',
        length=img.width(),
    )
    pb.pack(expand=True, fill='both')
    pb.step(99.99)

    #####

    # Create a label to display the image
    label = tk.Label(window, text='© OpenStreetMap', image=img, compound='top', justify='left', font=("TkDefaultFont", 8))
    label.pack()
    frame.pack(expand=True, fill='none')
    # add second label with text
    txt_label = tk.Label(window, text=place_name, font=("TkDefaultFont", 12))
    txt_label.pack(pady=2)
    txt_label.config(wraplength=img.height())
    # ToDo: match font size, padding window size etc

    pos_x = 200
    pos_y = 100
    window.geometry(f"{img.width()}x{img.height()+2*34+10}+{pos_x}+{pos_y}")
    window.overrideredirect(True) #Remove border - do not use overrideredirect directly on root as it will remove taskbar icon as well 

    label.bind("<ButtonPress-1>", window.start_move)
    label.bind("<ButtonRelease-1>", window.stop_move)
    label.bind("<B1-Motion>", window.do_move)

    total_time = 6000  # in ms - the actual time will probably be a bit longer than that due to overhead in functioncalls
    delay_ms = 50 # increasing this / reducing fps should probably decrease overhead
    step = 100 / (total_time/delay_ms)
    def animate_progressbar():
        if pb['value'] > (0+step):
            pb['value'] -= step
            window.after(delay_ms, animate_progressbar)
        else:
            root.destroy()
    window.after(0, animate_progressbar)
    window.mainloop()

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    coords = get_coordinates(file_path)
    png_path = print_image(coords[0], coords[1], 6)
    name = get_name_from_coordinates(coords[0], coords[1])
    borderless(png_path, name)
    

if __name__ == "__main__":
    main()