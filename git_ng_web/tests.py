import unittest

from mock import patch
from pyramid import testing

from .git_helper import (
    Git,
    _get_missing_lines,
    _parse_patch,
    parse_hunk_title,
    DIFF_LINE_TYPE_ADDED,
    DIFF_LINE_TYPE_DELETED,
    DIFF_LINE_TYPE_CONTEXT,
)

from .match import (
    transform_lines,
    seq_diff,
)


def clean_patch(patch):
    """In order to have readable patches the lines are indented so we need to
    remove it to have real patch
    """
    lines = []
    for line in patch.lstrip('\n').split('\n'):
        lines.append(line.lstrip())
    return '\n'.join(lines)


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'Git Ng Web')


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from git_ng_web import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Pyramid' in res.body)


class TestGitHelper(unittest.TestCase):

    def test__get_missing_lines(self):
        # @@ -1,6 +1,7 @@
        kw = {
            'b_line_num': 1,
            'prev_b_line_num': 0,
            'file_length': 100,
        }
        res = _get_missing_lines(**kw)
        self.assertEqual(res, [])

        # @@ -2,6 +2,7 @@
        kw = {
            'b_line_num': 2,
            'prev_b_line_num': 0,
            'file_length': 100,
        }
        res = _get_missing_lines(**kw)
        self.assertEqual(res, [1])

        # @@ -2,6 +2,7 @@
        # @@ -11,9 +12,18 @@
        kw = {
            'b_line_num': 12,
            'prev_b_line_num': 8,
            'file_length': 100,
        }
        res = _get_missing_lines(**kw)
        self.assertEqual(res, [9, 10, 11])

        # last part of file
        kw = {
            'b_line_num': 12,
            'prev_b_line_num': None,
            'file_length': 100,
        }
        res = _get_missing_lines(**kw)
        self.assertEqual(res, range(12, 32))

        # last part of file (shorten file)
        kw = {
            'b_line_num': 12,
            'prev_b_line_num': None,
            'file_length': 25,
        }
        res = _get_missing_lines(**kw)
        self.assertEqual(res, range(12, 26))

    def test_parse_patch_add(self):
        patch = '''
            @@ -0,0 +1,8 @@
            +This is a new file:
            +
            +line 1
            +line 2
            +line 3
            +line 4
            +line 5
            +line 6
        '''

        res = _parse_patch(clean_patch(patch), 8)
        expected = [[
            {
                'content': '+This is a new file:',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 1
            },
            {
                'content': '+',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 2
            },
            {
                'content': '+line 1',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 3
            },
            {
                'content': '+line 2',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 4
            },
            {
                'content': '+line 3',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 5
            },
            {
                'content': '+line 4',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 6
            },
            {
                'content': '+line 5',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 7
            },
            {
                'content': '+line 6',
                'a_line_num': None,
                'type': 'added',
                'b_line_num': 8
            }
        ]]
        self.assertEqual(res, expected)

    def test_parse_patch_delete(self):
        patch = '''
            @@ -1,8 +0,0 @@
            -This is a new file:
            -
            -line 1
            -line 2
            -line 3
            -line 4
            -line 5
            -line 6
        '''
        res = _parse_patch(clean_patch(patch), 8)
        expected = [[
            {
                'content': '-This is a new file:',
                'a_line_num': 1,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-',
                'a_line_num': 2,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 1',
                'a_line_num': 3,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 2',
                'a_line_num': 4,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 3',
                'a_line_num': 5,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 4',
                'a_line_num': 6,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 5',
                'a_line_num': 7,
                'type': 'deleted',
                'b_line_num': None
            },
            {
                'content': '-line 6',
                'a_line_num': 8,
                'type': 'deleted',
                'b_line_num': None
            }
        ]]
        self.assertEqual(res, expected)

    def test_parse_patch_first_line(self):
        patch = '''
            @@ -1,3 +1,5 @@
            +Add a new line
            +
             This is a new file:

             line 1
        '''
        res = _parse_patch(clean_patch(patch), 5)
        expected = [[
            {
                'b_line_num': 1,
                'a_line_num': None,
                'content': '+Add a new line',
                'type': 'added'
            },
            {
                'b_line_num': 2,
                'a_line_num': None,
                'content': '+',
                'type': 'added'
            },
            {
                'b_line_num': 3,
                'a_line_num': 1,
                'content': 'This is a new file:',
                'type': 'context'
            },
            {
                'b_line_num': 4,
                'a_line_num': 2,
                'content': '',
                'type': 'context'
            },
            {
                'b_line_num': 5,
                'a_line_num': 3,
                'content': 'line 1',
                'type': 'context'
            }]]
        self.assertEqual(res, expected)

        res = _parse_patch(clean_patch(patch), 8)
        expected = [[
            {
                'b_line_num': 1,
                'a_line_num': None,
                'content': '+Add a new line',
                'type': 'added'
            },
            {
                'b_line_num': 2,
                'a_line_num': None,
                'content': '+',
                'type': 'added'
            },
            {
                'b_line_num': 3,
                'a_line_num': 1,
                'content': 'This is a new file:',
                'type': 'context'
            },
            {
                'b_line_num': 4,
                'a_line_num': 2,
                'content': '',
                'type': 'context'
            },
            {
                'b_line_num': 5,
                'a_line_num': 3,
                'content': 'line 1',
                'type': 'context'
            },
            {
                'b_line_num': None,
                'a_line_num': None,
                'content': '',
                'context_data': {
                    'b_hunk_size': None,
                    'b_line_num': 6,
                    'a_hunk_size': None,
                    'a_line_num': 4,
                    'prev_b_line_num': None},
                'type': 'expand'
            }
        ]]
        self.assertEqual(res, expected)

    def test_parse_patch_middle_line(self):
        patch = '''
            @@ -2,6 +2,7 @@ This is a new file:

             line 1
             line 2
            +this is a new line
             line 3
             line 4
             line 5
        '''
        res = _parse_patch(clean_patch(patch), 7)
        expected = [[
            {
                'b_line_num': None,
                'a_line_num': None,
                'content': '@@ -2,6 +2,7 @@ This is a new file:',
                'context_data': {
                    'b_hunk_size': 7,
                    'b_line_num': 2,
                    'a_hunk_size': 6,
                    'a_line_num': 2,
                    'prev_b_line_num': 0
                },
                'type': 'expand'
            },
            {
                'b_line_num': 2,
                'a_line_num': 2,
                'content': '',
                'type': 'context'
            },
            {
                'b_line_num': 3,
                'a_line_num': 3,
                'content': 'line 1',
                'type': 'context'
            },
            {
                'b_line_num': 4,
                'a_line_num': 4,
                'content': 'line 2',
                'type': 'context'
            },
            {
                'b_line_num': 5,
                'a_line_num': None,
                'content': '+this is a new line',
                'type': 'added'
            },
            {
                'b_line_num': 6,
                'a_line_num': 5,
                'content': 'line 3',
                'type': 'context'
            },
            {
                'b_line_num': 7,
                'a_line_num': 6,
                'content': 'line 4',
                'type': 'context'
            },
            {
                'b_line_num': 8,
                'a_line_num': 7,
                'content': 'line 5',
                'type': 'context'
            }
        ]]
        self.assertEqual(res, expected)

        res = _parse_patch(clean_patch(patch), 10)
        expected = [[
            {
                'b_line_num': None,
                'a_line_num': None,
                'content': '@@ -2,6 +2,7 @@ This is a new file:',
                'context_data': {
                    'b_hunk_size': 7,
                    'b_line_num': 2,
                    'a_hunk_size': 6,
                    'a_line_num': 2,
                    'prev_b_line_num': 0
                },
                'type': 'expand'
            },
            {
                'b_line_num': 2,
                'a_line_num': 2,
                'content': '',
                'type': 'context'
            },
            {
                'b_line_num': 3,
                'a_line_num': 3,
                'content': 'line 1',
                'type': 'context'
            },
            {
                'b_line_num': 4,
                'a_line_num': 4,
                'content': 'line 2',
                'type': 'context'
            },
            {
                'b_line_num': 5,
                'a_line_num': None,
                'content': '+this is a new line',
                'type': 'added'
            },
            {
                'b_line_num': 6,
                'a_line_num': 5,
                'content': 'line 3',
                'type': 'context'
            },
            {
                'b_line_num': 7,
                'a_line_num': 6,
                'content': 'line 4',
                'type': 'context'
            },
            {
                'b_line_num': 8,
                'a_line_num': 7,
                'content': 'line 5',
                'type': 'context'
            },
            {
                'b_line_num': None,
                'a_line_num': None,
                'content': '',
                'context_data': {
                    'b_hunk_size': None,
                    'b_line_num': 9,
                    'a_hunk_size': None,
                    'a_line_num': 8,
                    'prev_b_line_num': None},
                'type': 'expand'
            }
        ]]
        self.assertEqual(res, expected)

    def test_parse_patch_last_line(self):
        patch = '''
            @@ -6,3 +6,4 @@ line 3
             line 4
             line 5
             line 6
            +this is a new line
        '''
        res = _parse_patch(clean_patch(patch), 4)
        expected = [[
            {
                'b_line_num': None,
                'a_line_num': None,
                'content': '@@ -6,3 +6,4 @@ line 3',
                'context_data': {
                    'b_hunk_size': 4,
                    'b_line_num': 6,
                    'a_hunk_size': 3,
                    'a_line_num': 6,
                    'prev_b_line_num': 0
                },
                'type': 'expand'
            },
            {
                'b_line_num': 6,
                'a_line_num': 6,
                'content': 'line 4',
                'type': 'context'
            },
            {
                'b_line_num': 7,
                'a_line_num': 7,
                'content': 'line 5',
                'type': 'context'
            },
            {
                'b_line_num': 8,
                'a_line_num': 8,
                'content': 'line 6',
                'type': 'context'
            },
            {
                'b_line_num': 9,
                'a_line_num': None,
                'content': '+this is a new line',
                'type': 'added'
            }
        ]]
        self.assertEqual(res, expected)

    def test_get_diff_context_middle_line(self):
        '''
            @@ -2,6 +2,7 @@ This is a new file:

             line 1
             line 2
            +this is a new line
             line 3
             line 4
             line 5
        '''

        file_contents = {
            1: 'This is a new file:',
            2: '',
            3: 'line 1',
            4: 'line 2',
            5: 'this is a new line',
            6: 'line 3',
            7: 'line 4',
            8: 'line 5',
        }

        filename = 'test.py'
        h = 'hash'

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            data = parse_hunk_title('@@ -2,6 +2,7 @@ This is a new file:')
            res = Git('.').get_diff_context(filename, h,
                                            prev_b_line_num=0, **data)
            expected = [
                {
                    'content': [(0, ' This is a new file:')],
                    'a_line_num': 1,
                    'type': 'extra',
                    'b_line_num': 1
                }
            ]
            self.assertEqual(res, expected)

    def test_get_diff_context_last_line(self):
        '''
            @@ -6,3 +6,4 @@ line 3
             line 4
             line 5
             line 6
            +this is a new line
        '''
        file_contents = {
            1: 'This is a new file:',
            2: '',
            3: 'line 1',
            4: 'line 2',
            5: 'line 3',
            6: 'line 4',
            7: 'line 5',
            8: 'line 6',
            9: 'this is a new line',
        }

        filename = 'test.py'
        h = 'hash'

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            data = parse_hunk_title('@@ -6,3 +6,4 @@ line 3')
            res = Git('.').get_diff_context(filename, h,
                                            prev_b_line_num=0, **data)
            expected = [
                {
                    'a_line_num': 1,
                    'b_line_num': 1,
                    'content': [(0, ' This is a new file:')],
                    'type': 'extra',
                },
                {
                    'a_line_num': 2,
                    'b_line_num': 2,
                    'content': [(0, ' ')],
                    'type': 'extra'
                },
                {
                    'a_line_num': 3,
                    'b_line_num': 3,
                    'content': [(0, ' line 1')],
                    'type': 'extra'
                },
                {
                    'a_line_num': 4,
                    'b_line_num': 4,
                    'content': [(0, ' line 2')],
                    'type': 'extra'
                },
                {
                    'a_line_num': 5,
                    'b_line_num': 5,
                    'content': [(0, ' line 3')],
                    'type': 'extra'
                }
            ]
            self.assertEqual(res, expected)

        # Add more ending line
        file_contents.update({
            10: 'line 10',
            11: 'line 11',
            12: 'line 12',
            13: 'line 13',
        })

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            data = parse_hunk_title('@@ -6,3 +6,4 @@ line 3')
            data['a_line_num'] += data['a_hunk_size']
            data['a_hunk_size'] = None
            data['b_line_num'] += data['b_hunk_size']
            data['b_hunk_size'] = None
            res = Git('.').get_diff_context(filename, h,
                                            prev_b_line_num=None, **data)
            expected = [
                {
                    'content': [(0, ' line 10')],
                    'a_line_num': 9,
                    'type': 'extra',
                    'b_line_num': 10
                },
                {
                    'content': [(0, ' line 11')],
                    'a_line_num': 10,
                    'type': 'extra',
                    'b_line_num': 11
                },
                {
                    'content': [(0, ' line 12')],
                    'a_line_num': 11,
                    'type': 'extra',
                    'b_line_num': 12
                },
                {
                    'content': [(0, ' line 13')],
                    'a_line_num': 12,
                    'type': 'extra',
                    'b_line_num': 13
                }
            ]
            self.assertEqual(res, expected)

    @patch('git_ng_web.git_helper.DIFF_CONTEXT_LINE', 3)
    def test_get_diff_context_last_line_context_lines(self):
        '''
            @@ -6,3 +6,4 @@ line 3
             line 4
             line 5
             line 6
            +this is a new line
        '''
        file_contents = {
            1: 'This is a new file:',
            2: '',
            3: 'line 1',
            4: 'line 2',
            5: 'line 3',
            6: 'line 4',
            7: 'line 5',
            8: 'line 6',
            9: 'this is a new line',
        }

        filename = 'test.py'
        h = 'hash'

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            data = parse_hunk_title('@@ -6,3 +6,4 @@ line 3')
            res = Git('.').get_diff_context(filename, h,
                                            prev_b_line_num=0, **data)
            expected = [
                {
                    'a_line_num': None,
                    'b_line_num': None,
                    'content': [(0, '@@ -3,6 +3,7 @@ ')],
                    'context_data': {
                        'a_hunk_size': 6,
                        'a_line_num': 3,
                        'b_hunk_size': 7,
                        'b_line_num': 3,
                        'prev_b_line_num': 0
                    },
                    'type': 'expand'
                },
                {
                    'a_line_num': 3,
                    'b_line_num': 3,
                    'content': [(0, ' line 1')],
                    'type': 'extra'
                },
                {
                    'a_line_num': 4,
                    'b_line_num': 4,
                    'content': [(0, ' line 2')],
                    'type': 'extra'
                },
                {
                    'a_line_num': 5,
                    'b_line_num': 5,
                    'content': [(0, ' line 3')],
                    'type': 'extra'
                }
            ]
            self.assertEqual(res, expected)

            res = Git('.').get_diff_context(filename, h,
                                            **expected[0]['context_data'])

            expected = [
                {
                    'a_line_num': 1,
                    'b_line_num': 1,
                    'content': [(0, ' This is a new file:')],
                    'type': 'extra',
                },
                {
                    'a_line_num': 2,
                    'b_line_num': 2,
                    'content': [(0, ' ')],
                    'type': 'extra'
                },
            ]
            self.assertEqual(res, expected)

        # Add more ending line
        file_contents.update({
            10: 'line 10',
            11: 'line 11',
            12: 'line 12',
            13: 'line 13',
        })

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            data = parse_hunk_title('@@ -6,3 +6,4 @@ line 3')
            data['a_line_num'] += data['a_hunk_size']
            data['a_hunk_size'] = None
            data['b_line_num'] += data['b_hunk_size']
            data['b_hunk_size'] = None
            res = Git('.').get_diff_context(filename, h,
                                            prev_b_line_num=None, **data)
            expected = [
                {
                    'content': [(0, ' line 10')],
                    'a_line_num': 9,
                    'type': 'extra',
                    'b_line_num': 10
                },
                {
                    'content': [(0, ' line 11')],
                    'a_line_num': 10,
                    'type': 'extra',
                    'b_line_num': 11
                },
                {
                    'content': [(0, ' line 12')],
                    'a_line_num': 11,
                    'type': 'extra',
                    'b_line_num': 12
                },
                {
                    'a_line_num': None,
                    'b_line_num': None,
                    'content': [],
                    'context_data': {
                        'a_hunk_size': None,
                        'a_line_num': 12,
                        'b_hunk_size': None,
                        'b_line_num': 13,
                        'prev_b_line_num': None
                    },
                    'type': 'expand'
                }
            ]
            self.assertEqual(res, expected)

            res = Git('.').get_diff_context(filename, h,
                                            **expected[-1]['context_data'])
            expected = [
                {
                    'content': [(0, ' line 13')],
                    'a_line_num': 12,
                    'type': 'extra',
                    'b_line_num': 13
                }
            ]
            self.assertEqual(res, expected)

    @patch('git_ng_web.git_helper.DIFF_CONTEXT_LINE', 1)
    def test_get_diff_context_2_hunks(self):
        """
            @@ -1,3 +1,4 @@
            +First line
             This is a new file:

             line 1
            @@ -6,3 +7,4 @@ line 3
             line 4
             line 5
             line 6
            +Last line
        """
        file_contents = {
            1: 'First line',
            2: 'This is a new file:',
            3: '',
            4: 'line 1',
            5: 'line 2',
            6: 'line 3',
            7: 'line 4',
            8: 'line 5',
            9: 'line 6',
            10: 'Last line',
            11: 'line 11',
            12: 'line 12',
            13: 'line 13',
            14: 'line 14',
        }

        filename = 'test.py'
        h = 'hash'

        with patch('git_ng_web.git_helper.Git._get_file_content_by_lines',
                   return_value=file_contents):

            prev_data = parse_hunk_title('@@ -1,3 +1,4 @@')
            data = parse_hunk_title('@@ -6,3 +7,4 @@ line 3')
            prev_b_line_num = (
                prev_data['b_line_num'] +
                prev_data['b_hunk_size'] - 1
            )
            res = Git('.').get_diff_context(
                filename, h, prev_b_line_num=prev_b_line_num, **data)
            expected = [
                {
                    'content': [(0, '@@ -5,4 +6,5 @@ line 2')],
                    'a_line_num': None,
                    'type': 'expand',
                    'context_data': {
                        'b_hunk_size': 5,
                        'a_line_num': 5,
                        'a_hunk_size': 4,
                        'b_line_num': 6,
                        'prev_b_line_num': 4
                    },
                    'b_line_num': None
                },
                {
                    'content': [(0, ' line 3')],
                    'a_line_num': 5,
                    'type': 'extra',
                    'b_line_num': 6
                }
            ]
            self.assertEqual(res, expected)

            res = Git('.').get_diff_context(
                filename, h, **expected[0]['context_data'])
            expected = [
                {
                    'content': [(0, ' line 2')],
                    'a_line_num': 4,
                    'type':
                    'extra',
                    'b_line_num': 5
                }
            ]
            self.assertEqual(res, expected)


class MatchTest(unittest.TestCase):

    def test_seq(self):

        def _check(a_line, b_line, expected):
            res = seq_diff(a_line, b_line)
            self.assertEqual(res, expected)

            r_a = ''.join(s for t, s in res if t in [0, -1])
            self.assertEqual(a_line, r_a)

            r_b = ''.join(s for t, s in res if t in [0, 1])
            self.assertEqual(b_line, r_b)

        a_line = 'Hello man!'
        b_line = 'Hello world!'
        expected = [(0, 'Hello '), (-1, 'man'), (1, 'world'), (0, '!')]
        _check(a_line, b_line, expected)

        a_line = 'a_b'
        b_line = 'a_c'
        expected = [(0, 'a_'), (-1, 'b'), (1, 'c')]
        _check(a_line, b_line, expected)

        a_line = 'b_a'
        b_line = 'c_a'
        expected = [(-1, 'b'), (1, 'c'), (0, '_a')]
        _check(a_line, b_line, expected)

        a_line = 'aB'
        b_line = 'aC'
        expected = [(0, 'a'), (-1, 'B'), (1, 'C')]
        _check(a_line, b_line, expected)

        a_line = '            this.projectId, this.hash);'
        b_line = (
            '            this.projectId, this.hash, '
            'this.ignoreAllSpace, this.context);')
        expected = [
            (0, '            this.projectId, this.hash'),
            (1, ', this.ignoreAllSpace, this.context'),
            (0, ');')
        ]
        _check(a_line, b_line, expected)

        a_line = '  getDiff(projectId, hash) {'
        b_line = '  getDiff(projectId, hash, ignoreAllSpace, unified) {'
        expected = [
            (0, '  getDiff(projectId, hash'),
            (1, ', ignoreAllSpace, unified'),
            (0, ') {')
        ]
        _check(a_line, b_line, expected)

        a_line = '    return this.http.get(url);'
        b_line = '    return this.http.post(other_url);'
        expected = [
            (0, '    return this.http.'),
            (-1, 'get('),
            (1, 'post('),
            (1, 'other_'),
            (0, 'url);')
        ]
        _check(a_line, b_line, expected)

        a_line = '    return this.http.get(url);'
        b_line = '    return this.http.getUrl(url);'
        expected = [
            (0, '    return this.http.get'),
            (1, 'Url'),
            (0, '(url);')
        ]
        _check(a_line, b_line, expected)

        a_line = 'Hello world'
        b_line = 'Hallo xosle'
        expected = [
            (-1, 'Hello '), (1, 'Hallo '),
            (-1, 'world'), (1, 'xosle'),
        ]
        _check(a_line, b_line, expected)

        a_line = 'This is a long sentence'
        b_line = 'There is a cat in the kitchen'
        expected = [
            (-1, 'This'),
            (1, 'There'),
            (0, ' is a '),
            (-1, 'long'),
            (1, 'cat in'),
            (0, ' '),
            (-1, 'sentence'),
            (1, 'the kitchen')
        ]
        _check(a_line, b_line, expected)

        a_line = 'This is a camel'
        b_line = 'There is a camelCase'
        expected = [
            (-1, 'This'),
            (1, 'There'),
            (0, ' is a camel'),
            (1, 'Case')
        ]
        _check(a_line, b_line, expected)

        a_line = 'This is a line'
        b_line = '     This is a line indented'
        expected = [
            (1, '     '),
            (0, 'This is a line'),
            (1, ' indented')
        ]
        _check(a_line, b_line, expected)

        a_line = 'expected = ['
        b_line = 'expected = [['
        expected = [
            (0, 'expected = ['),
            (1, '[')
        ]
        _check(a_line, b_line, expected)

        a_line = "dic['key']"
        b_line = "dic['new']"
        expected = [
            (0, "dic['"),
            (-1, 'key'),
            (1, 'new'),
            (0, "']"),

        ]
        _check(a_line, b_line, expected)

    def test_transform_lines(self):
        group = [
            {
                'type': DIFF_LINE_TYPE_CONTEXT,
                'content': ' Context before',
            },
            {
                'type': DIFF_LINE_TYPE_DELETED,
                'content': '- Hello world',
            },
            {
                'type': DIFF_LINE_TYPE_ADDED,
                'content': '+ Hello',
            },
            {
                'type': DIFF_LINE_TYPE_CONTEXT,
                'content': ' Context after',
            },
        ]

        expected = [
            {
                'type': DIFF_LINE_TYPE_CONTEXT,
                'content': [(0, ' Context before')],
            },
            {
                'type': DIFF_LINE_TYPE_DELETED,
                'content': [(0, '-'), (0, ' Hello'), (-1, ' world')],
            },
            {
                'type': DIFF_LINE_TYPE_ADDED,
                'content': [(0, '+'), (0, ' Hello')],
            },
            {
                'type': DIFF_LINE_TYPE_CONTEXT,
                'content': [(0, ' Context after')],
            },
        ]
        transform_lines(group)
        self.assertEqual(group, expected)
