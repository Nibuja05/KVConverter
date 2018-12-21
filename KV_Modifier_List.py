

def get_function_name_list():
	return ["OnAttackLanded", "OnCreated", "OnIntervalThink", "OnTakeDamage", "OnDestroy"]

def get_particle_constant(attach):
	if attach == "follow_origin":
		return "PATTACH_ABSORIGIN_FOLLOW"
	elif attach == "follow_overhead":
		return "PATTACH_OVERHEAD_FOLLOW"
	elif attach == "attach_origin":
		return "PATTACH_ABSORIGIN"
	elif attach == "attach_hitloc":
		return "PATTACH_POINT"
	elif attach == "follow_hitloc":
		return "PATTACH_POINT_FOLLOW"

def get_constant_function_by_name(name):
	if name == "IsHidden":
		return "IsHidden"
	elif name == "IsDebuff":
		return "IsDebuff"
	elif name == "IsPurgable":
		return "IsPurgable"
	elif name == "Attributes":
		return "GetAttributes"
	elif name == "Aura":
		return "IsAura"
	elif name == "Aura_Radius":
		return "GetAuraRadius"
	elif name == "Aura_Flags":
		return "GetAuraSearchFlags"
	elif name == "Aura_Types":
		return "GetAuraSearchType"
	elif name == "Aura_Teams":
		return "GetAuraSearchTeam"
	elif name == "EffectName":
		return "GetEffectName"
	elif name == "StatusEffectName":
		return "GetStatusEffectName"
	elif name == "StatusEffectPriority":
		return "GetStatusEffectPriority"
	else:
		return ""