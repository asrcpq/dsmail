import os, sys, datetime
import imaplib, tomllib
import time
from pathlib import Path

def chk(x):
	ret, data = x
	if ret != "OK":
		raise Exception((ret, data))
	return data

# the format of saved mail is {localdir}/{epoch}_{name}_{idx}.eml
# so this util shouldn't be executed for more than once in a second
def get_epoch():
	import time
	epoch = int(time.time())
	for ent in os.listdir(localdir):
		if ent.startswith(str(epoch)):
			raise Exception("executed more than once in 1 second!")
	return epoch

def login(ac):
	m = imaplib.IMAP4_SSL(ac["address"])
	chk(m.login(ac["username"], ac["password"]))
	return m

def create_archive_dir(m):
	data = chk(m.list())
	found = False
	for line in data:
		# should only have 3 
		sp = line.decode().rsplit(" ", 2)
		[prop, delim, path] = sp
		# dirty
		path = path.removeprefix('"')
		path = path.removesuffix('"')
		if path == f"Archive":
			found = True
			break
	if not found:
		chk(m.create(f"Archive"))

def get_indices(name, m, box):
	(rep, data) = m.search(None, "ALL")
	indices = data[0]
	count = len(indices.split())
	print(f"{name}/{box}: {count} mails", file = sys.stderr)
	return indices

def proc_download(name, m, box, indices):
	for i in indices.split():
		data = chk(m.fetch(i, "(RFC822)"))
		data = data[0][1]
		with open(f"{localdir}/{epoch}_{name}_{box}_{i.decode()}.eml", "wb") as f:
			f.write(data)
			print(f"recv mail size: {len(data)}", file = sys.stderr)

def proc_copy(m, indices):
	for i in reversed(indices.split()):
		chk(m.copy(i, f"Archive"))
		m.store(i, "+FLAGS", "\\Deleted")
	# m.expunge()

def proc_account(name, m, box):
	create_archive_dir(m)
	chk(m.select(box))
	indices = get_indices(name, m, box)
	proc_download(name, m, box, indices)
	proc_copy(m, indices)
	m.close()

# prepare global variables
localdir = "data/inbox"
epoch = get_epoch()

if __name__ == "__main__":
	Path(f"data").mkdir(exist_ok = True)
	for directory in ["inbox", "todo", "archive", "extract"]:
		Path(f"data/{directory}").mkdir(exist_ok = True)
	conf = tomllib.load(open(sys.argv[1], "rb"))
	for (name, ac) in conf["accounts"].items():
		m = login(ac)
		for sel in ac["select"]:
			try:
				proc_account(name, m, sel)
			except:
				import traceback
				m.logout()
				raise Exception(traceback.format_exc())
		m.logout()
