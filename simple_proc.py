from emparse import load_email, summary, display_email
from emutil import llget
from extractor import extract
from pathlib import PurePath
import os, shutil, sys, readline
import unicodedata
from subprocess import Popen, PIPE

def header_item(h, key):
	result = ""
	g = llget(h, key)
	for gg in g:
		result += key + ": " + gg[1] + "\n"
	return result

def action_read(fn):
	path = f"{source}/{fn}"
	(h, b) = load_email(path)

	hs = ""
	hs += header_item(h, "from")
	hs += header_item(h, "to")
	hs += header_item(h, "subject")

	proc = Popen(["less"], stdin = PIPE)
	proc.stdin.write(hs.encode())
	proc.stdin.write(b"\n")
	proc.stdin.write(display_email(h, b).encode())
	proc.stdin.close()
	proc.wait()

def action(table):
	try:
		s = input("> ")
	except EOFError:
		print("EOF exit")
		sys.exit(0)
	ws = s.split()
	
	flag = True
	match ws[0]:
		case "r":
			if len(ws) != 2:
				print("bad read arity")
				return
			action_read(table[int(ws[1])])
		case "q":
			sys.exit(0)
		case _:
			flag = False
	if flag:
		return

	if len(ws) == 0:
		return
	try:
		target = target_dict[ws[0]]
	except:
		print("bad key")
		return
	for w in ws[1:]:
		fn = table[int(w)]
		src = f"{source}/{fn}"

		if target == "extract":
			extract(src)
		else:
			shutil.move(src, f"{target}/{fn}")

			# archive mode, remove extracted
			if target == "archive":
				name = PurePath(f"{target}/{fn}").stem
				directory = f"extract/{name}"
				if os.path.exists(directory):
					shutil.rmtree(directory)

source = "inbox"
if len(sys.argv) >= 2:
	match sys.argv[1]:
		case "inbox":
			pass
		case "todo":
			source = "todo"
		case _:
			raise Exception(sys.argv[1])

target_dict = {
	"a": "archive",
	"t": "todo",
	"x": "extract",
}

def ptable():
	table = []
	max_items = 20
	# max_items = None
	for idx, file in enumerate(os.listdir(source)[:max_items]):
		table.append(file)
		ll = 20
		summary(idx, f"{source}/{file}")
	return table

while True:
	table = ptable()
	if not table:
		print("All mails proc, exit")
		sys.exit(0)
	action(table)
