from email.header import decode_header

def llget(d, key):
	result = []
	for (k, v) in d:
		if k == key:
			result.append(v)
	return result

def proc_block(block):
	header = []
	res = stage1(block)
	print(res["header"])

	disp = llget(res["header"], "Content-Disposition")
	if len(disp) > 0:
		fields = disp[0].split(";")
		if fields[0] == "attachment":
			fields[1].strip()
			print("attachment: {}")

def stage2(lines, ty):
	result = {}
	if ty == "multipart/mixed":
		delim = lines[0]
		# split blocks
		blocks = []
		current_block = []
		for line in lines[1:]:
			if line == delim:
				blocks.append(current_block)
				current_block = []
				continue
			current_block.append(line)
		for block in blocks:
			proc_block(block)
		return {
			"body": "\n".join(["\n".join(block) + "\n" for block in blocks]),
			"attachments": [],
		}
	# TODO: html render
	if ty == "text/plain" or ty == "text/html":
		return {
			"body": "\n".join(lines),
			"attachments": [],
		}
	else:
		raise Exception(f"Unhandled type {ty}")

def stage1(b):
	header = []
	body = []
	tmp_header = None
	break_point = 0
	for (idx, line) in enumerate(b):
		line = line.rstrip()
		if not line:
			break_point = idx
			break
		if line[0].isspace():
			tmp_header[1] += ' '
			for word in line.split():
				if word.startswith("=?") and word.endswith("?="):
					(data, enc) = decode_header(word)[0]
					word = data.decode(enc)
				tmp_header[1] += ' ' + word
			continue
		if tmp_header:
			header.append(tmp_header)
			tmp_header = None
		sp = line.split(': ', 1)
		if len(sp) == 2:
			tmp_header = [sp[0], sp[1]]
		else:
			tmp_header = [sp[0], ""]
	return {
		"header": header,
		"body": b[break_point + 1:],
	}

# python email module cannot handle modern mails, just write a simple one
def load_email(f):
	e = stage1(open(f).read().splitlines())
	ct = llget(e["header"], "Content-Type")[0].split(";")[0]
	new = stage2(e["body"], ct)
	e |= new
	return e

if __name__ == "__main__":
	import sys
	e = load_email(sys.argv[1])
	for k, v in e["header"]:
		if k in ["Subject", "From", "Sender", "To", "Date"]:
			print(f"[33m{k}:[0m {v}")
	print()
	# print(e["body"])
	# print()
	# print(llget(e["header"], "Subject"))
