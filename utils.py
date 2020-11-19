
def str2bool(s: str):
	s = s.lower()
	if s == "true" or s == "1" or s == "yes":
		return True
	else:
		return False
