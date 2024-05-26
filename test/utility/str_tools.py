def to_bytes(s):
    if isinstance(s, str):
        return s.encode('utf8')
    return s
