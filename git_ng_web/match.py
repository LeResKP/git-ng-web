from collections import defaultdict
from difflib import SequenceMatcher
import string


# These constant values are used in angular
DIFF_LINE_TYPE_ADDED = 'added'
DIFF_LINE_TYPE_DELETED = 'deleted'
DIFF_LINE_TYPE_CONTEXT = 'context'
DIFF_LINE_TYPE_EXTRA_CONTEXT = 'extra'
DIFF_LINE_TYPE_EXPAND = 'expand'


DEL = -1
CTX = 0
ADD = 1
SEPARATORS = [' ', '!', '(', ')', '_', ',', '.', '[', ']', "'", '"']


def _remove_punctuation(s):
    for p in string.punctuation:
        s = s.replace(p, '')
    return s


def _has_context(lis):
    for t, s in lis:
        if t == CTX:
            n = _remove_punctuation(s)
            if n and n.strip():
                print 'OK'
                return True
    return False


def apply_diff(lis):
    return _has_context(lis)


def get_line(line):
    return line['content'][1:]


def transform_lines(group):
    previous = None
    for line in group:
        if (previous and previous['type'] == DIFF_LINE_TYPE_DELETED and
                line['type'] == DIFF_LINE_TYPE_ADDED):
            a_line = get_line(previous)
            b_line = get_line(line)
            if a_line and b_line:
                diff = seq_diff(a_line, b_line)
                if apply_diff(diff):
                    previous['content'] = [(0, '-')] + [
                        d for d in diff if d[0] in (CTX, DEL)]
                    line['content'] = [(0, '+')] + [
                        d for d in diff if d[0] in (CTX, ADD)]

        previous = line

    # All the lines should be a list
    for line in group:
        if not isinstance(line['content'], list):
            line['content'] = [(0, line['content'])]


def get_separator_positions(s):
    case = None
    lis = [len(s)]
    for index, c in enumerate(s):
        if c in SEPARATORS:
            lis.append(index)
            case = None
        else:
            # TODO: rewrite this logic
            if c in string.lowercase:
                if case == 'upper':
                    case = None
                else:
                    case = 'lower'
            elif c in string.uppercase:
                if case == 'lower':
                    lis.append(index)
                    case = None
                else:
                    case = 'upper'
    return lis


def seq_diff(a, b):
    s = SequenceMatcher(None, a, b)

    a_spaces = get_separator_positions(a)
    b_spaces = get_separator_positions(b)
    lis = []
    s_a = ''
    s_b = ''

    def add(s_a, s_b):
        if s_a == s_b and s_a and s_b:
            lis.append((CTX, s_a))
            return '', ''

        if s_a:
            lis.append((DEL, s_a))

        if s_b:
            lis.append((ADD, s_b))
        return '', ''

    def ready(pos, s_x, spaces):
        return pos in spaces or s_x[-1] in SEPARATORS

    for tag, a1, a2, b1, b2 in s.get_opcodes():
        s_a += a[a1:a2]
        s_b += b[b1:b2]

        if not s_a and s_b:
            if ready(b2, s_b, b_spaces):
                s_a, s_b = add(s_a, s_b)

        elif s_a and not s_b:
            if ready(a2, s_a, a_spaces):
                s_a, s_b = add(s_a, s_b)

        else:
            if ready(a2, s_a, a_spaces) and ready(b2, s_b, b_spaces):
                s_a, s_b = add(s_a, s_b)

    add(s_a, s_b)
    return lis
