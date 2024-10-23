# BBatch - Blender Batch Exporter
 Blender addon for bulk exporting of assets.
 
![BBatch_Exporter](https://github.com/MathiasLArt/BBatch/assets/59111832/f0d1b418-80e1-46a6-b61c-27b87ab1f667)

# Features
* export 1 file per selected objects
* supports multiple formats (.fbx, .obj, .stl, .gltf, .dae, .abc)
  
   ![BBatch_SupportedFormats](https://github.com/MathiasLArt/BBatch/assets/59111832/2d7a4a57-2a67-48db-bcc0-a797d3d8d350)

* support exporting empties
* non destructively strips .xxx suffixes upon exporting for cleaner names in third party softwares

  
* advanced option to set smoothing type
* advanced option to set pivot location (usefull for export to game-engine as it places the object at world origins before exporting)

# Installing
1. Download latest release
2. Open Blender.
3. Go to: Edit => Preferences => addons
4. click install addon
5. select the downloaded .zip file
6. check 'enable plugin'

# Version control
Currently I am supporting perforce (p4v). The addon will auto-detect p4 setting if they have been setup correctly.

* p4 set P4CONFIG=p4config

if that didnt work, then provide the absolute path to the p4config file.
If not, add them manually to the preferences of the add-on.

p4Config example:

P4PORT=ssl:xxx.xx.xx.xxx:1666

P4USER=M3thi4sL

P4CLIENT=M4thi4sL_Blender


# Usage
1) select desired objects
2) set options
3) press export
4) time saved!

# Credits

heavily inspired by the work of https://github.com/jayanam/batex
