import os 
import cv2
import json
import sys

isFrozen = getattr(sys,"frozen",False)

dir_path = os.path.dirname(sys.executable) if isFrozen else os.path.dirname(os.path.realpath(__file__))
args = sys.argv

imageGrid = None
saveDirectory = dir_path
pathToImage = ""
cellSize = 0.1
modelHeight = 0.5
objFilename = "model.obj"
gridFilename = "grid.json"

def getGridFromImage(pathToImage):
    
    img = cv2.imread(pathToImage,0)
    rows,cols = img.shape

    imageGrid = []
    for i in range(rows):
        imageGrid.append([])
        for j in range(cols):
            imageGrid[i].append(1 if img[i,j] else 0) #black pixels are tiles
    
    return imageGrid

def generateObjFromGrid(grid, cell_size=1.0, height=1.0):
    rows = len(grid)
    cols = len(grid[0])
        
    vertices = []
    faces = []

    def add_face(verts):
        """verts: list of 4 [x, y, z]"""
        idx_start = len(vertices) + 1
        vertices.extend(verts)
        # two triangles per quad
        faces.append([idx_start, idx_start + 1, idx_start + 2])
        faces.append([idx_start, idx_start + 2, idx_start + 3])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                x = c * cell_size
                z = r * cell_size
                y = 0

                # cube corners
                bottom = [
                    [x, y, z],
                    [x + cell_size, y, z],
                    [x + cell_size, y, z + cell_size],
                    [x, y, z + cell_size],
                ]
                top = [
                    [x, y + height, z],
                    [x + cell_size, y + height, z],
                    [x + cell_size, y + height, z + cell_size],
                    [x, y + height, z + cell_size],
                ]

                # top + bottom
                add_face(top)
                add_face(bottom[::-1])  # flip bottom winding

                # neighbors (dx, dz, face)
                neighbors = [
                    (0, -1, [bottom[0], bottom[1], top[1], top[0]]),  # front
                    (1, 0, [bottom[1], bottom[2], top[2], top[1]]),  # right
                    (0, 1, [bottom[2], bottom[3], top[3], top[2]]),  # back
                    (-1, 0, [bottom[3], bottom[0], top[0], top[3]]), # left
                ]

                for dx, dz, face in neighbors:
                    nr = r + dz
                    nc = c + dx
                    if nr < 0 or nr >= rows or nc < 0 or nc >= cols or grid[nr][nc] == 1:
                        add_face(face)

    return {"vertices": vertices, "faces": faces}

def saveFiles():
    global imageGrid, saveDirectory, cellSize, modelHeight, objFilename, gridFilename
    
    mesh = generateObjFromGrid(imageGrid,cellSize,modelHeight)
    
    # Write OBJ file
    with open(os.path.join(saveDirectory,objFilename), "w") as f:
        for v in mesh["vertices"]:
            f.write(f"v {v[2]} {v[1]} {v[0]}\n")
        for face in mesh["faces"]:
            f.write(f"f {' '.join(str(i) for i in face)}\n")

    print(f"OBJ file saved as {objFilename}")
    
    # Write Grid file
    with open(os.path.join(saveDirectory,gridFilename), "w") as f:
        json.dump({"grid":imageGrid},f)

    print(f"Grid file saved as {gridFilename}")   

    return

def getNextArg():

    global args
    try:
        return args.pop(0)
    except IndexError:
        return None

def main():
    global saveDirectory, imageGrid, pathToImage, cellSize, modelHeight, objFilename, gridFilename
    
    getNextArg()
    
    arg = getNextArg()
    if not arg:
        return
    
    if arg == "help":
        print("Usage: python main.py [pathToImage]* [saveDirectory] [cellSize] [modelHeight] [objFilename] [gridFilename]")
        print("Arguments annotated with '*' are required")
        print("\nDefaults")
        print(f"saveDirectory:\t{saveDirectory}\ncellSize:\t{cellSize}\nmodelHeight:\t{modelHeight}\nobjFilename:\t{objFilename}\ngridFilename:\t{gridFilename}")
        return
    else:
        pathToImage = arg
        
    saveDirectory = getNextArg() or os.path.abspath(saveDirectory)
    if not saveDirectory:
        return
    
    if not os.path.exists(saveDirectory):
        print("Save Directory does not exist")
        return
        
    cellSize = getNextArg() or cellSize
    try:
        float(cellSize)
    except ValueError:
        print("cellSize must be a number")
        return
    cellSize = float(cellSize)
    
    modelHeight = getNextArg() or modelHeight
    try:
        float(modelHeight)
    except ValueError:
        print("modelHeight must be a number")
        return
    modelHeight = float(modelHeight)
    
    objFilename = getNextArg() or objFilename
    if objFilename.split(".")[-1] != "obj":
        print("objFilename extension must be .obj")
        return
    
    gridFilename = getNextArg() or gridFilename
    if gridFilename.split(".")[-1] != "json":
        print("gridFilename extension must be .json")
        return
    
    imageGrid = getGridFromImage(pathToImage)
    
    saveFiles()
    

if __name__ == "__main__":
    main()
