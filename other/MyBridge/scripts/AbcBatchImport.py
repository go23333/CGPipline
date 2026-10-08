import json

import unreal

if __name__ == "__main__":
	unreal.EditorPythonScripting.set_keep_python_script_alive(True)
	(cmd_tokens, cmd_switches, cmd_parameters) = unreal.SystemLibrary.parse_command_line(unreal.SystemLibrary.get_command_line())
	root_path = cmd_parameters['project_root']
	from UnrealPipeline.core.batchABCImport import BatchAbcImport
	BatchAbcImport(root_path)

