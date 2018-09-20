from collections import defaultdict
import diff_match_patch as dmp_module


# These constant values are used in angular
DIFF_LINE_TYPE_ADDED = 'added'
DIFF_LINE_TYPE_DELETED = 'deleted'
DIFF_LINE_TYPE_CONTEXT = 'context'
DIFF_LINE_TYPE_EXTRA_CONTEXT = 'extra'
DIFF_LINE_TYPE_EXPAND = 'expand'


SCORE_CACHE = {}


def get_line(line):
    return line['content'][1:]


def should_apply_diff(diff):
    part_types = [p[0] for p in diff]
    non_context = [p[0] for p in diff if p[0] != 0]
    len_by_type = defaultdict(int)

    for p in diff:
        len_by_type[p[0]] += len(p[1])

    if len(set(non_context)) == 1:
        return True

    if len(set(part_types)) == 3:
        ctx = len_by_type.get(0)
        if not ctx:
            return False

        if float(ctx) / sum(len_by_type.values()) > 0.25:
            return True

    return False


def transform_lines(group):
    dmp = dmp_module.diff_match_patch()
    previous = None
    for line in group:
        if (previous and previous['type'] == DIFF_LINE_TYPE_DELETED and
                line['type'] == DIFF_LINE_TYPE_ADDED):
            a_line = get_line(previous)
            b_line = get_line(line)
            if a_line and b_line:
                diff = dmp.diff_main(a_line, b_line)
                dmp.diff_cleanupSemantic(diff)
                if should_apply_diff(diff):
                    previous['content'] = [(0, '-')] + [d for d in diff if d[0] in (0, -1)]
                    line['content'] = [(0, '+')] + [d for d in diff if d[0] in (0, 1)]

        previous = line

    # All the lines should be a list
    for line in group:
        if not isinstance(line['content'], list):
            line['content'] = [(0, line['content'])]
