from speg import peg
import re, sys

if sys.version_info[0] == 2:
    _chr = unichr
else:
    _chr = chr

def load(fin):
    return loads(fin.read())

def loads(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    if s.startswith(u'\ufeff'):
        s = s[1:]
    return peg(s.replace('\r\n', '\n'), _p_root)

def _p_ws(p):
    p('[ \t]*')

def _p_nl(p):
    p(r'([ \t]*(?:#[^\n]*)?\r?\n)+')

def _p_ews(p):
    with p:
        p(_p_nl)
    p(_p_ws)

def _p_id(p):
    return p(r'[$a-zA-Z_][$0-9a-zA-Z_]*')

_escape_table = {
    'r': '\r',
    'n': '\n',
    't': '\t',
    'f': '\f',
    'b': '\b',
}
def _p_unescape(p):
    esc = p('\\\\(?:u[0-9a-fA-F]{4}|[^\n])')
    if esc[1] == 'u':
        return _chr(int(esc[2:], 16))
    return _escape_table.get(esc[1:], esc[1:])

_re_indent = re.compile(r'[ \t]*')
def _p_block_str(p, c):
    p(r'{c}{c}{c}'.format(c=c))
    lines = [['']]
    with p:
        while True:
            s = p(r'(?:{c}(?!{c}{c})|[^{c}\\])*'.format(c=c))
            l = s.split('\n')
            lines[-1].append(l[0])
            lines.extend([x] for x in l[1:])
            if p(r'(?:\\\n[ \t]*)*'):
                continue
            p.commit()
            lines[-1].append(p(_p_unescape))
    p(r'{c}{c}{c}'.format(c=c))

    lines = [''.join(l) for l in lines]
    strip_ws = len(lines) > 1
    if strip_ws and all(c in ' \t' for c in lines[-1]):
        lines.pop()

    indent = None
    for line in lines[1:]:
        if not line:
            continue
        if indent is None:
            indent = _re_indent.match(line).group(0)
            continue
        for i, (c1, c2) in enumerate(zip(indent, line)):
            if c1 != c2:
                indent = indent[:i]
                break

    ind_len = len(indent or '')
    if strip_ws and all(c in ' \t' for c in lines[0]):
        lines = [line[ind_len:] for line in lines[1:]]
    else:
        lines[1:] = [line[ind_len:] for line in lines[1:]]

    return '\n'.join(lines)

_re_mstr_nl = re.compile(r'(?:[ \t]*\n)+[ \t]*')
_re_mstr_trailing_nl = re.compile(_re_mstr_nl.pattern + r'\Z')
def _p_multiline_str(p, c):
    p('{c}(?!{c}{c})(?:[ \t]*\n[ \t]*)?'.format(c=c))
    string_parts = []
    with p:
        while True:
            string_parts.append(p(r'[^{c}\\]*'.format(c=c)))
            if p(r'(?:\\\n[ \t]*)*'):
                string_parts.append('')
                continue
            p.commit()
            string_parts.append(p(_p_unescape))
    p(c)
    string_parts[-1] = _re_mstr_trailing_nl.sub('', string_parts[-1])
    string_parts[::2] = [_re_mstr_nl.sub(' ', part) for part in string_parts[::2]]
    return ''.join(string_parts)

def _p_string(p):
    with p:
        return p(_p_block_str, '"')
    with p:
        return p(_p_block_str, "'")
    with p:
        return p(_p_multiline_str, '"')
    return p(_p_multiline_str, "'")

def _p_array_value(p):
    with p:
        p(_p_nl)
        return p(_p_object)
    with p:
        p(_p_ws)
        return p(_p_line_object)
    p(_p_ews)
    return p(_p_simple_value)

def _p_key(p):
    with p:
        return p(_p_id)
    return p(_p_string)

def _p_flow_kv(p):
    k = p(_p_key)
    p(_p_ews)
    p(':')
    with p:
        p(_p_nl)
        return k, p(_p_object)
    with p:
        p(_p_ws)
        return k, p(_p_line_object)
    p(_p_ews)
    return k, p(_p_simple_value)

def _p_flow_obj_sep(p):
    with p:
        p(_p_ews)
        p(',')
        p(_p_ews)
        return

    p(_p_nl)
    p(_p_ws)

def _p_simple_value(p):
    with p:
        p('null')
        return None

    with p:
        p('false')
        return False
    with p:
        p('true')
        return True

    with p:
        return int(p('0b[01]+')[2:], 2)
    with p:
        return int(p('0o[0-7]+')[2:], 8)
    with p:
        return int(p('0x[0-9a-fA-F]+')[2:], 16)
    with p:
        return float(p(r'-?(?:[1-9][0-9]*|0)?\.[0-9]+(?:e[\+-]?[0-9]+)?|(?:[1-9][0-9]*|0)(?:\.[0-9]+)e[\+-]?[0-9]+'))
    with p:
        return int(p('-?[1-9][0-9]*|0'), 10)

    with p:
        return p(_p_string)

    with p:
        p(r'\[')
        r = []
        with p:
            p.set('I', '')
            r.append(p(_p_array_value))
            with p:
                while True:
                    with p:
                        p(_p_ews)
                        p(',')
                        rr = p(_p_array_value)
                    if not p:
                        p(_p_nl)
                        with p:
                            rr = p(_p_object)
                        if not p:
                            p(_p_ews)
                            rr = p(_p_simple_value)
                    r.append(rr)
                    p.commit()
            with p:
                p(_p_ews)
                p(',')
        p(_p_ews)
        p(r'\]')
        return r

    p(r'\{')

    r = {}
    p(_p_ews)
    with p:
        p.set('I', '')
        k, v = p(_p_flow_kv)
        r[k] = v
        with p:
            while True:
                p(_p_flow_obj_sep)
                k, v = p(_p_flow_kv)
                r[k] = v
                p.commit()
        p(_p_ews)
        with p:
            p(',')
            p(_p_ews)
    p(r'\}')
    return r

def _p_line_kv(p):
    k = p(_p_key)
    p(_p_ws)
    p(':')
    p(_p_ws)
    with p:
        p(_p_nl)
        p(p.get('I'))
        return k, p(_p_indented_object)
    with p:
        return k, p(_p_line_object)
    with p:
        return k, p(_p_simple_value)
    p(_p_nl)
    p(p.get('I'))
    p('[ \t]')
    p(_p_ws)
    return k, p(_p_simple_value)

def _p_line_object(p):
    k, v = p(_p_line_kv)
    r = { k: v }
    with p:
        while True:
            p(_p_ws)
            p(',')
            p(_p_ws)
            k, v = p(_p_line_kv)
            r[k] = v # uniqueness
            p.commit()
    return r

def _p_object(p):
    p.set('I', p.get('I') + p('[ \t]*'))
    r = p(_p_line_object)
    with p:
        while True:
            p(_p_ws)
            with p:
                p(',')
            p(_p_nl)
            p(p.get('I'))
            rr = p(_p_line_object)
            r.update(rr) # unqueness
            p.commit()
    return r

def _p_indented_object(p):
    p.set('I', p.get('I') + p('[ \t]'))
    return p(_p_object)

def _p_root(p):
    with p:
        p(_p_nl)

    with p:
        p.set('I', '')
        r = p(_p_object)
        p(_p_ws)
        with p:
            p(',')

    if not p:
        p(_p_ws)
        r = p(_p_simple_value)

    p(_p_ews)
    p(p.eof)
    return r
