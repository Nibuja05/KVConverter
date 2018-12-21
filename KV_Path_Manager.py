
import re
import os

def get_root_folder(path):
	path = path.replace("\\", "/")
	pattern = r'(.*/dota_addons/.*?)/'
	match = re.search(pattern, path)
	if match is not None:
		return match.group(1)
	else:
		return ""

def get_lua_path(path):
	if path.find("vscripts") >= 0:
		lua_path = path[path.find("vscripts") + 9:]
		return lua_path
	return "<unknown>"

def find_mentioned_lua_path(path):
	mentioned_path = ""
	file = None
	try:
		file = open(path, 'r')
	except Exception as e:
		file = None
	finally:
		if file is None:
			print("Cannot open " + path)
			return ""
	
	file_pattern = r'\"ScriptFile\"\s*?\"(.*?)\"'
	for x in file:
		file_match = re.search(file_pattern, x)
		if file_match is not None:
			mentioned_path = file_match.group(1)
			break
	if mentioned_path == "":
		return ""
	path_pattern = r'(.*)\/.*\.lua'
	path_match = re.search(path_pattern, mentioned_path)
	if path_match is None:
		print("First mentioned file invalid.")
		return ""
	mentioned_path = path_match.group(1)
	mentioned_path = mentioned_path.replace("\\", "/")
	return mentioned_path

def get_origin_path(path):
	origin = ""
	pattern = r'(.*\/).*\.(txt|kv)'
	match = re.search(pattern, path)
	if match is None:
		return ""
	origin = match.group(1)
	return origin

#root_path = get_root_folder()
#get_lua_path(root_path, "heroes/hero_heataria/heataria_blaze_path.lua")