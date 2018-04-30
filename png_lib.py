import binascii
import zlib


def _pack_int(int, length):
    return int.to_bytes(length, byteorder = "big")
    
def _to_int(byte):
    return int.from_bytes(byte, byteorder = "big")

class png:

    _file_header = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
    _IEND = b"\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82"
    _IEND_chunk = None
    

    def __init__(self, filename = None, data = None, **kwargs):
        self.filename = filename
        self.chunks = []
        self._data = data
        if self._data is not None:
            self.width = len(data[0])
            self.height = len(data)
        else:
            self.width = None
            self.height = None
        self.bit_depth = kwargs.get("bit_depth", 8) #8 - 0..255
        self.color_type = kwargs.get("color_type", 6) #6 - truecolor with alpha
        self.compression_method = kwargs.get("compression_method", 0) #Standard
        self.filter_method = kwargs.get("filter_method", 0) #Standard
        self.interlace_method = kwargs.get("interlace_method", 0) #No interlace
    
    def get_data(self):
        return self._data
    
    def set_data(self, data):
        self._data = data
        self.width = len(data[0])
        self.height = len(data)
        return self._data
    
    def get_IHDR(self):
        chunk = _png_chunk()
        chunk.set_length(13) #length of IHDR is 13
        chunk.set_type("IHDR") #IHDR chunk
        chunk.data = b""
        chunk.data += _pack_int(self.width, 4)
        chunk.data += _pack_int(self.height, 4)
        chunk.data += _pack_int(self.bit_depth, 1)
        chunk.data += _pack_int(self.color_type, 1)
        chunk.data += _pack_int(self.compression_method, 1)
        chunk.data += _pack_int(self.filter_method, 1)
        chunk.data += _pack_int(self.interlace_method, 1)
        chunk.set_crc()
        return chunk
    
    #currently only support filter type 0 (None)
    #currently only support colot type 6 (truecolor with alpha)
    #currently only support bit depth = 8 (1 byte per channel)
    #currently only support interlace method 0 (no interlace)
    def get_IDAT(self, data = None):
        if data is None:
            data = self._data
        chunk = _png_chunk()
        chunk.set_type("IDAT")
        raw_data = b""
        for row in data:
            raw_data += b"\x00"
            for pixel in row:
                for values in pixel:
                    raw_data += _pack_int(values, 1)
        chunk.data = zlib.compress(raw_data, level=9)
        chunk.set_length(len(chunk.data))
        chunk.set_crc()
        return chunk
    
    def get_IEND(self):
        if png._IEND_chunk is None:
            png._IEND_chunk = _png_chunk()
            png._IEND_chunk.set_length(0) #IEND's data field is empty
            png._IEND_chunk.read_chunk(png._IEND)
        return png._IEND_chunk
    
    def custom_chunk(self, chunk_type, chunk_data):
        chunk = _png_chunk()
        chunk.set_length = len(chunk_data)
        chunk.set_type(chunk_type)
        chunk.data = chunk_data
        chunk.set_crc()
        return chunk
    
    def create_png(self, filename = None):
        if filename is None:
            filename = self.filename
        with open(filename, "xb") as png_f:
            png_f.write(png._file_header)
            for chunk in self.chunks:
                png_f.write(chunk.get_chunk())
    
    #auto create chunks, WARNING: will remove original chunks
    def smart_create(self, filename = None):
        self.chunks = []
        self.append(self.get_IHDR())
        self.append(self.get_IDAT())
        self.append(self.get_IEND())
        self.create_png(filename)
    
    def append(self, chunk):
        self.chunks.append(chunk)
    
    
    def enlarge_pixel_data(self, scale = 2):
        new_data = []
        for i in range(len(self._data)):
            new_data.append([])
            for j in range(len(self._data[0])):
                for _ in range(scale):
                    new_data[-1].append(self._data[i][j])
            for _ in range(scale - 1):
                new_data.append(new_data[-1])
        self.set_data(new_data)
        return new_data

class _png_chunk:
    
    def __init__(self, length = None, type = None, data = None, crc = None):
        self.length = length #in raw format
        self._length = None #in int format
        self.type = type
        self.data = data
        self.crc = crc
        
    def read_length(self, bytes):
        self.length = bytes[:4]
        return self.length
        
    def read_type(self, bytes):
        self.type = bytes[4:8]
        return self.type
        
    def read_data(self, bytes):
        self.data = bytes[8 : 8+self.get_length()]
        return self.data
    
    def read_crc(self, bytes):
        self.crc = bytes[8+self.get_length() : 8+self.get_length()+4]
        return self.crc
        
    def read_chunk(self, bytes):
        self.read_length(bytes)
        self.read_type(bytes)
        self.read_data(bytes)
        self.read_crc(bytes)
        return 4 + 4 + self.get_length() + 4
        
    def get_length(self):
        if self._length is None:
            self._length = int.from_bytes(self.length, byteorder = "big")
        return self._length
        
    def set_length(self, length_in_int):
        self.length = _pack_int(length_in_int, 4)
        return self.length
        
    def get_type(self):
        return self.type.decode("ascii")
        
    def set_type(self, type_in_str):
        self.type = type_in_str.encode("ascii")
        return self.type
        
    def set_crc(self):
        crc_int = binascii.crc32(self.type + self.data) & 0xffffffff
        self.crc = _pack_int(crc_int, 4)
        return self.crc
    
    def get_chunk(self):
        return self.length + self.type + self.data + self.crc
        
    def _print_chunk(self):
        print(hex(int.from_bytes(get_chunk, byteorder = "big")))
        
    @staticmethod
    def _hex_string(bytes):
        bytes_str = hex(int.from_bytes(bytes, byteorder = "big")).upper()[2:]
        if len(bytes_str) % 2 == 1:
            bytes_str = "0" + bytes_str
        num_leading_zero = len(bytes) - len(bytes_str)//2
        bytes_str = "00"*num_leading_zero + bytes_str
        return bytes_str

