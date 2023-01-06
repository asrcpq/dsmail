from pathlib import Path, PurePath
from emparse import load_email
from emutil import llget

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
