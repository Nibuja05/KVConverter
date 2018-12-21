
import re
import os
from KV_Lua_Part import LuaFunction, LuaPart, LuaModifier

def get_function_code(path, name):
	file = open(path, 'r')
	text = ""
	stack = []
	start_pattern = r'function\s*?' + re.escape(name) +'\s*?\(\s*?(?P<key>\w+)\s*?\)'
	open_pattern = r'(do|if|function)\s+'
	close_pattern = r'end\s'
	comment_pattern = r'^.*?(--.*)'
	comment_start_pattern = r'^.*?(--\[\[.*)'
	comment_end_pattern = r'^(.*?\]\])'
	comment_startet = False
	start = False
	key = ""
	for x in file:
		#check comment stuff first
		c_ml_match = re.search(comment_start_pattern, x)
		if c_ml_match is not None:
			comment_startet = True
			x = x.replace(c_ml_match.group(1), "")
		if comment_startet == True:
			c_ml_end_match = re.search(comment_end_pattern, x)
			if c_ml_end_match is not None:
				comment_startet = False
				x = x.replace(c_ml_end_match.group(1), "")
			else:
				x = ""
		c_match = re.search(comment_pattern, x)
		if c_match is not None:
			x = x.replace(c_match.group(1), "")

		#other
		match = re.search(start_pattern, x)
		if match is not None:
			start = True
			key = match.group('key')
			stack.append("function")
			x = re.sub(r'' + re.escape(key), "self", x)
			text += x
		elif start == True:
			open_match = re.search(open_pattern, x)
			close_match = re.search(close_pattern, x)
			if open_match is not None:
				stack.append(open_match.group())
			if close_match is not None:
				stack.pop()
				if len(stack) == 0:
					text += x
					break
			text += x
	file.close()
	return text, key

def convert_all_functions(path):
	try:
		file = open(path, 'r')
	except Exception as e:
		print(e)
		print("Cannot read .lua file at " + path)
		return ""
	else:
		function_list = get_all_functions(file.read())
		file.close()
		text = ""
		for x in function_list:
			temp_text, key = get_function_code(path, x)
			text += replace_key_to_self(temp_text, key) + "\n"
		return text

def replace_key_to_self(text, key):
	if key == "self":
		return text
	caster_pattern = r'' + re.escape(key) + '\.caster'
	ability_pattern = r'(.*\w+\s*=)\s*' + re.escape(key) + '\.ability'
	target_point_pattern = r'' + re.escape(key) + '\.target_points\[1\]'
	text = re.sub(caster_pattern, "self:GetCaster()", text)
	text = re.sub(target_point_pattern, "self:GetCursorPosition()", text)
	ability_match = re.search(ability_pattern, text)
	if ability_match is not None:
		changed_line = ability_match.group(1) + " self"
		text = text[:ability_match.start()] + changed_line + text[ability_match.end():]
		#ability_name = find_ability_name(ability_match.group())
		#print(ability_name)
		#text = text.replace(ability_name, "self")

	text = text.replace(key, "self")

	modifier_pattern = r'\w*\:ApplyDataDrivenModifier\((?P<source>.+)\s*,\s*(?P<target>.+)\s*,\s*(?P<name>.+)\s*,\s*(?P<param>.+)\)'
	modifier_match = re.search(modifier_pattern, text)
	while modifier_match is not None:
		start_text = text[:modifier_match.start()]
		end_text = text[modifier_match.end():]
		new_text = modifier_match.group('target') + ":AddNewModifier(" + modifier_match.group('source')
		new_text += ", self, " + modifier_match.group('name') + ", " + modifier_match.group('param') + ")"
		text = start_text + new_text + end_text
		modifier_match = re.search(modifier_pattern, text)

	return text

			
def find_ability_name(text):
	pattern = r'(\w+)\s*='
	match = re.search(pattern, text)
	return match.group(1)

def get_all_functions(text):
	pattern = r'function\s+(\w+)\s*?\(\s*?\w*\s*?\)'
	return re.findall(pattern, text)

def define_passives(class_name, modifiers):
	text = ""
	passive_list = []
	for x in modifiers:
		if x.is_passive():
			passive_list.append("\"" + x.get_name() + "\"")
	new_function = LuaFunction(class_name, "GetIntrinsicModifierName")
	new_part = LuaPart()
	if len(passive_list) == 1:
		new_part.add_line("return " + passive_list[0])
		new_function.add_part(new_part)
		text = str(new_function)
	elif len(passive_list) > 1:
		new_part.add_line("local passives = {")
		passives_part = LuaPart()
		for x in passive_list:
			passives_part.add_line(x + ",")
		new_part.add_part(passives_part)
		new_part.add_line("}")
		new_part.add_line("return passives")
		new_function.add_part(new_part)
		text = str(new_function)

	return text