from pathlib import Path, PurePath
from emparse import load_email
from emutil import llget, test_attachment

def extract(path):
	(h, bs) = load_email(path)
	name = PurePath(path).stem
	p = Path(f"extract/{name}")
	if p.exists():
		print(f"already extracted {p}")
		return
	p.mkdir()

	if isinstance(bs, str):
		with open(f"extract/{name}/body", "w") as f:
			print(bs, file = f)
		return
		
	for idx, (h, b) in enumerate(bs):
		suffix = test_attachment(h)
		if not at:
			suffix = ""
		ext = ""
		match llget(h, "Content-Type")[0][1]:
			case "application/x-zip-compression":
				ext = ".zip"
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
