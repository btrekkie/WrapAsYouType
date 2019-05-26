from sublime import Region

from WrapAsYouType.tests.command_test_base import WrapAsYouTypeCommandTestBase


class TestWrapAsYouTypeSettings(WrapAsYouTypeCommandTestBase):
    """Test the "wrap_as_you_type_*" settings."""

    def test_word_regex(self):
        """Test the "wrap_as_you_type_word_regex" setting."""
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('rulers', [60])

        # Allow breaks at hyphens, and disallow breaks between braces
        settings.set(
            'wrap_as_you_type_word_regex',
            r'[^\s\-\{]+-*|-+[^\s\-\{]*-*|\{[^\}]*\}?')
        settings.set(
            'wrap_as_you_type_space_between_words', [{
                'first_word_regex': r'[^\-]-+$',
                'space': '',
            }])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The function assumes that n >= 0.\n'
            ' */\n'
            'int fibonacci(int n) {\n'
            '    // Base case\n'
            '    if (n == 0) {\n'
            '        return 0;\n'
            '    }\n'
            '\n'
            '    // Iterative implementation of "fibonacci"\n'
            '    int cur = 1;\n'
            '    int prev = 0;\n'
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n'
            '    return cur;\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    cout << "The 8th Fibonacci number is " <<\n'
            '        fibonacci(8) << "\\n";\n'
            '    return 0;\n'
            '}\n')

        comment_start_point = view.find(r'/\*\*', 0).begin()
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._insert(
            point,
            ' The well-known nitty-gritty in non-object-oriented '
            'Fibonacci-centric implementation is that there are two ways of '
            'implementing it: {a slow, recursive implementation} and {a fast, '
            'iterative implementation.}')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The well-known nitty-gritty in non-\n'
            ' * object-oriented Fibonacci-centric implementation is that\n'
            ' * there are two ways of implementing it:\n'
            ' * {a slow, recursive implementation} and\n'
            ' * {a fast, iterative implementation.} The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('The "fibonacci" function', 0).begin()
        self._delete(point, 75)
        expected_text = (
            '/**\n'
            ' * The well-known nitty-gritty in non-object-oriented\n'
            ' * Fibonacci-centric implementation is that there are two\n'
            ' * ways of implementing it:\n'
            ' * {a slow, recursive implementation} and\n'
            ' * {a fast, iterative implementation.} The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_space_between_words(self):
        """Test the "wrap_as_you_type_space_between_words" setting."""
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('rulers', [60])

        settings.set(
            'wrap_as_you_type_space_between_words', [
                {
                    'first_word_regex': r'^(e\.g\.|i\.e\.)$',
                    'space': ' '
                },
                {
                    'first_word_regex': '[.?!]$',
                    'space': '  '
                },
                {
                    'first_word_regex': r'^Fibonacci$',
                    'second_word_regex': r'^sequence\.?$',
                    'space': '\t  '
                }
            ])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci\t  sequence.\n'
            ' */\n'
            'int fibonacci(int n) {\n'
            '    // Base case\n'
            '    if (n == 0) {\n'
            '        return 0;\n'
            '    }\n'
            '\n'
            '    // Iterative implementation of "fibonacci"\n'
            '    int cur = 1;\n'
            '    int prev = 0;\n'
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n'
            '    return cur;\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    cout << "The 8th Fibonacci number is " <<\n'
            '        fibonacci(8) << "\\n";\n'
            '    return 0;\n'
            '}\n')

        comment_start_point = view.find(r'/\*\*', 0).begin()
        point = view.find(r'Fibonacci\t  sequence\.', 0).end()
        self._insert(
            point,
            '  The Fibonacci\t  sequence begins with 0 as the 0th number and '
            '1 as the first number.  Every subsequent number is equal to the '
            'sum of the two previous numbers, e.g. the second term is 0 + 1 = '
            '1.  The function assumes that n >= 0.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci\t  sequence.  The Fibonacci\t  sequence\n'
            ' * begins with 0 as the 0th number and 1 as the first\n'
            ' * number.  Every subsequent number is equal to the sum of\n'
            ' * the two previous numbers, e.g. the second term is 0 + 1 =\n'
            ' * 1.  The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('The "fibonacci" function', 0).begin()
        self._delete(point, 78)
        expected_text = (
            '/**\n'
            ' * The Fibonacci\t  sequence begins with 0 as the 0th\n'
            ' * number and 1 as the first number.  Every subsequent\n'
            ' * number is equal to the sum of the two previous numbers,\n'
            ' * e.g. the second term is 0 + 1 = 1.  The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Break up "Fibonacci sequence"
        point = view.find(r'The Fibonacci\t  sequence', 0).begin()
        self._insert(point, '.  ')
        self._insert(point, 'Returns the nth Fibonacci number')
        expected_text = (
            '/**\n'
            ' * Returns the nth Fibonacci number.  The Fibonacci\n'
            ' * sequence begins with 0 as the 0th number and 1 as the\n'
            ' * first number.  Every subsequent number is equal to the\n'
            ' * sum of the two previous numbers, e.g. the second term is\n'
            ' * 0 + 1 = 1.  The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Make sure "Fibonacci number" does not receive the spacing reserved
        # for "Fibonacci sequence"
        point = view.find('Returns the nth', 0).begin()
        self._insert(point, '.  ')
        self._insert(
            point,
            '"fibonacci" is a function that takes an integer as an argument '
            'and returns an integer result')
        expected_text = (
            '/**\n'
            ' * "fibonacci" is a function that takes an integer as an\n'
            ' * argument and returns an integer result.  Returns the nth\n'
            ' * Fibonacci number.  The Fibonacci\t  sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number.  Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers, e.g. the second term is 0 + 1 = 1.  The function\n'
            ' * assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_paragraphs(self):
        """Test the "wrap_as_you_type_paragraphs" setting."""
        view = self._view
        view.set_syntax_file('Packages/Java/Java.tmLanguage')
        settings = self._view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'line_start': ' * ',
                    'selector':
                        'comment.block - '
                        '(punctuation.definition.comment.begin | '
                        'punctuation.definition.comment.end)',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '//',
                    'selector': 'comment.line',
                },
            ])
        settings.set(
            'wrap_as_you_type_paragraphs', [
                {
                    'first_line_regex':
                        r'^(?P<indent>@([a-zA-Z]+(\s+|$)|$))',
                    'indent_group': 'indent',
                },
                {
                    'first_line_regex':
                        r'^(\w+\s-(\s|$)|(?P<indent>Does not exist$))',
                    'indent': '    ',
                    'indent_group': 'indent',
                },
                {
                    'first_line_regex': r'^>>>( |$)',
                    'single_line': True,
                },
            ])
        settings.set('rulers', [60])

        self._append(
            'package com.example.fibonacci;\n'
            '\n'
            'class Fibonacci {\n'
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     */\n'
            '    public static int fibonacci(int n) {\n'
            '        // Base case\n'
            '        if (n == 0) {\n'
            '            return 0;\n'
            '        }\n'
            '\n'
            '        // Iterative implementation of "fibonacci"\n'
            '        int cur = 1;\n'
            '        int prev = 0;\n'
            '        for (int i = 1; i < n; i++) {\n'
            '            int next = cur + prev;\n'
            '            prev = cur;\n'
            '            cur = next;\n'
            '        }\n'
            '        return cur;\n'
            '    }\n'
            '\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println(\n'
            '            "The 8th Fibonacci number is " + fibonacci(8) +\n'
            '            "\\n");\n'
            '    }\n'
            '}\n')

        # Test "indent_group" entry
        comment_start_point = view.find(r'/\*\*', 0).begin() - 4
        point = view.find(r'>= 0\.', 0).end()
        self._insert(
            point,
            '\n* @param n The index of the number in the Fibonacci sequence '
            'to compute.')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     * @param n The index of the number in the Fibonacci\n'
            '     *        sequence to compute.\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        settings.set(
            'wrap_as_you_type_paragraphs', [
                {
                    'first_line_regex':
                        r'^@([a-zA-Z]+(\s+|$)|[a-zA-Z]*$)',
                    'indent_group': 0,
                },
                {
                    'first_line_regex':
                        r'^(\w+\s-(\s|$)|(?P<indent>Does not exist$))',
                    'indent': '    ',
                    'indent_group': 'indent',
                },
                {
                    'first_line_regex': r'^>>>( |$)',
                    'single_line': True,
                },
            ])
        point = view.find(r'sequence to compute\.', 0).end()
        self._insert(
            point,
            '\n* @return\t \t The nth Fibonacci number.  This method returns '
            '0 if n is 0.\n* @author jsmith')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     * @param n The index of the number in the Fibonacci\n'
            '     *        sequence to compute.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'sequence to compute\.', 0).end()
        self._insert(
            point,
            ' A value of 0 indicates the 0th number, 0, a value of 1 '
            'indicates the first number, 1, and so on.')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     * @param n The index of the number in the Fibonacci\n'
            '     *        sequence to compute. A value of 0 indicates\n'
            '     *        the 0th number, 0, a value of 1 indicates the\n'
            '     *        first number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('index of', 0).begin()
        self._delete(point, 13)
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test "indent" entry
        point = view.find(r'>= 0\.', 0).end()
        self._insert(
            point,
            '\n*\n* Fibonacci - the person who invented the Fibonacci '
            'sequence.')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     *\n'
            '     * Fibonacci - the person who invented the Fibonacci\n'
            '     *     sequence.\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        settings.set(
            'wrap_as_you_type_paragraphs', [
                {
                    'first_line_regex':
                        r'^@([a-zA-Z]+(\s+|$)|[a-zA-Z]*$)',
                    'indent_group': 0,
                },
                {
                    'first_line_regex':
                        r'^(\w+\s-(\s|$)|(?P<indent>Does not exist$))',
                    'indent': '    ',
                    'indent_group': 3,
                },
                {
                    'first_line_regex': r'^>>>( |$)',
                    'single_line': True,
                },
            ])
        point = view.find(r'     sequence\.', 0).end()
        self._insert(
            point,
            '\n* Method - a series of programming instructions situated in an '
            'enclosing class.')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     *\n'
            '     * Fibonacci - the person who invented the Fibonacci\n'
            '     *     sequence.\n'
            '     * Method - a series of programming instructions\n'
            '     *     situated in an enclosing class.\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test "indent_levels"
        settings.set(
            'wrap_as_you_type_paragraphs', [
                {
                    'first_line_regex':
                        r'^@([a-zA-Z]+(\s+|$)|[a-zA-Z]*$)',
                    'indent_group': 0,
                },
                {
                    'first_line_regex':
                        r'^(\w+\s-(\s|$)|(?P<indent>Does not exist$))',
                    'indent_group': 3,
                    'indent_levels': 3,
                },
                {
                    'first_line_regex': r'^>>>( |$)',
                    'single_line': True,
                },
            ])
        settings.set('tab_size', 2)
        start_point = view.find('Fibonacci -', 0).begin()
        end_point = view.find(r'enclosing class\.', 0).end()
        self._set_selection_region(Region(start_point, end_point))
        view.run_command('left_delete')
        self._insert(
            start_point,
            'Fibonacci - the person who invented the Fibonacci sequence.')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     *\n'
            '     * Fibonacci - the person who invented the Fibonacci\n'
            '     *       sequence.\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test a "single_line" value of true
        point = view.find(r'      sequence\.', 0).end()
        self._insert(
            point,
            '\n*\n'
            '*\n'
            '* >>> Fibonacci.fibonacci(8);\n'
            '*')
        self._insert(point + 14, ' Example:')
        point = view.find(r'fibonacci\(8\);', 0).end() + 7
        self._insert(point, ' 21')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     *\n'
            '     * Fibonacci - the person who invented the Fibonacci\n'
            '     *       sequence.\n'
            '     *\n'
            '     * Example:\n'
            '     * >>> Fibonacci.fibonacci(8);\n'
            '     * 21\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test a single-line paragraph that extends beyond the wrap width
        start_point = view.find(r'Fibonacci\.fibonacci\(8\);', 0).begin()
        end_point = view.find(r'Fibonacci\.fibonacci\(8\);', 0).end()
        self._backspace(Region(start_point, end_point))
        self._insert(
            start_point,
            'Fibonacci.fibonacci(3) + " " + Fibonacci.fibonacci(4) + " " + '
            'Fibonacci.fibonacci(5);')
        point = view.find(r'\* 21', 0).begin() + 2
        self._delete(point, 2)
        self._insert(point, '2 3 5')
        expected_text = (
            '    /**\n'
            '     * The "fibonacci" method returns the nth number in the\n'
            '     * Fibonacci sequence. The method assumes that n >= 0.\n'
            '     *\n'
            '     * Fibonacci - the person who invented the Fibonacci\n'
            '     *       sequence.\n'
            '     *\n'
            '     * Example:\n'
            '     * >>> Fibonacci.fibonacci(3) + " " + '
            'Fibonacci.fibonacci(4) + " " + Fibonacci.fibonacci(5);\n'
            '     * 2 3 5\n'
            '     * @param n The number in the Fibonacci sequence to\n'
            '     *        compute. A value of 0 indicates the 0th\n'
            '     *        number, 0, a value of 1 indicates the first\n'
            '     *        number, 1, and so on.\n'
            '     * @return\t \t The nth Fibonacci number.  This method\n'
            '     *        \t \t returns 0 if n is 0.\n'
            '     * @author jsmith\n'
            '     */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_passive(self):
        """Test the "wrap_as_you_type_passive" setting."""
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('wrap_as_you_type_passive', True)
        settings.set('rulers', [60])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.\n'
            ' */\n'
            'int fibonacci(int n) {\n'
            '    // Base case\n'
            '    if (n == 0) {\n'
            '        return 0;\n'
            '    }\n'
            '\n'
            '    // Iterative implementation of "fibonacci"\n'
            '    int cur = 1;\n'
            '    int prev = 0;\n'
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n'
            '    return cur;\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    cout << "The 8th Fibonacci number is " <<\n'
            '        fibonacci(8) << "\\n";\n'
            '    return 0;\n'
            '}\n')

        comment_start_point = view.find(r'/\*\*', 0).begin()
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._insert(point, '  The function assumes that n >= 0.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.  The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('The function assumes', 0).begin() - 1
        self._insert(
            point,
            'The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number. Every subsequent number is equal to the sum '
            'of the two previous numbers.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers. The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'Fibonacci sequence\.', 0).end() - 1
        self._insert(point, ', defined as follows')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence, defined as follows. The Fibonacci\n'
            ' * sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers. The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        region = view.find(r'as follows', 0)
        self._backspace(region)
        self._insert(region.begin(), 'hence')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence, defined hence. The Fibonacci sequence\n'
            ' * begins with 0\n'
            ' * as the 0th number and 1 as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers. The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('1 as the first', 0).begin()
        self._delete(point, 1)
        self._insert(point, 'one')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence, defined hence. The Fibonacci sequence\n'
            ' * begins with 0\n'
            ' * as the 0th number and one as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers. The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'assumes that n >= 0\.', 0).end()
        self._insert(point, ' It requires n to be an integer.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence, defined hence. The Fibonacci sequence\n'
            ' * begins with 0\n'
            ' * as the 0th number and one as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers. The function assumes that n >= 0. It requires n\n'
            ' * to be an integer.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_toggle(self):
        """Test the "wrap_as_you_type_disabled" setting.

        Test the "wrap_as_you_type_disabled" setting and
        ToggleWrapAsYouTypeCommand.
        """
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('rulers', [60])
        settings.erase('wrap_as_you_type_disabled')

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.\n'
            ' */\n'
            'int fibonacci(int n) {\n'
            '    // Base case\n'
            '    if (n == 0) {\n'
            '        return 0;\n'
            '    }\n'
            '\n'
            '    // Iterative implementation of "fibonacci"\n'
            '    int cur = 1;\n'
            '    int prev = 0;\n'
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n'
            '    return cur;\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    cout << "The 8th Fibonacci number is " <<\n'
            '        fibonacci(8) << "\\n";\n'
            '    return 0;\n'
            '}\n')

        comment_start_point = view.find(r'/\*\*', 0).begin()
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._insert(point, '  The function assumes that n >= 0.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.  The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        view.run_command('toggle_wrap_as_you_type')
        point = view.find('The function assumes', 0).begin() - 1
        self._insert(
            point,
            'The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number. Every subsequent number is equal to the sum '
            'of the two previous numbers.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0 as '
            'the 0th number and 1 as the first number. Every subsequent '
            'number is equal to the sum of the two previous numbers. The '
            'function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        view.run_command('toggle_wrap_as_you_type')
        point = view.find('The Fibonacci sequence', 0).begin()
        self._delete(point, 82)
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. Every subsequent number is equal to\n'
            ' * the sum of the two previous numbers. The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test setting "wrap_as_you_type_disabled" directly
        settings.set('wrap_as_you_type_disabled', True)
        point = view.find('Every subsequent number', 0).begin()
        self._insert(
            point,
            'The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number. ')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0 as '
            'the 0th number and 1 as the first number. Every subsequent '
            'number is equal to\n'
            ' * the sum of the two previous numbers. The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_extend_section_cpp(self):
        """Test WrapAsYouTypeExtendSectionCommand on C++ code."""
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('rulers', [60])
        settings.set('wrap_as_you_type_enter_extends_section', True)

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers.\n'
            ' */\n'
            'int fibonacci(int n) {\n'
            '    // Base case\n'
            '    if (n == 0) {\n'
            '        return 0;\n'
            '    }\n'
            '\n'
            '    // Iterative implementation of "fibonacci"\n'
            '    int cur = 1;\n'
            '    int prev = 0;\n'
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev; // Store in a temporary variable\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n'
            '    return cur;\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    cout << "The 8th Fibonacci number is " <<\n'
            '        fibonacci(8) << "\\n";\n'
            '    return 0;\n'
            '}\n')

        # Test block comment
        comment_start_point = view.find(r'/\*\*', 0).begin()
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._delete(point, 1)
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.\n'
            ' *\n'
            ' * The Fibonacci sequence begins with 0 as the 0th number\n'
            ' * and 1 as the first number. Every subsequent number is\n'
            ' * equal to the sum of the two previous numbers.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'numbers\.', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        point += 7
        self._insert(
            point, 'Here\'s some background information on Fibonacci:')
        point = view.find('on Fibonacci:', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        point += 7
        self._insert(point, '    - Born around 1175.')
        point = view.find(r'1175\.', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        point += 11
        self._insert(point, '- The Fibonacci sequence is named after him.')
        point = view.find(r'named after him\.', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        point += 11
        self._insert(point, '- Died around 1240-50.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.\n'
            ' *\n'
            ' * The Fibonacci sequence begins with 0 as the 0th number\n'
            ' * and 1 as the first number. Every subsequent number is\n'
            ' * equal to the sum of the two previous numbers.\n'
            ' *\n'
            ' * Here\'s some background information on Fibonacci:\n'
            ' *\n'
            ' *     - Born around 1175.\n'
            ' *\n'
            ' *     - The Fibonacci sequence is named after him.\n'
            ' *\n'
            ' *     - Died around 1240-50.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('The Fibonacci sequence', 0).begin() - 1
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        point = view.find('- Born', 0).begin() - 2
        settings.set('trim_automatic_white_space', False)
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        settings.set('trim_automatic_white_space', True)
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence.\n'
            ' *\n'
            ' *\n'
            '  The Fibonacci sequence begins with 0 as the 0th number\n'
            ' * and 1 as the first number. Every subsequent number is\n'
            ' * equal to the sum of the two previous numbers.\n'
            ' *\n'
            ' * Here\'s some background information on Fibonacci:\n'
            ' *\n'
            ' *   \n'
            ' *     - Born around 1175.\n'
            ' *\n'
            ' *     - The Fibonacci sequence is named after him.\n'
            ' *\n'
            ' *     - Died around 1240-50.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test line comment
        comment_start_point = view.find(
            '    // Iterative implementation', 0).begin()
        point = view.find('implementation of "fibonacci"', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        point += 15
        self._insert(
            point,
            'At each step, we update the "cur" and "prev" to advance the '
            'current and previous Fibonacci numbers.')
        point = view.find(r'previous Fibonacci numbers\.', 0).end()
        expected_text = (
            '    // Iterative implementation of "fibonacci"\n'
            '    //\n'
            '    // At each step, we update the "cur" and "prev" to\n'
            '    // advance the current and previous Fibonacci numbers.\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('"cur" and "prev"', 0).end()
        self._insert(point, ':')
        self._set_selection_region(Region(point + 1, point + 2))
        view.run_command('wrap_as_you_type_extend_section')
        expected_text = (
            '    // Iterative implementation of "fibonacci"\n'
            '    //\n'
            '    // At each step, we update the "cur" and "prev":\n'
            '    // to advance the current and previous Fibonacci\n'
            '    // numbers.\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test trailing line comment and ordinary code
        start_point = view.find('        int next', 0).begin()
        point = view.find('temporary variable', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        point += 9
        self._insert(point, 'cout << "Next is " << next << \'\\n\';')
        point = view.find('next << \'\\\\n\';', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        point += 9
        self._insert(point, 'cout << "Current is " << cur << \'\\n\';')
        expected_text = (
            '        int next = cur + prev; // Store in a temporary variable\n'
            '        cout << "Next is " << next << \'\\n\';\n'
            '        cout << "Current is " << cur << \'\\n\';\n'
            '        prev = cur;\n'
            '        cur = next;\n')
        actual_text = view.substr(
            Region(start_point, start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_extend_section_python(self):
        """Test WrapAsYouTypeExtendSectionCommand on Python code."""
        # This method tests an empty line start string
        view = self._view
        self._set_up_python()
        view.settings().set('wrap_as_you_type_enter_extends_section', True)

        self._append(
            'def fibonacci(n):\n'
            '    """Return the nth number in the Fibonacci sequence."""\n'
            '    # Base case\n'
            '    if n == 0:\n'
            '        return 0\n'
            '\n'
            '    # Iterative implementation of "fibonacci"\n'
            '    cur = 1\n'
            '    prev = 0\n'
            '    for i in range(1, n):\n'
            '        cur, prev = cur + prev, cur\n'
            '    return cur\n'
            '\n'
            'print(\'The 8th Fibonacci number is {:d}\'.format(fibonacci(8)))'
            '\n')

        comment_start_point = view.find('    """', 0).begin()
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        self._insert(point + 2, '    Assume that n >= 0.')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '\n'
            '    Assume that n >= 0.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'Assume that', 0).begin() - 1
        self._insert(
            point,
            ' The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number. Every subsequent number is equal to the sum of '
            'the two previous numbers.')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '\n'
            '    The Fibonacci sequence begins with 0 as the 0th number and 1 '
            'as the\n'
            '    first number. Every subsequent number is equal to the sum '
            'of the two\n'
            '    previous numbers. Assume that n >= 0.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'Assume that', 0).begin() - 1
        self._delete(point, 1)
        self._set_selection_point(point)
        view.run_command('wrap_as_you_type_extend_section')
        view.run_command('wrap_as_you_type_extend_section')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '\n'
            '    The Fibonacci sequence begins with 0 as the 0th number and 1 '
            'as the\n'
            '    first number. Every subsequent number is equal to the sum '
            'of the two\n'
            '    previous numbers.\n'
            '\n'
            '    Assume that n >= 0.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)
