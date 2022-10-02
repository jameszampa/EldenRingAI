from asyncio import subprocess


import os
import time
import subprocess


def _start_elden_ring(path_elden_ring):
    subprocess.run([path_elden_ring])


def _stop_elden_ring(path_elden_ring):
    os.system("taskkill /im eldenring.exe")


path_elden_ring = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\ELDEN RING\\Game\\eldenring.exe'
_start_elden_ring(path_elden_ring)
time.sleep(60)
_stop_elden_ring(path_elden_ring)

