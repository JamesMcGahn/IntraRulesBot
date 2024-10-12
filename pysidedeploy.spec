[app]

# title of your application
title = IntraRulesBot

# project directory. the general assumption is that project_dir is the parent directory
# of input_file
project_dir = .

# project_dir = ./
# source file path
input_file = C:\Users\james.mcgahn\Documents\IntraRulesBot\main.py

# directory where exec is stored
exec_directory = C:\Users\james.mcgahn\Documents\IntraRulesBot\build

# path to .pyproject project file
project_file = 

# application icon
icon = C:\Users\james.mcgahn\Documents\IntraRulesBot\resources\system_icons\logo48_48.ico

[python]

# python path
python_path = C:\Users\james.mcgahn\Documents\IntraRulesBot\.venv\Scripts\python.exe

#python_path = /Users/jamesmcgahn/Documents/GitHub/IntraRulesBot/.venv/bin/python
# python packages to install
packages = Nuitka==2.4.8,pywin32==307

# buildozer = for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]

# comma separated path to qml files required
# normally all the qml files required by the project are added automatically
qml_files = 

# excluded qml plugin binaries
excluded_qml_plugins = 

# qt modules used. comma separated
modules = Widgets,Gui,Core

# qt plugins used by the application
plugins = accessiblebridge,styles,egldeviceintegrations,xcbglintegrations,iconengines,platforminputcontexts,platforms/darwin,platforms,generic,imageformats,platformthemes

[android]

# path to pyside wheel
wheel_pyside = 

# path to shiboken wheel
wheel_shiboken = 

# plugins to be copied to libs folder of the packaged application. comma separated
plugins = 

[nuitka]

# usage description for permissions requested by the app as found in the info.plist file
# of the app bundle
# eg = extra_args = --show-modules --follow-stdlib
macos.permissions = 

# mode of using nuitka. accepts standalone or onefile. default is onefile.
mode = onefile

# (str) specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations --windows-console-mode=disable --windows-icon-from-ico=./resources/system_icons/logo48_48.ico --company-name=IntraRulesBot --product-name=IntraRulesBot --product-version=1.0.0 --copyright=MIT --file-description="IntraRulesBot Rules Automation"

[buildozer]

# build mode
# possible options = [release, debug]
# release creates an aab, while debug creates an apk
mode = relase

# contrains path to pyside6 and shiboken6 recipe dir
recipe_dir = 

# path to extra qt android jars to be loaded by the application
jars_dir = 

# if empty uses default ndk path downloaded by buildozer
ndk_path = 

# if empty uses default sdk path downloaded by buildozer
sdk_path = 

# other libraries to be loaded. comma separated.
# loaded at app startup
local_libs = 

# architecture of deployed platform
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
arch = 

