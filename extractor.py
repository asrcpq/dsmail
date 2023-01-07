from pathlib import Path, PurePath
from emparse import load_email
from emutil import llget, test_attachment

def mime2ext(s):
	ext = ""
	match s.lower():
		case "text/html":
			ext = ".html"
		case "text/plain":
			ext = ".txt"
		case "application/x-zip-compression":
			ext = ".zip"
	return ext

def extract(path):
	(h, bs) = load_email(path)
	name = PurePath(path).stem
	p = Path(f"extract/{name}")
	if p.exists():
		print(f"already extracted {p}")
		return
	p.mkdir()

	if isinstance(bs, str):
		ext = mime2ext(llget(h, "content-type")[0][1])
		with open(f"extract/{name}/body{ext}", "w") as f:
			print(bs, file = f)
		return
		
	for idx, (h, b) in enumerate(bs):
		suffix = test_attachment(h)
		ext = mime2ext(llget(h, "content-type")[0][1])
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
