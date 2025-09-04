import cx_Freeze

executables = [cx_Freeze.Executable("main.py",base="console",target_name="map-maker.exe")]

cx_Freeze.setup(
    name="Map Maker",
    executables = executables
)
