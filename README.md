# ExifMapOverlay
The purpose of this tool is to show a simple small map overlay when viewing photos.
Intended as a nice gimmick when reviewing vacation photos.
If a jpeg contains GeoLocation Data, fetch a map and place name from OpenStreetMap and display a small window always on top for a few seconds, then autoclose the map again.

I use IrfanView as image viewer, but I felt it misses this feature (in stock IrfanView, you need to press I🡒E🡒O (Info🡒Exif🡒OpenStreetMap) to view a map in the browser), with this utility, you can just assign it as external editor in IrfanView and then press <kbd>⇧ Shift</kbd> + <kbd>1</kbd> to open the map.

Here is what the overlay looks like:

![Map Overlay of Bichlbach](/doc/ExifMapOverlay_sample.png)

## Usage
Call ExifMapOverlay with the path to a jpeg file as single argument, example: *`ExifMapOverlay.exe 20250829_180640.jpg`*

If you are using IrfanView (such as myself), you can simply set up ExifMapOverlay as am external editor, which will allow you to bring up the overlay from IrfanView by pressing e.g. <kbd>⇧ Shift</kbd> + <kbd>1</kbd>. To do so navigate to Options🡒Properties🡒Miscellaneous and add the path to ExifMapOverlay.exe (e.g. `C:\Users\sayofan\portableApps\ExifMapOverlay.exe`) as one of the external editors. There is no need to add any arguments, as IrfanView will automatically pass the current file name as first argument.

## Compiling
This project uses a slightly modified [Static Map](https://github.com/komoot/staticmap) and [OSMPythonTools](https://github.com/mocnik-science/osm-python-tools). The latter one has quite a few dependecies.
To package into an executable file, I use PyInstaller with

`python -m PyInstaller .\src\exifMapOverlay.py --onedir --noconsole --icon .\scratch\logo.ico`

## Settings
There are a few simple settings like position of the window which are kept in a .json file. The file is stored in the temp folder and will be created upon the first execution of ExifMapOverlay with default parameters.
The contents of the settings file are 
```jsonc
{
    "window_pos_x": 200,
    "window_pos_y": 100,
    "nominatim_language": null,  // null for native names; otherwise a http Accept-Language header (e.g. 'de-DE')
    "tile_server_url_template": "https://tile.osm.org/{z}/{x}/{y}.png",  // # OSM tile server. For a list, see https://wiki.openstreetmap.org/wiki/Raster_tile_providers
    "tile_size_px": 256,  // the side length of the tiles. must be matched to the server. usually 256 or 512.
    "map_zoom_level": 6,  // tile zoom level, see https://wiki.openstreetmap.org/wiki/Zoom_levels
    "map_pixel_size_x": 200,
    "map_pixel_size_y": 200,
    "place_text_font_size": 12,
    "approx_display_time_ms": 6000
}
```

## Remarks
This uses OSMPythonTools to access Nominatim and StaticMap to access map tiles from OpenStreetMap.
Downloaded data is cached as required by OSM when using their APIs. StaticMap was slightly modified to allow for caching. I do not set an expiration date for the cache, it is simply stored in the system's tempfolder.

Please respect the usage policies of any tile server you use.
