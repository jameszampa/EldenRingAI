#!/bin/bash

export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.steam/steam"
cd /home/james/.local/share/Steam/steamapps/compatdata/1245620/pfx
STEAM_COMPAT_DATA_PATH="/home/james/.local/share/Steam/steamapps/compatdata/1245620/" WINEPREFIX=$PWD \
    "$HOME/.local/share/Steam/steamapps/common/Proton - Experimental/proton" run "/home/james/.local/share/Steam/steamapps/common/ELDEN RING/Game/eldenring.exe" 
