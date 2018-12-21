
from KV_Property_List import get_property_name, get_property_by_name

class LuaFunction():
	"""docstring for LuaPart"""
	def __init__(self, class_name, function_name, args = ""):
		self.class_name = class_name
		self.function_name = function_name
		self.args = args
		self.values = []

	def add_part(self, part): 
		if not part is None:
			part.set_count(1)
			self.values.append(part)

	def set_args(self, args):
		self.args = args

	def get_values(self):
		return self.values

	def get_name(self):
		return self.function_name

	def get_class(self):
		return self.class_name

	def get_args(self):
		return self.args

	def __str__(self):
		text = "function " + self.class_name + ":" + self.function_name + "(" + self.args + ")\n"
		count = 1
		for x in self.values:
			text += str(x)
		text += "end\n"
		return text


class LuaPart():
	"""docstring for LuaPart"""
	def __init__(self, count = 0):
		self.count = count
		self.values = []

	def add_line(self, line):
		self.values.append(line)

	def set_count(self, count):
		self.count = count
		for x in self.values:
			if type(x) is LuaPart:
				x.set_count(self.count + 1)

	def add_part(self, part):
		if not part is None:
			part.set_count(self.count + 1)
			self.values.append(part)

	def has_part_child(self):
		for x in self.values:
			if type(x) is LuaPart:
				return True
		return False

	def __str__(self):
		text = ""
		for x in self.values:
			if type(x) is LuaPart:
				text += str(x)
			else:
				text += fTab(self.count) +  x + "\n"
		return text

class LuaModifier():
	"""docstring for LuaModifier"""
	def __init__(self, name, path):
		self.name = name
		self.functions = []
		self.passive = False
		self.path = path
		self.properties = {}

	def get_link(self):
		return "LinkLuaModifier(\"" + self.name + "\", \"" + self.path + "\", LUA_MODIFIER_MOTION_NONE)\n"

	def get_name(self):
		return self.name

	def add_function(self, func):
		old_func = None
		for x in self.functions:
			if x.get_name() == func.get_name():
				old_func = x
		if old_func is not None:
			new_func = LuaFunction(func.get_class(), func.get_name(), func.get_args())
			for x in old_func.get_values():
				new_func.add_part(x)
			for x in func.get_values():
				new_func.add_part(x)
			self.functions.remove(old_func)
			self.functions.append(new_func)
		else:
			self.functions.append(func)

	def add_property(self, name, value):
		self.properties[name] = value

	def has_function_with_name(self, name):
		for x in self.functions:
			if x.get_name() == name:
				return True
		return False

	def get_function_by_name(self, name):
		for x in self.functions:
			if x.get_name() == name:
				return x
		return None

	def set_passive(self, state):
		self.passive = state

	def is_passive(self):
		return self.passive

	def __str__(self):
		text = self.name + " = class({})\n\n"
		if len(self.properties) > 0:
			new_function = LuaFunction(self.name, "DeclareFunctions")
			new_part = LuaPart()
			new_part.add_line("local funcs = {")
			funcs_part = LuaPart()
			for x in self.properties.keys():
				funcs_part.add_line(x + ",")
			new_part.add_part(funcs_part)
			new_part.add_line("}")
			new_part.add_line("return funcs")
			new_function.add_part(new_part)
			self.functions.append(new_function)
			for x,y in self.properties.items():
				func_function = LuaFunction(self.name, get_property_name(x))
				value_part = LuaPart()
				y = convert_value_to_special(y)
				value_part.add_line("return " + y)
				func_function.add_part(value_part)
				self.functions.append(func_function)

		for x in self.functions:
			text += str(x) + "\n"
		return text


def fTab(count):
		string = ""
		for x in range(count):
			string += "\t"
		return string	

def convert_value_to_special(value):
	if "%" in value:
		value = "self:GetAbility():GetSpecialValueFor(\"" + value[value.find("%") + 1:] + "\")"
	return value
