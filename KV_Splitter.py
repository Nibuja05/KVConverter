
import os
import random
from KV_Path_Manager import get_root_folder, get_lua_path
from KV_Lua_Manager import convert_all_functions
from KV_Reader import KVPart, KVComment, read_file
from KV_Property_List import get_property_name, get_property_by_name
from KV_Modifier_List import get_particle_constant, get_constant_function_by_name, get_function_name_list
from KV_Lua_Part import LuaFunction, LuaPart, LuaModifier

def split_to_spells(master):
	spell_list = []
	for x in master.get_values():
		if type(x) is KVPart:
			spell_list.append(x)
	return spell_list

def get_spell_components(spell):
	components = {}
	attributes = []
	functions = []
	components['attributes'] = attributes
	components['functions'] = functions
	components['precache'] = None
	components['special'] = None
	components['modifiers'] = None
	for x in spell.get_values():
		if type(x) is KVPart:
			name = x.get_name()
			if name == "precache":
				components['precache'] = x
			elif name == "Modifiers":
				components['modifiers'] = x
			elif name == "AbilitySpecial":
				components['special'] = x
			else:
				if x.has_KV_child():
					functions.append(x)
				else:
					attributes.append(x)
	return components

def combine_to_KV_text(old_spell, components, path):
	new_spell = KVPart(old_spell.get_name())
	for x in components['attributes']:
		if not x.get_name() == "BaseClass":
			new_spell.add_KVPart_finished(x)
		else:
			base_class = KVPart("BaseClass")
			base_class.add_simple_value("ability_lua")
			script_file = KVPart("ScriptFile")
			script_file.add_simple_value(get_lua_path(path))
			new_spell.add_KVPart_finished(base_class)
			new_spell.add_KVPart_finished(script_file)
	new_spell.add_KVComment("//Precache")
	new_spell.add_KVComment("//-------------------------------------------------------------------------------")
	new_spell.add_KVPart_finished(components['precache'])
	new_spell.add_KVComment("//AbilitySpecial")
	new_spell.add_KVComment("//-------------------------------------------------------------------------------")
	new_spell.add_KVPart_finished(components['special'])
	return new_spell

def create_lua_file(name):
	text = name + " = class({})\n"
	return text

def create_lua_function(part, class_name, path):
	name = part.get_name()
	lua_function = LuaFunction(class_name, part.get_name())

	if "attack" in part.get_name().lower():
		lua_function.set_args("args")
	if "attack" in part.get_name().lower():
		attack_part = LuaPart()
		attack_part.add_line("self:GetAbility().target = args.target")
		attack_part.add_line("self:GetAbility().attacker = args.attacker")
		lua_function.add_part(attack_part)
	for x in part.get_values():
		lua_function.add_part(get_new_lua_part(x, False, False))

	return lua_function

def extract_run_script(part):
	script_list = []
	for x in part.get_values():
		if x.get_name() == "RunScript":
			run_script = {}
			params = []
			for y in x.get_values():
				if y.get_name() == "ScriptFile":
					run_script['file'] = y.get_values()[0]
				elif y.get_name() == "Function":
					run_script['function'] = y.get_values()[0]
				elif y.get_name() == "Target":
					run_script['target'] = y.get_values()[0]
				else:
					run_script['params'] = params
					params.append(y.get_values()[0])
			script_list.append(run_script)

	return script_list


def get_all_parts(part):
	return_list = []
	return_list.append(part)
	if not part.is_empty():
		for x in part.get_values():
			if type(x) is KVPart:
				if x.has_KV_child():
					return_list = return_list + get_all_parts(x)
	return return_list

def get_old_functions(part, class_name, root_path):
	lua_files = []
	root_path += "/scripts/vscripts/"
	for x in get_all_parts(part):
		if x.get_name() == "RunScript":
			for y in x.get_values():
				if y.get_name() == "ScriptFile":
					name = root_path + y.get_values()[0]
					if not name in lua_files:
						lua_files.append(name)
	text = ""
	for x in lua_files:
		text += convert_all_functions(x)
	return text

def fTab(count):
	string = ""
	for x in range(count):
		string += "\t"
	return string

def convert_all_modifiers(components, path):
	modifier_list = []
	if components['modifiers'] is not None:
		for x in components['modifiers'].get_values():
			new_modifier = LuaModifier(x.get_name(), get_lua_path(path) + ".lua")
			convert_modifier(new_modifier, x)
			modifier_list.append(new_modifier)

	return modifier_list

def convert_modifier(modifier, part):
	if part.has_KV_child():
		for x in part.get_values():
			if type(x) is KVPart:
				if x.has_KV_child():
					get_function_from_part(modifier, x)
				else:
					get_simple_function_from_part(modifier, x)

def get_simple_function_from_part(modifier, part):

	name = modifier.get_name()
	function_name = ""
	value = part.get_values()[0]
	if value == "0":
		value = "false"
	elif value == "1":
		value = "true"
	if part.get_name() == "Passive":
		if value == "true":
			modifier.set_passive(True)
		return
	if part.get_name() == "ThinkInterval":
		start_function = LuaFunction(name, "OnCreated")
		interval_part = LuaPart()
		value = convert_value_to_special(value)
		interval_part.add_line("self:StartIntervalThink(" + value + ")")
		start_function.add_part(interval_part)
		modifier.add_function(start_function)
		return
	else:
		function_name = get_constant_function_by_name(part.get_name())
	if function_name == "":
		return
	value = value.replace("|", "+")
	value = convert_value_to_special(value)
	if "/" in value:
		value = "\"" + value + "\""
	new_function = LuaFunction(name, function_name)
	new_part = LuaPart()
	new_part.add_line("return " + value)
	new_function.add_part(new_part)
	modifier.add_function(new_function)

def get_function_from_part(modifier, part):
	name = modifier.get_name()
	new_function = LuaFunction(name, part.get_name())
	if part.get_name() in get_function_name_list():
		if "attack" in part.get_name().lower():
			new_function.set_args("args")
		if "attack" in part.get_name().lower():
			attack_part = LuaPart()
			attack_part.add_line("self:GetAbility().target = args.target")
			attack_part.add_line("self:GetAbility().attacker = args.attacker")
			new_function.add_part(attack_part)
		for x in part.get_values():
			new_function.add_part(get_new_lua_part(x, True, False))
		prop = get_property_by_name(part.get_name())
		if not prop == "":
			modifier.add_property(prop, "")
	elif part.get_name() == "Properties":
		for x in part.get_values():
			if type(x) is KVPart:
				modifier.add_property(x.get_name(), x.get_values()[0])
		return None
	elif part.get_name() == "States":
		new_function = LuaFunction(name, "CheckState")
		new_part = LuaPart()
		new_part.add_line("local state = {")
		states_part = LuaPart()
		for x in part.get_values():
			if type(x) is KVPart:
				value = x.get_values()[0]
				if value == "MODIFIER_STATE_VALUE_ENABLED":
					value = "true"
				else:
					value = "false"
				states_part.add_line("[" + x.get_name() + "] = " + value + ",")
		new_part.add_part(states_part)
		new_part.add_line("}")
		new_part.add_line("return state")
		new_function.add_part(new_part)

	modifier.add_function(new_function)

def get_new_lua_part(part, is_modifier, target_block):
	if not type(part) is KVComment:
		new_part = LuaPart()
		if part.get_name() == "RunScript":
			values = get_values_from_part(part)
			for x,y in values.items():
				if x == "Function":
					function = y
				elif x == "Target":
					if y == "POINT":
						y = "self:GetCursorPosition()"
						if is_modifier:
							new_part.add_line("self:GetAbility().targetPoints[1] = " + y)
						else:
							new_part.add_line("self.targetPoints[1] = " + y)
					else:
						if is_modifier:
							new_part.add_line("self:GetAbility().target = " + get_lua_target(y, is_modifier, target_block))
						else:
							new_part.add_line("self.target = " + get_lua_target(y, is_modifier, target_block))
				else:
					if not x == "ScriptFile":
						if "%" in y:
							y = "self:GetAbility():GetSpecialValueFor(\"" + y[y.find("%") + 1:] + "\")"
						else:
							y = "\"" + y + "\""
						new_part.add_line("self:GetAbility()." + x + " = " + y + "\n")
			if is_modifier:
				new_part.add_line(function + "(self:GetAbility())\n")
			else:
				new_part.add_line(function + "(self)\n")
		elif part.get_name() == "Damage":
			values = get_values_from_part(part)
			for x,y in values.items():
				values[x] = convert_value_to_special(y)
			target = get_lua_target(values["Target"], is_modifier, target_block)
			damage_part = LuaPart()
			damage_values = LuaPart()
			damage_part.add_line("local damageTable = ")
			damage_part.add_line("{")
			damage_values.add_line("victim = " + target + ",")
			damage_values.add_line("attacker = self:GetCaster(),")
			damage_values.add_line("damage = " + values["Damage"] + ",")
			damage_values.add_line("damage_type = " + values["Type"] + ",")
			damage_part.add_part(damage_values)
			damage_part.add_line("}")
			damage_part.add_line("ApplyDamage(damageTable)")
			new_part = damage_part 
		elif part.get_name() == "FireSound":
			values = get_values_from_part(part)
			for x,y in values.items():
				if x == "EffectName":
					sound_name = y
				elif x == "Target":
					target = get_lua_target(y, is_modifier, target_block)
			new_part.add_line(target + ":EmitSound(" + sound_name + ")")
		elif part.get_name() == "ActOnTargets":
			values = get_values_from_part(part)
			vars = {}
			for x,y in values.items():
				if x == "Target":
					for z in y:
						v,w = z.items()
						if v == "Center":
							if w == "POINT":
								new_part.add_line("local searchLoc = self:GetCursorPosition()")
							else:
								w = get_lua_target(w, is_modifier, target_block)
								new_part.add_line("locl searchLoc = " + w + ":GetAbsOrigin()")
						else:
							var_name = v.lower()
							var_value = convert_value_to_special(w)
							vars[var_name] = var_value
				else:
					if not "teams" in vars:
						vars["teams"] = "DOTA_UNIT_TARGET_TEAM_BOTH"
					if not "type" in vars:
						vars["type"] = "DOTA_UNIT_TARGET_ALL"
					if not "flags" in vars:
						vars["flags"] = "DOTA_UNIT_TARGET_FLAG_NONE"
					for v,w in vars.items():
						new_part.add_line("local " + v + " = " + w)
					new_part.add_line("local searchResult = FindUnitsInRadius(caster:GetTeamNumber(), searchLoc, nil, radius, teams, type, flags, FIND_CLOSEST, false)")
					new_part.add_line("for _,unit in pairs(searchResult) do")
					for z in y:
						new_part.add_part(get_new_lua_part(z, is_modifier, True))
					new_part.add_line("end")
		elif part.get_name() == "ApplyModifier":
			values = get_values_from_part(part)
			mod_table = {}
			for x,y in values.items():
				if x == "Target":
					target = get_lua_target(y, is_modifier, target_block)
				elif x == "ModifierName":
					mod_name = "\"" + y + "\""
				else:
					mod_table[x] = y
			if is_modifier:
				ability = "self:GetAbility()"
			else:
				ability = "self"
			mod_args = ""
			for x,y in mod_table.items():
				mod_args += x + " = " + convert_value_to_special(y) + ","
			new_part.add_line(target + ":AddNewModifier(self:GetCaster(), " + ability + ", " + mod_name + ", {" + mod_args + "})")
		elif part.get_name() == "RemoveModifier":
			values = get_values_from_part(part)
			for x,y in values.items():
				if x == "Target":
					target = get_lua_target(y, is_modifier, target_block)
				elif x == "ModifierName":
					mod_name = "\"" + y + "\""
			new_part.add_line(target + ":RemoveModifierByName(" + mod_name + ")")
		elif part.get_name() == "CreateThinker":
			values = get_values_from_part(part)
			mod_table = {}
			for x,y in values.items():
				if x == "ModifierName":
					mod_name = "\"" + y + "\""
				elif x == "Target":
					if y == "POINT":
						thinker_loc = "self:GetCursorPosition()"
					else:
						y = get_lua_target(y, is_modifier, target_block)
						thinker_loc = y + ":GetAbsOrigin()"
				else:
					mod_table[x] = y
			if is_modifier:
				ability = "self:GetAbility()"
			else:
				ability = "self"
			mod_args = ""
			for x,y in mod_table.items():
				mod_args += x + " = " + convert_value_to_special(y) + ","
			new_part.add_line("CreateModifierThinker( self:GetCaster(), " + ability + ", " + mod_name + ", {" + mod_args + "}, " + thinker_loc + ", self:GetCaster():GetTeamNumber(), false)")
		elif part.get_name() == "":
			pass

		return new_part
	return None


def get_syntax_from_name(part, name, property_list, particle_list):
	text = ""
	if part.get_name() in get_function_name_list():
		if "attack" in part.get_name().lower():
			text = "\nfunction " + name + ":" + part.get_name() + "( args )\n"
		else:
			text = "\nfunction " + name + ":" + part.get_name() + "()\n"
		if "attack" in part.get_name().lower():
			text += fTab(1) + "self:GetAbility().target = args.target\n"
			text += fTab(1) + "self:GetAbility().attacker = args.attacker\n"
		for x in part.get_values():
			text += get_action(x, 1, particle_list, True)
		text += "end\n"
		prop = get_property_by_name(part.get_name())
		if not prop == "":
			property_list.append(prop)
	elif part.get_name() == "Properties":
		text = "\nfunction " + name + ":DeclareFunctions()\n"
		text += fTab(1) + "local funcs = {\n"
		prop_list = {}
		for x in part.get_values():
			prop_list[x.get_name()] = x.get_values()[0]
			text += fTab(2) + x.get_name() + ",\n"
		for x in property_list:
			text += fTab(2) + x + ",\n"
		property_list = []
		text += fTab(1) + "}\n" + fTab(1) + "return funcs\nend\n"
		for x,y in prop_list.items():
			text += "\nfunction " + name + ":" + get_property_name(x) + "()\n"
			if "%" in y:
				y = "self:GetAbility():GetSpecialValueFor(\"" + y[y.find("%") + 1:] + "\")"
			text += fTab(1) + "return " + y + "\nend\n"
	return text

def get_constant(part, name, passive_list):
	text = ""
	value = part.get_values()[0]
	func_name = ""
	if value == "0":
		value = "false"
	elif value == "1":
		value = "true"
	if part.get_name() == "Passive":
		if value == "true":
			passive_list.append(name)
		return ""
	else:
		func_name = get_constant_function_by_name(part.get_name())
		print(func_name)
	value = value.replace("|", "+")
	if "%" in value:
		value = "self:GetAbility():GetSpecialValueFor(\"" + value[value.find("%") + 1:] + "\")"
	text += "\nfunction " + name + ":" + func_name + "\n"
	text += fTab(1) + "return " + value + "\nend\n"
	return text

def get_action(part, count, particle_list, is_modifier):
	text = ""
	if part.get_name() == "RunScript":
		function = ""
		params = {}
		for x in part.get_values():
			if x.get_name() == "Function":
				function = x.get_values()[0]
			else:
				if not x.get_name() == "ScriptFile":
					params[x.get_name()] = x.get_values()[0]
		for x,y in params.items():
			if "%" in y:
				y = "self:GetAbility():GetSpecialValueFor(\"" + y[y.find("%") + 1:] + "\")"
			else:
				y = "\"" + y + "\""
			text += fTab(count) + "self:GetAbility()." + x + " = " + y + "\n"
		text += fTab(count) + function + "(self:GetAbility())\n"
	elif part.get_name() == "AttachEffect":
		values = get_values_from_part(part)
		target = values["Target"]
		particle = values["EffectName"]
		attach = values["EffectAttachType"]
		if target == "CASTER":
			target = "self:GetCaster()"
		else:
			target = "self:GetParent()"
		if type(target) is KVPart:
			pass
		constant = get_particle_constant(attach)
		particle_id = ""
		while particle_id == "":
			particle_id = "particle" + str(random.randint(1,100))
			if particle_id in particle_list.keys():
				particle_id = ""
			else:
				particle_list[particle_id] = target
		text += fTab(count) + "if " + target + "." + particle_id + " == nil then\n"
		text += fTab(count + 1) + target + "." + particle_id + " = ParticleManager:CreateParticle(\"" + particle + "\", " + constant + ", " + target + ")\n"
		text += fTab(count + 1) + "ParticleManager:SetParticleControlEnt(" + target + "." + particle_id + ", 0, " + target + ", " + constant + ", \"" + attach + "\", " + target + ":GetAbsOrigin(), true)\n"
		text += fTab(count) + "end\n"
	elif part.get_name() == "Damage":
		values = get_values_from_part(part)
		for x,y in values.items():
			values[x] = convert_value_to_special(y)
		target = get_lua_target(values["Target"], is_modifier, target_block)
		damage = convert_value_to_special(values["Damage"])
		damage_type = values["Type"].replace("|", "+")
		text += fTab(count) + "local damageTable = \n" + fTab(count) + "{\n"
		text += fTab(count + 1) + "victim = " + target + ",\n"
		text += fTab(count + 1) + "attacker = self:GetCaster(),\n"
		text += fTab(count + 1) + "damage = " + damage + ",\n"
		text += fTab(count + 1) + "damage_type = " + damage_type + ",\n"
		text += fTab(count) + "}\n" + fTab(count) + "ApplyDamage(damageTable)\n" 

	if is_modifier == False:
		text.replace("self:GetAbility()", "self")

	return text


def get_values_from_part(part):
	value_dict = {}
	for x in part.get_values():
		if len(x.get_values()) > 1:
			value = x.get_values()
		else:
			value = x.get_values()[0]
		value_dict[x.get_name()] = value
	return value_dict

def convert_value_to_special(value):
	if "%" in value:
		value = "self:GetAbility():GetSpecialValueFor(\"" + value[value.find("%") + 1:] + "\")"
	return value

def get_lua_target(target, is_modifier, target_block):
	if type(target) == list:
		for z in target:
			x,y = z.items()
			#something here
			return "unit"
	if target == "CASTER":
		return "self:GetCaster()"
	elif target == "TARGET":
		if not target_block:
			if is_modifier:
				return "self:GetParent()"
			else:
				return "self:GetCursorTarget()"
		else:
			return "unit"
	return ""