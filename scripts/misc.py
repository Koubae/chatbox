"""Collection of scripts / recipes
"""

_byte_array = bytearray(b'\xFF\x0F')
print(_byte_array)

_byte_array[1] = 255
print(_byte_array)
_byte_array.append(128)
print(_byte_array)