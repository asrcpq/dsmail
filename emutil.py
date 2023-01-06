from email.header import decode_header
import quopri, base64

def split_block(lines):
	split_point = None
	for (idx, line) in enumerate(lines):
		line = line.rstrip()
		if not line:
			split_point = idx
			break
	return (lines[:split_point], lines[split_point + 1:])

def proc_word(word):
	if word.startswith("=?") and word.endswith("?="):
		(data, enc) = decode_header(word)[0]
		word = data.decode(enc)
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
	cte = llget(header, "Content-Transfer-Encoding")
	lines = "\n".join(lines)
	if len(cte) > 0:
		match cte[0][1]:
			case "quoted-printable":
				lines = quopri.decodestring(lines)
			case "base64":
				lines =base64.b64decode(lines)
			case "7bit" | "8bit":
				pass
			case e:
				raise Exception(e)

	ct = llget(header, "Content-Type")[0]
	for [k, v] in ct[2]:
		if k == "charset":
			if isinstance(lines, str):
				lines = lines.encode()
			# lines = lines.decode(v)
			lines = lines.decode(v, errors = "replace")
			break
	return lines
