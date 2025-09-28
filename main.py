import os 
import cv2
import json
import sys
import math

isFrozen = getattr(sys,"frozen",False)

dir_path = os.path.dirname(sys.executable) if isFrozen else os.path.dirname(os.path.realpath(__file__))
args = sys.argv

imageGrid = None
saveDirectory = dir_path
pathToImage = ""
cellSize = 0.5
modelHeight = 2
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
    normals = []

    def add_face(verts):
        """verts: list of 4 [x, y, z]"""
        idx_start = len(vertices) + 1
        vertices.extend(verts)

        # normal from first 3 verts
        n = compute_normal(verts[0], verts[1], verts[2])
        normals.append(n)
        n_idx = len(normals)

        # two triangles, with normals
        faces.append([(idx_start, n_idx), (idx_start+1, n_idx), (idx_start+2, n_idx)])
        faces.append([(idx_start, n_idx), (idx_start+2, n_idx), (idx_start+3, n_idx)])
        
    def normalize(v):
        length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        return [v[0]/length, v[1]/length, v[2]/length] if length > 0 else [0,0,0]

    def compute_normal(v1, v2, v3):
        # Cross product (v2-v1) x (v3-v1)
        uz, uy, ux = v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]
        vz, vy, vx = v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2]
        return normalize([uy*vz - uz*vy,
                        uz*vx - ux*vz,
                        ux*vy - uy*vx])

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
                        
    ground_y = 0  # same as wall bottom
    ground = [
        [0, ground_y, 0],
        [cols * cell_size, ground_y, 0],
        [cols * cell_size, ground_y, rows * cell_size],
        [0, ground_y, rows * cell_size],
    ]
    idx_start = len(vertices) + 1
    vertices.extend(ground)
    normal = [0, 1, 0]  
    normals.append(normal)
    n_idx = len(normals)

    faces.append([(idx_start, n_idx), (idx_start + 1, n_idx), (idx_start + 2, n_idx)])
    faces.append([(idx_start, n_idx), (idx_start + 2, n_idx), (idx_start + 3, n_idx)])
    faces.append([(idx_start+2, n_idx), (idx_start + 1, n_idx), (idx_start, n_idx)])
    faces.append([(idx_start+3, n_idx), (idx_start + 2, n_idx), (idx_start, n_idx)])

    
    return {"vertices": vertices, "faces": faces, "normals": normals}

def saveFiles():
    global imageGrid, saveDirectory, cellSize, modelHeight, objFilename, gridFilename
    
    mesh = generateObjFromGrid(imageGrid,cellSize,modelHeight)
    
    # Write OBJ file
    with open(os.path.join(saveDirectory,objFilename), "w") as f:
        for v in mesh["vertices"]:
            f.write(f"v {v[2]} {v[1]} {v[0]}\n")
        for n in mesh["normals"]:
            f.write(f"vn {n[0]} {n[1]} {n[2]}\n")
        for face in mesh["faces"]:
            # face is list of (vertex_index, normal_index)
            f.write("f " + " ".join(f"{vi}//{ni}" for vi,ni in face) + "\n")

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
