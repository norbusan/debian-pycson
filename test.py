import sys, os, os.path, json

sys.path.insert(0, os.path.join(os.path.split(__file__)[0], 'cson'))
import cson

total = 0
errors = []

def matches(name):
    return not sys.argv[1:] or name in sys.argv[1:]

srcdir = os.path.join(os.path.split(__file__)[0], 'test', 'parser')
for name in os.listdir(srcdir):
    if not name.endswith('.cson'):
        continue
    if not matches(name):
        continue
    total += 1

    cson_fname = os.path.join(srcdir, name)
    with open(cson_fname, 'rb') as fin:
        try:
            c = cson.load(fin)
        except cson.ParseError as e:
            print('parser/{}({},{}): error: {}'.format(name, e.line, e.col, e.msg))
            errors.append(name)
            continue

    json_name = name[:-5] + '.json'

    with open(os.path.join(srcdir, json_name), 'rb') as fin:
        j = json.loads(fin.read().decode('utf-8'))
    if c != j:
        print('error: {}'.format(name))
        print(repr(c))
        print(repr(j))
        errors.append(name)
        continue
    with open(os.path.join(srcdir, json_name), 'rb') as fin:
        try:
            c = cson.load(fin)
        except cson.ParseError as e:
            print('parser/{}({},{}): error: {}'.format(json_name, e.line, e.col, e.msg))
            errors.append(name)
            continue
    if c != j:
        print('error: {}'.format(name))
        print(repr(c))
        print(repr(j))
        errors.append(name)

srcdir = os.path.join(os.path.split(__file__)[0], 'test', 'writer')
for name in os.listdir(srcdir):
    if not name.endswith('.json'):
        continue
    if not matches(name):
        continue
    total += 1
    json_fname = os.path.join(srcdir, name)
    with open(json_fname, 'rb') as fin:
        j = json.loads(fin.read().decode('utf-8'))

    c = cson.dumps(j, indent=4, sort_keys=True, ensure_ascii=False)

    cson_name = name[:-5] + '.cson'
    with open(os.path.join(srcdir, cson_name), 'rb') as fin:
        cc = fin.read().decode('utf-8').replace('\r\n', '\n')

    if c != cc:
        print('error: {}'.format(name))
        print(repr(c))
        print(repr(cc))
        errors.append(name)
        continue

    try:
        c = cson.loads(c)
    except cson.ParseError as e:
        print('writer/{}({},{}): error: {}'.format(name, e.line, e.col, e.msg))
        errors.append(name)
        continue

    if c != j:
        print('error: {}'.format(name))
        print(repr(c))
        print(repr(j))
        errors.append(name)

try:
    o = []
    o.append({'a': o})
    cson.dumps(o, indent=4)
except ValueError:
    pass
else:
    print('check_circular doesn\'t work')
    errors.append('check_circular')

class X:
    pass

xx = [1]
def x_def(x):
    return xx

c = cson.dumps(X(), default=x_def)
if c != '[1]':
    print('default doesn\'t work')
    print(c)
    errors.append('default')

c = cson.dumps(X(), indent=4, default=x_def)
if c != '[\n    1\n]\n':
    print('default doesn\'t work')
    print(c)
    errors.append('default')

xx.append(xx)
try:
    cson.dumps(xx, default=x_def)
except ValueError:
    pass
else:
    print('check_circular doesn\'t work')
    errors.append('check_circular')

try:
    cson.dumps(xx, indent=4, default=x_def)
except ValueError:
    pass
else:
    print('check_circular doesn\'t work')
    errors.append('check_circular')

c = cson.dumps({1: 1}, indent=4)
if c != "'1': 1\n":
    print('non-string keys')
    print(c)
    errors.append('non-string keys')

c = cson.dumps({X(): 1}, indent=4, skipkeys=True)
if c != "{}\n":
    print('skipkeys')
    print(c)
    errors.append('skipkeys')

try:
    cson.dumps({X(): 1}, indent=4)
except TypeError:
    pass
else:
    print('skipkeys')
    errors.append('skipkeys')

if errors:
    sys.exit(1)

print('succeeded: {}'.format(total))
