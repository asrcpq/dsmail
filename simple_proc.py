from emparse import load_email, llget, block_summary, pw, summary
from extractor import extract
from pathlib import PurePath
import os, shutil, sys
import unicodedata

def action(table):
	try:
		s = input("> ")
	except EOFError:
		print("EOF exit")
		sys.exit(0)
	ws = s.split()
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
				directory = "extract/{name}"
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
	"e": "extract",
}

def ptable():
	table = []
	for idx, file in enumerate(os.listdir(source)):
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
