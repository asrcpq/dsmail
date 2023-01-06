from emutil import parse_body, proc_word, split_block, llget, test_attachment

def pw(s, code):
	return f"[3{code}m{s}[0m"

def parse_header(lines):
	headers = []
	tmp_header = None
	for line in lines:
		line = line.rstrip()
		cont = line[0].isspace()
		line = " ".join([proc_word(w) for w in line.split(" ")]) # RFC2047
		if cont:
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
		fields = [f.strip() for f in header[1].split(";")]
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
	ct = llget(header, "Content-Type")[0]
	if ct[1].startswith("multipart"):
		delim = llget(ct[2], "boundary")[0][1]
		blocks = []
		linebuf = []
		first = True
		for line in body:
			line = line.rstrip()
			if delim in line: # NOTE: maybe more strict test?
				if first:
					first = False
					linebuf = []
					continue
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

def block_summary(b):
	at = test_attachment(b[0])
	if at:
		print(at, len(b[1]))

def summary(idx, path):
	(h, bs) = load_email(path)
	h_from = llget(h, "From")[0][1]
	h_to = llget(h, "To")[0][1]
	h_sub = llget(h, "Subject")[0][1]
	print(pw(str(idx), 1), pw(h_from, 3), pw(h_to, 2), type(bs).__name__, len(bs), path)
	print("\t" + h_sub)
	if isinstance(bs, list):
		for b in bs:
			block_summary(b)

if __name__ == "__main__":
	import sys
	for (idx, path) in enumerate(sys.argv[1:]):
		summary(idx, path)
