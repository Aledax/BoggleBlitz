import socket
import json
import struct
import pickle

#----------------------------------------------------------------------------
# class EasySocket
#
# Supports sending and receiving complete byte strings (bytes objects),
# handling all buffering and data chunking internally.
#----------------------------------------------------------------------------

class EasySocket:
  def __init__(self, sock=None):
    if sock == None:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.sock = sock
    self.recv_buffer = b''

  def bind(self, hostname, port):
    self.sock.bind((hostname, port))
    
  def listen(self):
    self.sock.listen()
  
  def accept(self):
    (sock, addr) = self.sock.accept()
    return sock
    
  def connect(self, hostname, port):
    try: self.sock.connect((hostname, port))
    except: return False
    return True
  
  @property
  def sockname(self):
    return format_address(self.sock.getsockname())

  @property      
  def peername(self):
    return format_address(self.sock.getpeername())

  def send_all(self, data):
    try: self.sock.sendall(data)
    except: return False
    return True

  def receive_chunk(self):
    # Return the next chunk of data from the socket.
    # Returns None if the socket has been closed.
    try: data = self.sock.recv(4096)
    except: data = b''
    if data == b'': return None
    return data

  # See the packet format description later in this file.

  def packetize(self, bytes):
    # Encapsulate the byte string in a packet for sending
    packetlength = HEADER_LENGTH + len(bytes)
    if packetlength > 2 ** (PKTLEN_LENGTH * 8):
      print('Data size exceeds maximum supported packet size')
      return None
    header = PACKET_MARKER
    header += struct.pack(PKTLEN_FORMAT, packetlength)
    return header + bytes
    
  def unpacketize(self):
    # Scan the receive buffer for the next packet marker.
    # Discard any bytes that don't match the packet marker.
    # Retreive the byte string from the packet.
    while len(self.recv_buffer) >= HEADER_LENGTH \
      and self.recv_buffer[:MARKER_LENGTH] != PACKET_MARKER:
      print('Malformed packet received', bytes([self.recv_buffer[0]]))
      self.recv_buffer = self.recv_buffer[1:]
      
    # Return if no packet marker was found, of if the receive buffer
    # contains insufficient data to retrieve the entire header.
    if len(self.recv_buffer) < HEADER_LENGTH: return None

    # Retrieve the packet length field from the header.
    length = struct.unpack(PKTLEN_FORMAT,
      self.recv_buffer[MARKER_LENGTH:MARKER_LENGTH + PKTLEN_LENGTH])[0]
    
    # Return if the receive buffer contains less than a full packet.
    if len(self.recv_buffer) < length: return None

    # Get the byte string from the packet
    bytes = self.recv_buffer[HEADER_LENGTH:length]
    
    # Remove the packet from the receive buffer.
    self.recv_buffer = self.recv_buffer[length:]

    return bytes

  def sendObject(self, obj):
    self.send(pickle.dumps(obj))
    
  def send(self, data):
    # Sends a complete byte string through the socket.
    # Blocks until the complete byte string has been sent.
    # Returns False if an error is encountered.
    packet = self.packetize(data)
    if packet == None: return False
    return self.send_all(packet)

  def receiveObject(self):
    data = self.receive()
    if data == None: return None
    else: return pickle.loads(data)

  def receive(self):
    # Returns the next complete byte string from the socket.
    # Blocks until a complete byte string has been received.
    # Returns None if the socket has been closed.
    data = self.unpacketize()
    while data == None:
      chunk = self.receive_chunk()
      if chunk == None: return None
      self.recv_buffer += chunk
      data = self.unpacketize()
    return data

#----------------------------------------------------------------------------
# class JsonSocket
#
# Supports sending and receiving complete data structures.
# The data structures must be compatible with JSON encoding.
#----------------------------------------------------------------------------

class JsonSocket(EasySocket):
  def packetize(self, data):
    # Encode the data structure into JSON format and packetize it.
    bytes = json.dumps(data, ensure_ascii=False).encode(ENCODE_FORMAT)
    return super().packetize(bytes)
    
  def unpacketize(self):
    # Unpacketize the payload
    bytes = super().unpacketize()
    if bytes == None: return None
    
    # Decode the JSON-formatted byte string into a data object.
    try:
      data = json.loads(bytes, encoding=ENCODE_FORMAT)
    except:
      print('Malformed JSON data in packet:', self.recv_buffer)
      return None
    return data
    
#----------------------------------------------------------------------------
# class ServerSocket
#----------------------------------------------------------------------------

class ServerSocket(EasySocket):
  def __init__(self, port):
    super().__init__()
    self.bind(input("IPv4 Address: "), port)
    self.listen()

#----------------------------------------------------------------------------
# Packet format
#
# PACKET = <PACKET_HEADER><PACKET_PAYLOAD>
# PACKET_HEADER = <PACKET_MARKER><PACKET_LENGTH>
# PACKET_PAYLOAD = byte string of any length up to 2 ** (PKTLEN_LENGTH * 8)
#----------------------------------------------------------------------------

PACKET_MARKER = b'EZSK'
MARKER_LENGTH = len(PACKET_MARKER)
PKTLEN_FORMAT = '>H'
PKTLEN_LENGTH = 2
HEADER_LENGTH = MARKER_LENGTH + PKTLEN_LENGTH
ENCODE_FORMAT = 'utf-8'

#----------------------------------------------------------------------------
# Helper functions
#----------------------------------------------------------------------------

def format_address(address):
  # Create a compact human-readable string from a socket address
  return address[0] + ":" + str(address[1])
