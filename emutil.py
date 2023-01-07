from email.header import decode_header
import quopri, base64

def parse_percentage(s):
	bs = []
	idx = 0
	while True:
		if idx >= len(s):
			break
		if s[idx] == "%":
			i = int(s[idx + 1] + s[idx + 2], 16)
			idx += 3
			bs.append(i)
		else:
			bs.append(ord(s[idx]))
			idx += 1
	bs = bytes(bs)
	return bs

# split block to head and body
def split_block(lines):
	split1 = None
	for (idx, line) in enumerate(lines):
		line = line.rstrip()
		if not line:
			split = idx
			break
	return (lines[:split], lines[split + 1:])

# convert RFC2047
def proc_word(word):
	if word.startswith("=?") and word.endswith("?="):
		(data, enc) = decode_header(word)[0]
		try:
			word = data.decode(enc)
		except UnicodeDecodeError:
			print("ERROR: invalid unicode")
			word = data.decode(enc, errors = "ignore")
		return word
	else:
		return word

def llget(d, key):
	result = []
	for l in d:
		if l[0] == key:
			result.append(l)
	return result

def parse_body(lines, header):
	cte = llget(header, "content-transfer-encoding")
	lines = "\n".join(lines)
	if len(cte) > 0:
		match cte[0][1].lower():
			case "quoted-printable":
				lines = quopri.decodestring(lines)
			case "base64":
				try:
					lines = base64.b64decode(lines)
				except Exception as e:
					lines = b"INVALID BASE64 DATA SKIPPED"
			case "7bit" | "8bit":
				pass
			case e:
				raise Exception(e)

	ct = llget(header, "content-type")[0]
	for [k, v] in ct[2]:
		if k == "charset":
			if isinstance(lines, str):
				lines = lines.encode()
			# lines = lines.decode(v)
			lines = lines.decode(v, errors = "replace")
			break
	return lines

def test_attachment(header):
	cd = llget(header, "content-disposition")
	if len(cd) > 0:
		vall = ""
		enc = ""
		if cd[0][1] == "attachment":
			for [k, v] in cd[0][2]:
				if k == "filename":
					return v
				# RFC2231
				if k.startswith("filename"):
					v = v.rsplit("=", 1)[-1]
					sp = v.rsplit("'")
					if len(sp) == 3:
						enc = sp[0]
					v = sp[-1]
					v = v.split(";", 1)[0]
					vall += v
		if vall:
			# vall = vall.replace("%", "")
			# bs = bytes.fromhex(vall)
			bs = parse_percentage(vall)
			return bs.decode(enc)
	return ""
