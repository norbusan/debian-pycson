import re, json, sys

if sys.version_info[0] == 2:
    def _is_num(o):
        return isinstance(o, int) or isinstance(o, long) or isinstance(o, float)
    def _stringify(o):
        if isinstance(o, str):
            return unicode(o)
        if isinstance(o, unicode):
            return o
        return None
else:
    def _is_num(o):
        return isinstance(o, int) or isinstance(o, float)
    def _stringify(o):
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, str):
            return o
        return None

_id_re = re.compile(r'[$a-zA-Z_][$0-9a-zA-Z_]*\Z')

class CSONEncoder:
    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
            indent=None, default=None):
        self._skipkeys = skipkeys
        self._ensure_ascii = ensure_ascii
        self._allow_nan = allow_nan
        self._sort_keys = sort_keys
        self._indent = ' ' * (indent or 4)
        self._default = default
        if check_circular:
            self._obj_stack = set()
        else:
            self._obj_stack = None

    def _format_simple_val(self, o):
        if o is None:
            return 'null'
        if isinstance(o, bool):
            return 'true' if o else 'false'
        if _is_num(o):
            return str(o)
        s = _stringify(o)
        if s is not None:
            return self._escape_string(s)
        return None

    def _escape_string(self, s):
        r = json.dumps(s, ensure_ascii=self._ensure_ascii)
        return u"'{}'".format(r[1:-1].replace("'", r"\'"))

    def _escape_key(self, s):
        if s is None or isinstance(s, bool) or _is_num(s):
            s = str(s)
        s = _stringify(s)
        if s is None:
            if self._skipkeys:
                return None
            raise TypeError('keys must be a string')
        if not _id_re.match(s):
            return self._escape_string(s)
        return s

    def _push_obj(self, o):
        if self._obj_stack is not None:
            if id(o) in self._obj_stack:
                raise ValueError('Circular reference detected')
            self._obj_stack.add(id(o))

    def _pop_obj(self, o):
        if self._obj_stack is not None:
            self._obj_stack.remove(id(o))

    def _encode(self, o, obj_val=False, indent='', force_flow=False):
        if isinstance(o, list):
            if not o:
                if obj_val:
                    yield ' []\n'
                else:
                    yield indent
                    yield '[]\n'
            else:
                if obj_val:
                    yield ' [\n'
                else:
                    yield indent
                    yield '[\n'
                    indent = indent + self._indent
                self._push_obj(o)
                for v in o:
                    for chunk in self._encode(v, obj_val=False, indent=indent, force_flow=True):
                        yield chunk
                self._pop_obj(o)
                yield indent[:-len(self._indent)]
                yield ']\n'
        elif isinstance(o, dict):
            items = [(self._escape_key(k), v) for k, v in o.items()]
            if self._skipkeys:
                items = [(k, v) for k, v in items if k is not None]
            if self._sort_keys:
                items.sort()
            if force_flow or not items:
                if not items:
                    if obj_val:
                        yield ' {}\n'
                    else:
                        yield indent
                        yield '{}\n'
                else:
                    if obj_val:
                        yield ' {\n'
                    else:
                        yield indent
                        yield '{\n'
                        indent = indent + self._indent
                    self._push_obj(o)
                    for k, v in items:
                        yield indent
                        yield k
                        yield ':'
                        for chunk in self._encode(v, obj_val=True, indent=indent + self._indent, force_flow=False):
                            yield chunk
                    self._pop_obj(o)
                    yield indent[:-len(self._indent)]
                    yield '}\n'
            else:
                if obj_val:
                    yield '\n'
                self._push_obj(o)
                for k, v in items:
                    yield indent
                    yield k
                    yield ':'
                    for chunk in self._encode(v, obj_val=True, indent=indent + self._indent, force_flow=False):
                        yield chunk
                self._pop_obj(o)
        else:
            v = self._format_simple_val(o)
            if v is None:
                self._push_obj(o)
                v = self.default(o)
                for chunk in self._encode(v, obj_val=obj_val, indent=indent, force_flow=force_flow):
                    yield chunk
                self._pop_obj(o)
            else:
                if obj_val:
                    yield ' '
                else:
                    yield indent
                yield v
                yield '\n'

    def iterencode(self, o):
        return self._encode(o)

    def encode(self, o):
        return ''.join(self.iterencode(o))

    def default(self, o):
        if self._default is None:
            raise TypeError('Cannot serialize an object of type {}'.format(type(o).__name__))
        return self._default(o)

def dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None,
        indent=None, default=None, sort_keys=False, **kw):
    if indent is None and cls is None:
        return json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
            allow_nan=allow_nan, default=default, sort_keys=sort_keys, separators=(',', ':'))

    if cls is None:
        cls = CSONEncoder
    encoder = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
        allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, default=default, **kw)

    for chunk in encoder.iterencode(obj):
        fp.write(chunk)

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None,
        default=None, sort_keys=False, **kw):
    if indent is None and cls is None:
        return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
            allow_nan=allow_nan, default=default, sort_keys=sort_keys, separators=(',', ':'))

    if cls is None:
        cls = CSONEncoder
    encoder = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
        allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, default=default, **kw)

    return encoder.encode(obj)
