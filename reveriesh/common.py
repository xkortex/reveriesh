class SIG_REVERIESH(object):
    KILL = 'SIG_REVERIESH_KILL'.encode()
    PROMPT = 'SIG_REVERIESH_PROMPT'.encode()


class ascii_format:
    magenta = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    clear = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

    def __new__(cls, s, f=None):
        return ascii_format.format(s, f)

    @staticmethod
    def from_int(i):
        return '\033[{}m'.format(i)

    @staticmethod
    def format(s, f=None):
        if f is None:
            f = ascii_format.clear
        elif isinstance(f, int):
            f = ascii_format.from_int(f)
        elif isinstance(f, str):
            f = getattr(ascii_format, f)
        else:
            raise ValueError('Invalid format type: {}'.format(type(f)))

        return '{}{}{}'.format(f, s, ascii_format.clear)


"""WORK IN PROGRESS """
def marshall_item(x):
    # type: (Any) -> bytes
    """Marshall data into binary format
    Right now, only working with strings, so we can take some shortcuts
    with deliminators
    """
    if isinstance(x, bytes):
        return x
    if isinstance(x, str):
        return x.encode()
    raise TypeError('Cannot marshall type: {}'.format(type(x)))

def unmarshall_item(x):
    # type: (bytes) -> str
    try:
        return x.decode()
    except Exception as exc:
        raise TypeError('Cannot marshall data: {}'.format(type(x)))


def dictpack(dd):
    # type: (dict) -> bytes
    out = b''
    for k, v in dd.items():
        ke = marshall_item(k)
        kv = marshall_item(v)


def dictunpack():
    # type: (bytes) -> dict
    pass


