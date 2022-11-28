"""Collection of scripts / recipes
"""

_byte_array = bytearray(b'\xFF\x0F')
print(_byte_array)

_byte_array[1] = 255
print(_byte_array)
_byte_array.append(128)
print(_byte_array)


def string_with_padding():
    """How to add padding to a f-string"""
    message = "Hello World"
    padding = 10
    message_padded = f'{len(message):<{padding}}{message}'
    print(f'Message = {message}')
    print(f'Padding = {padding}')
    print(f'Message Padded = {message_padded}')

string_with_padding()