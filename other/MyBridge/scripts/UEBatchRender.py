import json

import unreal

if __name__ == "__main__":
	unreal.EditorPythonScripting.set_keep_python_script_alive(True)
	(cmd_tokens, cmd_switches, cmd_parameters) = unreal.SystemLibrary.parse_command_line(unreal.SystemLibrary.get_command_line())
	queue_asset_path = cmd_parameters['queue'].split(",")
	config_path = cmd_parameters['config']
	from UnrealPipeline.core.batchRender import RenderSequences
	RenderSequences(queue_asset_path,config_path)