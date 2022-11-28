"""Collection of scripts / recipes
"""

def byte_array_functions():
    _byte_array = bytearray(b'\xFF\x0F')
    print(_byte_array)

    _byte_array[1] = 255
    print(_byte_array)
    _byte_array.append(128)
    print(_byte_array)

# byte_array_functions()

def string_with_padding():
    """How to add padding to a f-string"""
    message = "Hello World"
    padding = 10
    message_padded = f'{len(message):<{padding}}{message}'
    print(f'Message = {message}')
    print(f'Padding = {padding}')
    print(f'Message Padded = {message_padded}')

# string_with_padding()



def struct_package():
    import struct
    #payload_size = struct.calcsize('>L')
    #print(payload_size)
    print(struct.calcsize('>l'))
    print(struct.calcsize('>L'))
    print(struct.calcsize('=L'))

    print(struct.calcsize('=f'))
    print(struct.calcsize('=d'))
    print(struct.calcsize('>f'))
    print(struct.calcsize('>d'))

    print(struct.calcsize('<f'))
    print(struct.calcsize('<d'))

    print(struct.calcsize('@l'))
    print(struct.calcsize('@L'))
    print(struct.calcsize('@f'))
    print(struct.calcsize('@d'))


    message = "Hello world".encode('utf-8')
    message = message[:struct.calcsize(">L")]

    message_unpacked = struct.unpack(">L", message)
    print(message_unpacked)

    packed = struct.pack('i', 4)
    print(packed)
    INT_MAX = 2147483647
    packed = struct.pack('i', INT_MAX)
    print(packed)

    packed = struct.pack('i', INT_MAX)
    print(packed)


struct_package()

