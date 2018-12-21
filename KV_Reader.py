
import re
import math

class KVPart():
	"""docstring for KVPart"""
	def __init__(self, name, tab_count = 0):
		#super(KVPart, self).__init__()
		self.name = name
		self.values = []
		self.tab_count = tab_count
		self.parent = None
		self.master = False

	def add_simple_value(self, value):
		self.values.append(value)

	def add_KVPart(self, name):
		if self.master == False:
			new_KVPart = KVPart(name, self.tab_count + 1)
		else:
			new_KVPart = KVPart(name, self.tab_count)
		new_KVPart.set_parent(self)
		self.values.append(new_KVPart)
		return new_KVPart

	def add_KVPart_finished(self, part):
		if not part is None:
			part.set_tab_count(self.tab_count + 1)
			self.values.append(part)

	def add_KVComment(self, text):
		new_KVComment = KVComment(text)
		self.values.append(new_KVComment)

	def is_empty(self):
		if len(self.values) == 0:
			return True
		return False

	def set_parent(self, parent):
		self.parent = parent

	def get_parent(self):
		return self.parent

	def has_parent(self):
		if self.parent is not None:
			return True
		return False

	def get_name(self):
		return self.name

	def set_master(self, boolean):
		self.master = boolean

	def get_values(self):
		return self.values

	def has_KV_child(self):
		return any(isinstance(x, KVPart) for x in self.values)

	def set_tab_count(self, count):
		self.tab_count = count

	def items(self):
		return self.name, self.values[0]
		
	def __str__(self):
		if self.master == False:	
			string = self.fTab(self.tab_count) + "\"" + self.name + "\""
			if any(isinstance(x, KVPart) for x in self.values):
				string += "\n" + self.fTab(self.tab_count) + "{\n"
			else:
				count = self.get_normal_space(string)
				string += self.get_normal_space(string)
			for x in self.values:
				if type(x) is KVPart:
					string += str(x)
				elif type(x) is KVComment:
					string += self.fTab(self.tab_count + 1) + str(x) + "\n"
				else:
					string += "\"" + str(x) + "\"\n"
			if any(isinstance(x, KVPart) for x in self.values):
				string += self.fTab(self.tab_count) + "}\n"
			return string
		else:
			if len(self.values) > 1:
				string = ""
				for x in self.values:
					string += str(x) + "\n"
				return string
			else:
				return ""

	def __repr__(self):
		return "<|" + self.name + "|>"

	def fTab(self, count):
		string = ""
		for x in range(count):
			string += "\t"
		return string

	def get_normal_space(self, text):
		lines = text.splitlines()
		last_line = lines[len(lines) - 1]
		new_position = last_line.rfind("\"")
		tab_count = math.floor((40 - new_position) / 5)
		space_count = ((40 - new_position) % 5) + 1
		string = ""
		for x in range(space_count):
			string += " "
		string += self.fTab(tab_count)
		return string

class KVComment():
	"""docstring for KVComment"""
	def __init__(self, text):
		#super(KVComment, self).__init__()
		self.text = text

	def __str__(self):
		return self.text
		

def read_file(path):
	#path = input("Please enter the path of the KV File:")
	#path = "C:\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota_addons\\heataria\\scripts\\npc\\abilities\\heataria_blaze_path.txt"
	try:
		file = open(path, "r")
		text = file.read()
	except FileNotFoundError:
		text = read_file()
	finally:
		master = KVPart("master")
		master.set_master(True)
		progress_text(text, master)
		return master

#processes a KV textfile into a KV_Part structure
def progress_text(text, last_KVPart = None):
	if last_KVPart is not None:
		#search patterns to check structure
		quote_pattern = r'\"(.*?)\"'
		open_pattern = r'.*{'
		close_pattern = r'.*}'
		comment_pattern = r'//.*'
		quote_match = re.search(quote_pattern, text)
		open_match = re.search(open_pattern, text)
		close_match = re.search(close_pattern, text)
		comment_match = re.search(comment_pattern, text)

		#cancel if there are no more quotes left
		if quote_match is not None:
			quote_start = quote_match.start()
		else:
			return

		#if there are no brackets left, give them a placeholder value
		if open_match is not None:
			open_start = open_match.start()
		else:
			open_start = len(text)
		if close_match is not None:
			close_start = close_match.start()
		else:
			close_start = len(text)
		if comment_match is not None:
			comment_start = comment_match.start()
		else:
			comment_start = len(text)
		string = quote_match.group(1)

		#print("SEACH: q." + str(quote_start) + " o." + str(open_start) + " cl." + str(close_start) + " co." + str(comment_start))

		if comment_start < quote_start and comment_start < open_start and comment_start < close_start:
			string = comment_match.group()
			text = text[comment_match.end() + 1:]
			last_KVPart.add_KVComment(string)
			progress_text(text, last_KVPart)

		#no bracktes before next quote -> simply add to current KV_Part
		elif quote_start < open_start and quote_start < close_start:

			#check if its a value or key
			if last_KVPart.is_empty() and not last_KVPart.get_name() == "master":
				last_KVPart.add_simple_value(string)
				new_KVPart = last_KVPart.get_parent()
			else:
				new_KVPart = last_KVPart.add_KVPart(string)
			text = text[quote_match.end() + 1:]
			progress_text(text, new_KVPart)

		#closing bracket -> remove bracket and move to parent KV_Part
		elif close_start < quote_start:
			text = text[close_match.end() + 1:]
			if last_KVPart.has_parent():
				temp_KVPart = last_KVPart.get_parent()
			else:
				temp_KVPart = last_KVPart
			progress_text(text, temp_KVPart)

		#opening bracket -> creates a new child KV_Part
		elif open_start < quote_start:
			new_KVPart = last_KVPart.add_KVPart(string)
			text = text[quote_match.end() + 1:]
			progress_text(text, new_KVPart)
