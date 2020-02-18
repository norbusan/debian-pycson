import cson, os, json

def test_parser():
    srcdir = os.path.join(os.path.split(__file__)[0], 'parser')
    for name in os.listdir(srcdir):
        if not name.endswith('.cson'):
            continue

        cson_fname = os.path.join(srcdir, name)
        with open(cson_fname, 'rb') as fin:
            c = cson.load(fin)

        json_name = name[:-5] + '.json'
        with open(os.path.join(srcdir, json_name), 'rb') as fin:
            j = json.loads(fin.read().decode('utf-8'))

        assert c == j
        with open(os.path.join(srcdir, json_name), 'rb') as fin:
            c = cson.load(fin)
        assert c == j
