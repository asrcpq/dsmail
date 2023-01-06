from email.header import decode_header

def llget(d, key):
	result = []
	for (k, v) in d:
		if k == key:
			result.append(v)
	return result

def proc_word(word):
	if word.startswith("=?") and word.endswith("?="):
		(data, enc) = decode_header(word)[0]
		word = data.decode(enc)
		return word
	else:
		return word

def proc_line(line):
	return " ".join([proc_word(word) for word in line.split()])

def proc_block(block):
	header = []
	res = stage1(block)

	disp = llget(res["header"], "Content-Disposition")
	if len(disp) > 0:
		fields = disp[0].split(";")
		if fields[0] == "attachment":
			fn = ""
			for field in fields:
				field = field.strip()
				sp = field.split("=", 1)
				if sp[0] == "filename":
					# NOTE: dirty
					fns = sp[1].removeprefix('"')
					fns = fns.removesuffix('"')
					for word in fns.split():
						fn += proc_word(word)
			return ("attachment", fn)
	return ("content", "unimpl")

def stage2(lines, ty):
	result = {}
	if ty == "multipart/mixed":
		delim = lines[0]
		# split blocks
		blocks = []
		attachments = []
		contents = []
		current_block = []
		for line in lines[1:]:
			if line == delim:
				blocks.append(current_block)
				current_block = []
				continue
			current_block.append(line)
		for block in blocks:
			(ty, body) = proc_block(block)
			if ty == "attachment":
				attachments.append(body)
			else:
				contents.append(body)
		return {
			"body": "\n".join(["\n".join(content) for content in contents]),
			"attachments": attachments,
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
			line = proc_line(line)
			tmp_header[1] += " " + line
			continue
		if tmp_header:
			header.append(tmp_header)
			tmp_header = None
		sp = line.split(': ', 1)
		if len(sp) == 2:
			line = proc_line(sp[1])
			tmp_header = [sp[0], line]
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
