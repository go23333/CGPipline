import maya.api.OpenMaya as om

import maya.cmds as cmds
import os
import json
import subprocess


def maya_useNewAPI():  # noqa
    """dummy method to tell Maya this plugin uses the Maya Python API 2.0"""
    pass

class UploadFileToServe(om.MPxCommand):
    command_name = "UploadFileToServe"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def command_creator():
        return UploadFileToServe()

    def doIt(self, args):
        currentScenePath = cmds.file(q=True, sceneName=True)
        if currentScenePath == "":
            print("No file is currently open.")
        else:
            fileName = os.path.basename(currentScenePath)
            if "_Mo" in fileName:
                newFileName  = fileName.replace("_Mo", "")
            if "_Shade" in fileName:
                newFileName = fileName.replace("_Shade", "")
            currentPath = os.path.dirname(currentScenePath)
            parentDir = os.path.dirname(currentPath)
            referenceFolder = os.path.join(parentDir, "Reference")
            if not os.path.exists(referenceFolder):
                os.makedirs(referenceFolder)
            newFilePath = os.path.join(referenceFolder, newFileName)
            newFilePath = newFilePath.replace("\\", "/")
            cmds.file(rename=newFilePath)
            cmds.file(save=True)
            print("file save to: " + newFilePath)

        GaiBianLuJing = newFilePath.replace("/", "\\")
        desktopPath = os.getenv("USERPROFILE") + "\\Desktop"  
        fileName = "file_data.json"
        fullPath = os.path.join(desktopPath, fileName)
        jsonContent = [
            {
                "path": GaiBianLuJing,
                "type": "file"
            }
        ]

        try:
            with open(fullPath, "w") as file:
                json.dump(jsonContent, file, indent=4)
            print("File saved successfully at: " + fullPath)
        except Exception as e:
            print("Failed to open the file for writing: " + str(e))

        username = os.getenv('USER') or os.getenv('USERNAME')
        DiaoYongHuanJing = "C:/Users/{}/AppData/Roaming/zynn/zynnMain/main/zynnMain.exe".format(username)
        subprocess.call([DiaoYongHuanJing, fullPath, "-allow-file-access-from-files"])


def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(UploadFileToServe.command_name, UploadFileToServe.command_creator)
    except Exception as e:
        om.MGlobal.displayError("Failed to register command: {0}".format(UploadFileToServe.command_name))
        raise e


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(UploadFileToServe.command_name)
    except Exception as e:
        om.MGlobal.displayError("Failed to unregister command: {0}".format(UploadFileToServe.command_name))
        raise e