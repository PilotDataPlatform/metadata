import base64
import re
import math

def encode_label_for_ltree(raw_string: str) -> str:
    base32_string = str(base64.b32encode(raw_string.encode('utf-8')), 'utf-8')
    return re.sub('=', '', base32_string)

def encode_path_for_ltree(raw_path: str) -> str:
    labels = raw_path.split('.')
    path = ''
    for label in labels:
        path += f'{encode_label_for_ltree(label)}.'
    return path[:-1]

def decode_label_from_ltree(encoded_string: str) -> str:
    missing_padding = math.ceil(len(encoded_string) / 8) * 8 - len(encoded_string)
    if missing_padding:
        encoded_string += '=' * missing_padding
    utf8_string = base64.b32decode(encoded_string.encode('utf-8')).decode('utf-8')
    return utf8_string

def decode_path_from_ltree(encoded_path: str) -> str:
    labels = encoded_path.split('.')
    path = ''
    for label in labels:
        path += f'{decode_label_from_ltree(label)}.'
    return path[:-1]
