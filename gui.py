from customtkinter import *
from PIL import Image, ImageDraw, ImageColor, ImageGrab, ImageTk
from io import BytesIO
import win32clipboard
import os 
import cv2
import json

dir_path = os.path.dirname(os.path.realpath(__file__))

imageGrid = None

root = CTk()
root.title("Robot Map Maker")
root.geometry("500x335")
root.resizable(False,False)


cellSize = StringVar()
modelHeight = StringVar()
objFilename = StringVar()
gridFilename = StringVar()

cellSize.set("1")
modelHeight.set("1")
objFilename.set("model.obj")
gridFilename.set("grid.json")


def selectFiles():
    global imageGrid, saveFilesButton
    image = filedialog.askopenfilename(title='Open a file',initialdir=dir_path,filetypes=(('PNG Files', '*.png'),))

    if not image:
        return
    
    else:
        img = cv2.imread(image,0)
        rows,cols = img.shape

        imageGrid = []
        for i in range(rows):
            imageGrid.append([])
            for j in range(cols):
                imageGrid[i].append(0 if img[i,j] else 1) #black pixels are tiles
        
        print("Generated grid from image")
        saveFilesButton.configure(state="normal")




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
            if grid[r][c] == 1:
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
                    if nr < 0 or nr >= rows or nc < 0 or nc >= cols or grid[nr][nc] == 0:
                        add_face(face)

    return {"vertices": vertices, "faces": faces}


def saveFiles():
    
    
    try:
        float(cellSize.get())
    except ValueError as e:
        print("Cell size must be number")
        return
        
    try:
        float(modelHeight.get())
    except ValueError as e:
        print("Model height must be number")
        return
    
    mesh = generateObjFromGrid(imageGrid,float(cellSize.get()),float(modelHeight.get()))
    
    dir = filedialog.askdirectory(initialdir=dir_path,title="Select folder to save files")
    
    if not dir:
        print("Directory Error")
        return
    
    
    # Write OBJ file
    with open(dir+"/"+objFilename.get(), "w") as f:
        for v in mesh["vertices"]:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in mesh["faces"]:
            f.write(f"f {' '.join(str(i) for i in face)}\n")

    print(f"OBJ file saved as {objFilename.get()}")
    
    # Write Grid file
    with open(dir+"/"+gridFilename.get(), "w") as f:
        json.dump({"grid":imageGrid},f)

    print(f"Grid file saved as {gridFilename.get()}")   

    return


selectFilesButton = CTkButton(root,text="Select Files",command=selectFiles)
selectFilesButton.pack(pady=20)

optionsFrame = CTkFrame(root)
optionsFrame.pack(expand=True,fill="both",padx=20,pady=(0,20))

CTkLabel(optionsFrame,text="OBJ Model Options",font=("Arial",20)).pack(pady=(5,0))

sizeOptionsFrame = CTkFrame(optionsFrame,fg_color="transparent")
sizeOptionsFrame.pack()

containerFrame = CTkFrame(sizeOptionsFrame)
containerFrame.pack(side="left",padx=(0,20))

CTkLabel(containerFrame,text="Cell Size").pack(pady=(20,0))
cellSizeEntry = CTkEntry(containerFrame,placeholder_text="Cell Size",textvariable=cellSize)
cellSizeEntry.pack()

containerFrame = CTkFrame(sizeOptionsFrame)
containerFrame.pack(side="right",padx=(20,0))

CTkLabel(containerFrame,text="Model Height").pack(pady=(20,0))
modelHeightEntry = CTkEntry(containerFrame,placeholder_text="Model Height",textvariable=modelHeight)
modelHeightEntry.pack()


nameOptionsFrame = CTkFrame(optionsFrame,fg_color="transparent")
nameOptionsFrame.pack()

containerFrame = CTkFrame(nameOptionsFrame)
containerFrame.pack(side="left",padx=(0,20))

CTkLabel(containerFrame,text="Obj filename").pack(pady=(20,0))
objNameEntry = CTkEntry(containerFrame,placeholder_text="Obj filename (model.obj)",textvariable=objFilename)
objNameEntry.pack()

containerFrame = CTkFrame(nameOptionsFrame)
containerFrame.pack(side="right",padx=(20,0))

CTkLabel(containerFrame,text="Grid JSON filename").pack(pady=(20,0))
gridNameEntry = CTkEntry(containerFrame,placeholder_text="Grid JSON filename (grid.json)",textvariable=gridFilename)
gridNameEntry.pack()

saveFilesButton = CTkButton(optionsFrame,text="Save files",command=saveFiles,state=DISABLED)
saveFilesButton.pack(pady=20)


root.mainloop()
