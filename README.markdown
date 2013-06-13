FAA FAR 77 Surface Generation [Python Toolbox]
============================================

## Requirements ##

* [ArcGIS Desktop]
	* [3D Analyst] License
	* [Aeronautical Solution Extension]

## `LineToFar77` tool ##

### Parameters ###

* Runway Line (String)
	* A list of numbers separated by commas, spaces, or semicolons. There should be four numbers in the string.
* Runway Spatial Reference (Optional, defaults to `3857`)
* Elevation Layer
* Is Prepared Hard Surface (Optional, defaults to `False`)
* Runway Type. One of the following values:
	* `Visual Runway Visual Approach`
	* `Utility Runway Visual Approach`
	* `Utility Runway Non Precision Instrument Approach`
	* `Precision Instrument Runway`
	* `Non Precision Instrument Runway High Visibility`
	* `Non Precision Instrument Runway Approach Low Visibility`
* Output Feature Class (Output)

[Python Toolbox]: http://resources.arcgis.com/en/help/main/10.1/0015/001500000022000000.htm
[ArcGIS Desktop]: http://www.esri.com/software/arcgis/arcgis-for-desktop
[3D Analyst]: http://www.esri.com/software/arcgis/extensions/3danalyst/
[Aeronautical Solution Extension]: http://www.esri.com/software/arcgis/extensions/aero-solution/
