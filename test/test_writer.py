import cson, os, json, pytest

def test_writer():
    srcdir = os.path.join(os.path.split(__file__)[0], 'writer')
    for name in os.listdir(srcdir):
        if not name.endswith('.json'):
            continue

        json_fname = os.path.join(srcdir, name)
        with open(json_fname, 'rb') as fin:
            j = json.loads(fin.read().decode('utf-8'))

        c = cson.dumps(j, indent=4, sort_keys=True, ensure_ascii=False)

        cson_name = name[:-5] + '.cson'
        with open(os.path.join(srcdir, cson_name), 'rb') as fin:
            cc = fin.read().decode('utf-8').replace('\r\n', '\n')

        assert c == cc

        c = cson.loads(c)
        assert c == j

def test_circular():
    with pytest.raises(ValueError):
        o = []
        o.append({'a': o})
        cson.dumps(o, indent=4)

def test_default_terse():
    class X:
        pass

    xx = [1]
    def x_def(x):
        return xx

    c = cson.dumps(X(), default=x_def)
    assert c == '[1]'

def test_default_indent():
    class X:
        pass

    xx = [1]
    def x_def(x):
        return xx

    c = cson.dumps(X(), indent=4, default=x_def)
    assert c == '[\n    1\n]\n'

def test_circular_in_default():
    class X:
        pass

    xx = [1]
    xx.append(xx)
    def x_def(x):
        return xx

    with pytest.raises(ValueError):
        cson.dumps(X(), default=x_def)

def test_circular_in_default_indent():
    class X:
        pass

    xx = [1]
    xx.append(xx)
    def x_def(x):
        return xx

    with pytest.raises(ValueError):
        cson.dumps(X(), indent=4, default=x_def)

def test_nonstring_keys():
    c = cson.dumps({1: 1}, indent=4)
    assert c == "'1': 1\n"

def test_unskipped_keys():
    class X:
        pass

    with pytest.raises(TypeError):
        cson.dumps({X(): 1}, indent=4)

def test_skipkeys():
    class X:
        pass

    c = cson.dumps({X(): 1}, indent=4, skipkeys=True)
    assert c == "{}\n"
