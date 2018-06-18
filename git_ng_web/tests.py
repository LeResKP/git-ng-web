import unittest

from mock import patch
from pyramid import testing

from .git_helper import (
    Git,
    _get_missing_lines,
    _parse_patch,
    parse_hunk_title,
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
        expected = [
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
        ]
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
        expected = [
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
        ]
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
        expected = [
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
            }]
        self.assertEqual(res, expected)

        res = _parse_patch(clean_patch(patch), 8)
        expected = [
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
        ]
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
        expected = [
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
        ]
        self.assertEqual(res, expected)

        res = _parse_patch(clean_patch(patch), 10)
        expected = [
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
        ]
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
        expected = [
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
        ]
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
                    'content': ' This is a new file:',
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
                    'content': ' This is a new file:',
                    'type': 'extra',
                },
                {
                    'a_line_num': 2,
                    'b_line_num': 2,
                    'content': ' ',
                    'type': 'extra'
                },
                {
                    'a_line_num': 3,
                    'b_line_num': 3,
                    'content': ' line 1',
                    'type': 'extra'
                },
                {
                    'a_line_num': 4,
                    'b_line_num': 4,
                    'content': ' line 2',
                    'type': 'extra'
                },
                {
                    'a_line_num': 5,
                    'b_line_num': 5,
                    'content': ' line 3',
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
                    'content': ' line 10',
                    'a_line_num': 9,
                    'type': 'extra',
                    'b_line_num': 10
                },
                {
                    'content': ' line 11',
                    'a_line_num': 10,
                    'type': 'extra',
                    'b_line_num': 11
                },
                {
                    'content': ' line 12',
                    'a_line_num': 11,
                    'type': 'extra',
                    'b_line_num': 12
                },
                {
                    'content': ' line 13',
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
                    'content': '@@ -3,6 +3,7 @@ ',
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
                    'content': ' line 1',
                    'type': 'extra'
                },
                {
                    'a_line_num': 4,
                    'b_line_num': 4,
                    'content': ' line 2',
                    'type': 'extra'
                },
                {
                    'a_line_num': 5,
                    'b_line_num': 5,
                    'content': ' line 3',
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
                    'content': ' This is a new file:',
                    'type': 'extra',
                },
                {
                    'a_line_num': 2,
                    'b_line_num': 2,
                    'content': ' ',
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
                    'content': ' line 10',
                    'a_line_num': 9,
                    'type': 'extra',
                    'b_line_num': 10
                },
                {
                    'content': ' line 11',
                    'a_line_num': 10,
                    'type': 'extra',
                    'b_line_num': 11
                },
                {
                    'content': ' line 12',
                    'a_line_num': 11,
                    'type': 'extra',
                    'b_line_num': 12
                },
                {
                    'a_line_num': None,
                    'b_line_num': None,
                    'content': '',
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
                    'content': ' line 13',
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
                    'content': '@@ -5,4 +6,5 @@ line 2',
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
                    'content': ' line 3',
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
                    'content': ' line 2',
                    'a_line_num': 4,
                    'type':
                    'extra',
                    'b_line_num': 5
                }
            ]
            self.assertEqual(res, expected)
