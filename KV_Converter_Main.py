
import sys, getopt, re, os
import readline
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from KV_Path_Manager import get_root_folder, find_mentioned_lua_path, get_origin_path
from KV_Reader import read_file
from KV_Splitter import split_to_spells, create_lua_function, create_lua_file, get_spell_components, combine_to_KV_text, convert_all_modifiers, get_old_functions
from KV_Lua_Manager import define_passives


def main(argv):
	inputfile = ''
	lua_outputpath = ''
	kv_outputpath = ''
	project_path = ''

	welcome = 	" __      __        _                              _        \n \ \    / /  ___  | |  __   ___   _ __    ___    | |_   ___ \n  \ \/\/ /  / -_) | | / _| / _ \ | '  \  / -_)   |  _| / _ \ \n   \_/\_/   \___| |_| \__| \___/ |_|_|_| \___|    \__| \___/\n"
	label = " _                          _       _                 _______\n| \    /\|\     /|         ( \     ( \      |\     /|(  ___  )\n|  \  / /| )   ( |          \ \    | (      | )   ( || (   ) |\n|  (_/ / | |   | |   _____   \ \   | |      | |   | || (___) |\n|   _ (  ( (   ) )  (_____)   ) )  | |      | |   | ||  ___  |\n|  ( \ \  \ \_/ /            / /   | |      | |   | || (   ) |\n|  /  \ \  \   /            / /    | (____/\| (___) || )   ( |\n|_/    \/   \_/            (_/     (_______/(_______)|/     \|\n"
	version = " __   __                   _                  _        __  \n \ \ / /  ___   _ _   ___ (_)  ___   _ _     / |      /  \ \n  \ V /  / -_) | '_| (_-< | | / _ \ | ' \    | |  _  | () |\n   \_/   \___| |_|   /__/ |_| \___/ |_||_|   |_| (_)  \__/\n"
	print(welcome)
	print(label)
	print(version)

	readline.parse_and_bind("control-v: paste")

	if len(argv) > 0:
		argv = combine_elements_in_string(argv)
		try:
			opts, args = getopt.getopt(argv, "hi:o:u:p:", ["ifile=","ofile=", "ufile=", "pfile="])
		except getopt.GetoptError:
			print("Parameter Error")
			sys.exit(2)
		else:
			if not len(opts) == 0:
				for opt, arg in opts:
					if opt == '-h':
						#parameter help:
						print("Possible parameters:")
						print("   Inputfile:        -i <path> or -i '/c' (opens file chooser)")
						print("   Outputpath (Lua): -o <path> or")
						print("                     -o '/r' (output in <addon_name>/scripts/vscripts) or")
						print("                     -o '/rs' (output, where mentioned .lua file is located)")
						print("                     -o '/rsa+<alternative>' (like /rs but with alternative,")
						print("                         if there is no mentioned .lua file. Inside /vscripts/)")
						print("   Outputpath (KV):  -u <path> or")
						print("                     -u '/r' (output in <addon_name>/scripts/npc[/abilities])")
						print("                     -u '/rs' (output in <addon_name>/scripts/npc/[origin_path])")
						print("   Project Path:     -p <path> (to set other <addon_name>, use any file from there)")
						print("[Standart] Input: -i /c; Output (Lua/KV): Same as input")

					elif opt in ("-i", "--ifile"):
						inputfile = arg
						inputfile = inputfile.replace("\\", "/")
						if not os.path.exists(inputfile) and inputfile != "/c":
							print("Invalid File. Cancel")
							sys.exit()
					elif opt in ("-o", "--ofile"):
						lua_outputpath = arg
					elif opt in ("-u", "--ufile"):
						kv_outputpath = arg
					elif opt in ("-p", "--pfile"):
						project_path = arg

	while len(argv) == 0 or '-h' in argv:
		if len(argv) == 0:
			print("No input parameters found. Do you want to enter them now?")
			print("Please insert your parameters (/exit to leave): \n(leave empty for none; -h for help)")
		user_input = input("> ")
		if user_input == "/exit":
			sys.exit()
		argv = user_input.split(" ")
		argv = combine_elements_in_string(argv)

		try:
			opts, args = getopt.getopt(argv, "hi:o:u:p:", ["ifile=","ofile=", "ufile=", "pfile="])
		except getopt.GetoptError:
			print("Parameter Error")
			sys.exit(2)

		for opt, arg in opts:
			if opt == '-h':
				#parameter help:
				print("Possible parameters:")
				print("   Inputfile:        -i <path> or -i '/c' (opens file chooser)")
				print("   Outputpath (Lua): -o <path> or")
				print("                     -o '/r' (output in <addon_name>/scripts/vscripts) or")
				print("                     -o '/rs' (output, where mentioned .lua file is located)")
				print("                     -o '/rsa+<alternative>' (like /rs but with alternative,")
				print("                         if there is no mentioned .lua file. Inside /vscripts/)")
				print("   Outputpath (KV):  -u <path> or")
				print("                     -u '/r' (output in <addon_name>/scripts/npc[/abilities])")
				print("                     -u '/rs' (output in <addon_name>/scripts/npc/[origin_path])")
				print("   Project Path:     -p <path> (to set other <addon_name>, use any file from there)")
				print("[Standart] Input: -i /c; Output (Lua/KV): Same as input")
				
			elif opt in ("-i", "--ifile"):
				inputfile = arg
				inputfile = inputfile.replace("\\", "/")
				if not os.path.exists(inputfile) and inputfile != "/c":
					print("Invalid File. Cancel")
					sys.exit()
			elif opt in ("-o", "--ofile"):
				lua_outputpath = arg
			elif opt in ("-u", "--ufile"):
				kv_outputpath = arg
			elif opt in ("-p", "--pfile"):
				project_path = arg

	if inputfile == "/c":
		try:
			Tk().withdraw()
			inputfile = askopenfilename()
		except:
			print("Invalid File. Cancel")
			sys.exit()
		if not os.path.exists(inputfile):
			print("Invalid File. Cancel")
			sys.exit()
	if lua_outputpath == "":
		lua_outputpath = inputfile[:inputfile.rfind("/")]
	elif lua_outputpath == "/r":
		if project_path == "":
			lua_outputpath = get_root_folder(inputfile) + "/scripts/vscripts"
		else:
			lua_outputpath = get_root_folder(project_path) + "/scripts/vscripts"
		if lua_outputpath == "/scripts/vscripts":
			lua_outputpath = inputfile[:inputfile.rfind("/")]
	elif lua_outputpath == "/rs":
		location = find_mentioned_lua_path(inputfile)
		if location != "":
			root_path = get_root_folder(inputfile)
			if project_path != "":
				root_path = get_root_folder(inputfile)
			lua_outputpath = root_path + "/scripts/vscripts/" + location
			if not os.path.exists(lua_outputpath):
				print("Couldn't find mentioned lua path. Cancel")
				sys.exit()
		else:
			print("Couldn't find mentioned lua path. Cancel")
			sys.exit()
	elif "/rsa" in lua_outputpath:
		alternative = lua_outputpath.replace("/rsa+", "")
		location = find_mentioned_lua_path(inputfile)
		root_path = get_root_folder(inputfile)
		if project_path != "":
			root_path = get_root_folder(inputfile)
		if location != "":
			lua_outputpath = root_path + "/scripts/vscripts/" + location
			if not os.path.exists(lua_outputpath):
				print("Couldn't find mentioned lua path. Cancel")
				sys.exit()
		else:
			print("No valid mentioned lua path. Using alternative")
			lua_outputpath = root_path + "/scripts/vscripts/" + alternative
			if not os.path.exists(lua_outputpath):
				print("Couldn't find mentioned lua path. Cancel")
				sys.exit()
	else:
		lua_outputpath = lua_outputpath.replace("\\", "/")
	if kv_outputpath == "":
		kv_outputpath = inputfile[:inputfile.rfind("/")]
	elif kv_outputpath == "/r":
		if project_path == "":
			kv_outputpath = get_root_folder(inputfile) + "/scripts/npc"
		else:
			kv_outputpath = get_root_folder(project_path) + "/scripts/npc"
		if os.path.isdir(kv_outputpath + "/abilities"):
			kv_outputpath += "/abilities"
		if lua_outputpath == "/npc" or lua_outputpath == "/npc/abilities":
			lua_outputpath = inputfile[:inputfile.rfind("/")]
	elif kv_outputpath == "/rs":
		location = get_origin_path(inputfile)
		if location != "":
			kv_outputpath = location
		else:
			print("Couldn't find correct origin path. Cancel")
			sys.exit()
	else:
		kv_outputpath = kv_outputpath.replace("\\", "/")

	print("\nRunning with: \n  Input: " + inputfile)
	print("  Output (Lua):" + lua_outputpath + "\n  Output (KV): " + kv_outputpath)

	run(inputfile, lua_outputpath, kv_outputpath)

def combine_elements_in_string(string_list):
	string_start = False
	temp_string = '"'
	new_list = []
	for x in string_list:
		if '"' in x:
			if string_start == False:
				x = x[x.find('"') + 1:]
				string_start = True
			else:
				x = x[:x.find('"')]
				temp_string += x + '"'
				x = temp_string
				temp_string = '"'
				string_start = False
		if string_start == True:
			temp_string += x + " "
		else:
			new_list.append(x)
	return new_list

def run(inputfile, lua_output, kv_output):

	print("run!")

	kv_master = read_file(inputfile)
	print(inputfile)
	for x in split_to_spells(kv_master):

		components = get_spell_components(x)
		class_name = x.get_name()
		lua_file_name = lua_output + "/" +  class_name

		text = create_lua_file(class_name)
		for y in components['functions']:
			text += "\n\n" + str(create_lua_function(y, class_name, inputfile))
		kv_text = combine_to_KV_text(x, components, lua_file_name)
		old_functions = get_old_functions(x, x.get_name(), get_root_folder(inputfile))
		print("\nPrint Old Functions:\n")
		#print(old_functions)

		modifiers = convert_all_modifiers(components, lua_file_name)
		modifier_text = ""
		for x in modifiers:
			modifier_text += str(x)
		modifier_link = ""
		for x in modifiers:
			modifier_link += x.get_link()
		passives = define_passives(class_name, modifiers)
		print("\nPrint Passives:\n")
		print(passives)

		text = modifier_link + "\n\n--Spell Function\n\n" + text + passives
		text += "\n\n--Old Functions\n\n" + old_functions + "\n\n--Modifiers\n\n" + modifier_text

		#print("\nPrinting Text:\n")
		#print(text)

		try:
			lua_file = open(lua_file_name + ".lua", "w+")
			lua_file.write(text)
			lua_file.close()
		except Exception as e:
			print("Something went wrong!")
			return
		try:
			kv_file_name = kv_output + "/" +  class_name + "_lua.txt"
			kv_file = open(kv_file_name, "w+")
			kv_file.write(str(kv_text))
			kv_file.close()
		except Exception as e:
			print("Something went wrong!")
			return
			
	print("\n\nCompiling succesful!")
	print("Open output folder? (y/n)")
	try:
		user_input = input("> ")
		if user_input == "y":
			os.startfile(lua_output)
			os.startfile(ks_output)
	except Exception as e:
		sys.exit()
	finally:
		print("Exiting...")
		sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])