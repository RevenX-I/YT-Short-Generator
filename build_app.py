
import PyInstaller.__main__
import os
import shutil

print("Preparing Build...")

# Define assets to include (Source, Destination)
datas = [
    ('assets', 'assets'),
    ('fonts', 'fonts'),
    ('songs', 'songs'),
    ('src', 'src'),
    ('.env', '.'),
    ('main.py', '.'),
]

# Construct --add-data flags
add_data_flags = []
sep = ';' if os.name == 'nt' else ':'
for src, dest in datas:
    if os.path.exists(src):
        # PyInstaller format: source;dest
        add_data_flags.append(f'--add-data={src}{sep}{dest}')
    else:
        print(f"Warning: {src} not found, skipping...")

# PyInstaller Arguments
args = [
    'launcher.py',                  # Entry Point
    '--name=ShortsGPT_Premium',     # Exe Name
    '--onefile',                    # Single .exe file
    '--clean',                      # Clean cache
    '--hidden-import=streamlit',
    '--hidden-import=altair',
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=moviepy',
    '--hidden-import=dotenv',
    '--hidden-import=moviepy.audio.fx.all', # Fix for moviepy missing fx
    '--collect-all=streamlit',      # Grab all Streamlit dependencies
    '--collect-all=moviepy',        # Grab all MoviePy dependencies
    '--collect-all=proglog',
    '--collect-all=imageio',
    '--collect-all=imageio_ffmpeg', # Ensure ffmpeg binds
] + add_data_flags

print("Running PyInstaller (This may take 2-3 minutes)...")
PyInstaller.__main__.run(args)

print("\n" + "="*50)
print(f"Build Complete! Check the 'dist' folder.")
print("="*50 + "\n")
