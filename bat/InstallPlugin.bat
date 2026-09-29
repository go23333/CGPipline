@echo off
net use S: \\192.168.3.248\Script
setx MAYA_MODULE_PATH S:\CGPipline\maya
setx SUBSTANCE_PAINTER_PLUGINS_PATH=S:\CGPipline\maya\sp\deploy
exit