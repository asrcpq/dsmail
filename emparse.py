from emutil import *
from pathlib import Path, PurePath

def parse_header(lines):
	headers = []
	tmp_header = None
	for line in lines:
		line = line.rstrip()
		if line[0].isspace():
			tmp_header[1] += line.strip()
			continue
		if tmp_header:
			headers.append(tmp_header)
		sp = line.split(": ", 1)
		if len(sp) == 1:
			tmp_header = [sp[0], ""]
		else:
			tmp_header = [sp[0], sp[1]]
	# push the last header field
	if tmp_header:
		headers.append(tmp_header)

	for header in headers:
		fields = header[1].split(";")
		# rfc2047
		for idx in range(len(fields)):
			new_field = [proc_word(w) for w in fields[idx].split(" ")]
			fields[idx] = " ".join(new_field)
		header[1] = fields[0]
		header.append([])
		# x=y
		for idx in range(1, len(fields)):
			sp = fields[idx].split('=', 1)
			if len(sp) == 2:
				v = sp[1]
				# NOTE: dirty
				v = v.removeprefix('"')
				v = v.removesuffix('"')
				v = proc_word(v)
				header[2].append([sp[0], v])
			else:
				header[2].append([sp[0]])
	return headers

def proc_block(lines):
	(header, body) = split_block(lines)
	header = parse_header(header)
	ct = llget(header, "Content-Type")[0][1]
	if ct.startswith("multipart"):
		delim = body[0]
		blocks = []
		linebuf = []
		for line in body[1:]:
			if line == delim or line == delim + "--":
				(h, b) = proc_block(linebuf)
				blocks.append((h, b))
				linebuf = []
			else:
				linebuf.append(line)
	else:
		blocks = parse_body(body, header)
	return (header, blocks)

def load_email(f):
	lines = open(f).read().splitlines()
	return proc_block(lines)

def print_block(b):
	if isinstance(b[1], list):
		print(b[0], len(b[1]))
		for b in b[1]:
			print_block(b)
		return
	print(b[0], len(b[1]))

def extract(path):
	(h, bs) = load_email(path)
	name = PurePath(path).stem
	Path(f"extract/{name}").mkdir()

	if isinstance(bs, str):
		with open(f"extract/{name}/body", "w") as f:
			print(bs, file = f)
		return
		
	for idx, (h, b) in enumerate(bs):
		cd = llget(h, "Content-Disposition")
		suffix = ""
		if len(cd) > 0:
			if cd[0][1] == "attachment":
				for [k, v] in cd[0][2]:
					if k == "filename":
						suffix = f"-{v}"
						break
		ext = ""
		match llget(h, "Content-Type")[0][1]:
			case "application/x-zip-compression":
				ext = ".xz"
		path = f"extract/{name}/{idx}{suffix}{ext}"
		if isinstance(b, str):
			with open(path, "w") as f:
				print(b, file = f)
		elif isinstance(b, bytes):
			with open(path, "wb") as f:
				f.write(b)
		else:
			raise Exception(type(b))

if __name__ == "__main__":
	import sys
	extract(sys.argv[1])
