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
    if not os.access(file_path, os.R_OK):
        m = StaticMap(200, 200, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')
        marker = CircleMarker((lon, lat), "#0037FFFF", 12)
        m.add_marker(marker)
        image = m.render(zoom=zoom_factor)
        image.save(file_path)
    return file_path

def get_temp_map_name(lat, lon, zoom_factor):
    temp_dir = os.path.join(tempfile.gettempdir(), 'ExifMapper')
    file_name = f"{lat:.7f}_{lon:.7f}_zoom{zoom_factor}.png"  # 7 decimaly ~ 0.1m
    file_path = os.path.join(temp_dir, file_name)
    return file_path
    

def get_name_from_coordinates(lat, lon) -> str:
    temp_dir = os.path.join(tempfile.gettempdir(), 'ExifMapper')
    CachingStrategy.use(JSON, cacheDir=temp_dir)
    nominatim = Nominatim()
    nomQuery = nominatim.query(lat, lon, reverse=True)
    try:
        return nomQuery.address()['village']
    except KeyError:
        return nomQuery.address()['city']
    # ToDo: parse some more info and handle more fields, like country, town, neighourhood


def borderless(image_path, place_name):
    root = tk.Tk()
    root.attributes('-alpha', 0.0) #For icon
    root.iconify()
    window = tk.Toplevel(root)
    window.attributes("-topmost", True)
    # window.after(10000, lambda: root.destroy())  # autoclose after 10s #ToDo: add (small) timerbar
    # ToDo: make windiw draggable, save position in inifile
    # ToDo: add osm credits below image
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
    label = tk.Label(window, image=img)
    label.pack()
    frame.pack(expand=True, fill='none')
    # add second label with text
    txt_label = tk.Label(window, text=place_name, font=("Arial", 12))
    txt_label.pack(pady=2)
    # ToDo: match font size, padding window size etc

    pos_x = 200
    pos_y = 100
    window.geometry(f"{img.width()}x{img.height()+37}+{pos_x}+{pos_y}")
    # window.geometry(f"{img.width()}x{img.height()+37}")
    window.overrideredirect(1) #Remove border - do not use overrideredirect directly on root as it will remove taskbar icon as well 
    # window.after(10000, lambda: root.destroy())  # autoclose after 10s #ToDo: add (small) timerbar
    total_time = 8000  # in ms - the actual time will probably be a bit longer than that due to overhead in functioncalls
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
    # ToDo: Credit OpenStreetMap
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