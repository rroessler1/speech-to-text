import difflib
from pprint import pprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def diff(str1, str2):
    d = difflib.Differ()
    result = list(d.compare(str1, str2))
    pprint(result)


def inline_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)
    def process_tag(tag, i1, i2, j1, j2):
        if tag == 'replace':
            return f"<span style=\"color:red\">{matcher.b[j1:j2]}</span>"
            # return '[{}->{}]'.format(matcher.a[i1:i2], matcher.b[j1:j2])
        if tag == 'delete':
            return f"<span style=\"color:orange\">{matcher.a[i1:i2]}</span>"
        if tag == 'equal':
            return matcher.a[i1:i2]
        if tag == 'insert':
            return f"<span style=\"color:red\">{matcher.b[j1:j2]}</span>"
        assert False, "Unknown tag %r"%tag
    return ''.join(process_tag(*t) for t in matcher.get_opcodes())


def show_diff(seqm):
    """Unify operations between two compared strings
seqm is a difflib.SequenceMatcher instance whose a & b are strings"""
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
        elif opcode == 'delete':
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
        elif opcode == 'replace':
            output.append("<rep>" + seqm.b[b0:b1] + "</rep>")
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)
