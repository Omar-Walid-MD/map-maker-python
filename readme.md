# Tool to turn Black and White PNG into a JSON Grid and 3D Model for Pathfinding

## How to use

1. Install the following Python packages:
    - opencv-python
    - cx_Freeze
2. Build the executables:
    ```python setup.py build```

3. Run the exectuable:

    Windows Command: ```map-maker.exe path/to/map.png```

    Linux Command: ```./map-maker path/to/map.png```

## Inputs: 
A simple Black and White Pixel Grid in PNG format (See example.png)

## Arguments (in order):
```[pathToImage]* [saveDirectory] [cellSize] [modelHeight] [objFilename] [gridFilename]```
 
 - **pathToImage:** path to PNG image (required)
 - **saveDirectory:** directory to save output files
 - **cellSize:** size of a single grid cell in **meters** (default is 0.5 meters)
 - **modelHeight:** height of the 3D Model in **meters** (default is 2 meters)
 - **objFilename:** name of the saved obj file (default is model.obj - must be .obj)
 - **gridFilename:** name of the saved grid file (default is grid.json - must be .json)

