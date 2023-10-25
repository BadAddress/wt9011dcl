
val = b'\x50\x22'
intval = int.from_bytes(val, signed=True)
print(intval)
