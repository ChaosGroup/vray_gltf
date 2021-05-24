# V-Ray glTF viewer

![Sample render](/samples/basic/basic.png)

## Overview

The V-Ray glTF viewer is a set of Python scripts for the V-Ray App SDK that allow the parsing and rendering of glTF (.gltf and .glb) files.

## Installing and running the V-Ray glTF viewer

### With V-Ray App SDK

* Install Python 3.8 for all users in "c:\Program Files\Python38"

* Install nightly V-Ray 5 App SDK (Qt version) in "C:\Program Files\Chaos Group\V-Ray\AppSDK". Be sure to choose the _Advanced_ installation type and make sure the installation does _not_ modify any license settings or environment variables.

  Note: In case you accidentally let the V-Ray App SDK installation modify the V-Ray license settings, run the tool setvrlservice.exe or from the start menu search for "Change V-Ray client license settings" to change them.

* Open a command prompt (press Windows+R, type `cmd` and press Enter).

* Execute `set path="c:\program files\python38";"c:\program files\python38\scripts";%path%`
* _First time only:_ Execute `pip install numpy`
* _First time only:_ Execute `pip install pyquaternion`
* _First time only:_ Execute `pip install numba`
* _First time only:_ Execute `pip install scipy`

* Execute `"C:\Program Files\Chaos Group\V-Ray\AppSDK\setenv38.bat"`
* Execute `cd /d VRAY_GLTF_FOLDER` where VRAY_GLTF_FOLDER is the folder where the file main.py is located.
* Execute `python main.py` to see a list of options; use `python main.py --help` for detailed usage description.

### With V-Ray 5 for 3ds Max

The Python binding of the V-Ray AppSDK is also included with V-Ray 5 for 3ds Max and Maya and in this case it is not needed to install the V-Ray AppSDK separately.

* Make sure you have a recent version of V-Ray 5 for 3ds Max with the Python 3 binding of the V-Ray App SDK included (check if you have the folder "C:\Program Files\Chaos Group\V-Ray\3ds Max 2021\samples\appsdk\python38").

* Install Python 3.8 for all users in "c:\Program Files\Python38"

* Open a command prompt (press Windows+R, type `cmd` and press Enter).

* Execute `set path="c:\program files\python38";"c:\program files\python38\scripts";%path%`
* _First time only:_ Execute `pip install numpy`
* _First time only:_ Execute `pip install pyquaternion`
* _First time only:_ Execute `pip install numba`
* _First time only:_ Execute `pip install scipy`

* Execute `"C:\Program Files\Chaos Group\V-Ray\3ds Max 2021\samples\appsdk\setenv38.bat"`
* Execute `cd /d VRAY_GLTF_FOLDER` where VRAY_GLTF_FOLDER is the folder where the file main.py is located.
* Execute `python main.py` to see a list of options; use `python main.py --help` for detailed usage description.

## Usage

The V-Ray glTF scripts are command-line only; there is no GUI and all options must be passed on the command line.

Use the --help option to list all possible options and their values.

## Supported features

The glTF parser supports glTF 2.0 with the following extensions:

* KHR_texture_transform
* KHR_materials_pbrSpecularGlossiness
* KHR_materials_transmission
* KHR_materials_clearcoat
* KHR_materials_sheen
* KHR_lights_punctual is currently WIP

Simple transform animations are supported to some extent. Vertex deformations, either through morphing or skinning are currently not supported.

Most of the sample models provided by Khronos generally render fine, as well as many models from the Windows 3D viewer library.
