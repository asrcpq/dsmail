from emparse import load_email, llget
import os, shutil, sys
import unicodedata

def pw(s, code):
	return f"[3{code}m{s}[0m"

def move(table, target):
	try:
		s = input(target + " > ")
	except EOFError:
		print("EOF exit")
		sys.exit(0)
	for w in s.split():
		fn = table[int(w)]
		shutil.move(f"{source}/{fn}", f"{target}/{fn}")

source = "inbox"
if len(sys.argv) >= 2:
	match sys.argv[1]:
		case "inbox":
			pass
		case "todo":
			source = "todo"
		case _:
			raise Exception(sys.argv[1])

match source:
	case "inbox":
		targets = ["archive", "todo"]
	case "todo":
		targets = ["archive"]
	case _:
		raise Exception("unreachable")

while True:
	table = []
	for idx, file in enumerate(os.listdir(source)):
		table.append(file)
		ll = 20
		e = load_email(f"{source}/{file}")
		h_from = llget(e["header"], "From")[0]
		h_to = llget(e["header"], "To")[0]
		h_sub = llget(e["header"], "Subject")[0]
		print(pw(str(idx), 1), pw(h_from, 3), pw(h_to, 2))
		print("\t" + h_sub)
		for at in e["attachments"]:
			print(pw("\t" + at, 6))
	if not table:
		print("All mails proc, exit")
		break
	for target in targets:
		move(table, target)
