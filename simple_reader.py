import email
import os, shutil

dir_inbox = 'inbox'
dir_archive = 'archive'
def dec(raw):
	(data, enc) = email.header.decode_header(raw)[0]
	if not enc:
		s = data
	else:
		s = data.decode(enc)
	return s

def eml2plain(msg):
	headers = msg.items()
	result = ""
	for header in headers:
		if header[0] in ["Date", "Reply-To", "Subject", "To", "Cc", "From"]:
			result += f"{header[0]}: {dec(header[1])}\n"
	for part in msg.walk():
		ct = part.get_content_type()
		match ct:
			case 'text/plain':
				payload = part.get_payload(decode=True)
				result += payload.decode()
			case _:
				result += f"skip {ct} with len {len(part.get_payload())}\n"
	return result

def action(file, s, e):
	action = input(f"action [32m>[0m ")
	match action:
		case "s": # skip
			pass
		case "a": # archive
			shutil.move(f"{dir_inbox}/{file}", f"{dir_archive}/{file}")
		case "d": # detail
			print(file)
			print(eml2plain(e))
			return False
		case _:
			print("[31mbad input[0m")
			return False
	return True

count1 = len(os.listdir(dir_inbox))
print(f"Proc {count1}")
for file in os.listdir(dir_inbox):
	e = email.message_from_file(open(f"{dir_inbox}/{file}"))
	f = dec(e.get("from"))
	t = dec(e.get("to"))
	print(f"{f} [33m->[0m {t}")
	s = dec(e.get("subject"))
	print(s)
	while True:
		if action(file, s, e):
			break
count2 = len(os.listdir('./inbox'))
print(f"Proc {count1} -> {count2}")
