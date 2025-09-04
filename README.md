# ExifMapOverlay
The purpose of this tool is to show a simple small map overlay when viewing photos.
Intended as a nice gimmick when reviewing vacation photos.
If a jpeg contains GeoLocation Data, fetch a map and place name from OpenStreetMap and display a small window always on top for a few second, then autoclose the map again.

I use IrfanView as image viewer, but I felt it misses this feature (in stock IrfanView, you need to press I->E->O (Info->Exif->OpenStreetMap) to view a map in the browser), with this utility, you can just assign it as external editor in IrfanView and then press e.g. shift+1 to open the map.

## Usage
Call ExifMapOverlay with the path to a jpeg file as single argument, example: *`ExifMapOverlay.exe 20250829_180640.jpg`*

## Settings
I plan to include a few settings in an ini file.

## Remarks
This uses OSMPythonTools to access Nomatim and StaticMap to access map tiles from OpenStreetMap.
Downloaded data is cached as required by OSM when using their APIs. I do not set an expiration date for the cache, it is simply stored in the systems tempfolder.
