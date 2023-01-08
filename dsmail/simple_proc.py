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
	# proc = Popen(["cat"], stdin = PIPE)
	proc.stdin.write(hs.encode())
	proc.stdin.write(b"\n")
	proc.stdin.write(display_email(h, b).encode())
	proc.stdin.close()
	proc.wait()

def action1(ws, table):
	global flush
	match ws[0]:
		case "r":
			if len(ws) != 2:
				print("bad read arity")
				return
			try:
				action_read(table[int(ws[1])])
			except Exception as e:
				print("read failed:", e)
		case "p":
			flush = True
		case "q":
			sys.exit(0)
		case _:
			return False
	return True

def action(table):
	global flush
	try:
		s = input("> ")
	except EOFError:
		print("EOF exit")
		sys.exit(0)
	ws = s.split()
	if action1(ws, table):
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
			continue
		flush = True
		shutil.move(src, f"data/{target}/{fn}")

		# archive mode, remove extracted
		if target == "archive":
			name = PurePath(f"data/{target}/{fn}").stem
			directory = f"data/extract/{name}"
			if os.path.exists(directory):
				print("remove extracted", directory)
				shutil.rmtree(directory)

if len(sys.argv) >= 2:
	match sys.argv[1]:
		case "inbox":
			source = "data/inbox"
		case "todo":
			source = "data/todo"
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

flush = True
while True:
	if flush:
		table = ptable()
		flush = False
	if not table:
		print("All mails proc, exit")
		sys.exit(0)
	action(table)
