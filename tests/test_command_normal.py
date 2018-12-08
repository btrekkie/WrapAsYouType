from sublime import Region

from WrapAsYouType.tests.command_test_base import WrapAsYouTypeCommandTestBase


class TestWrapAsYouTypeCommandNormal(WrapAsYouTypeCommandTestBase):
    """Test WrapAsYouTypeCommand under "normal" editing behavior."""

    def test_cpp_block_comments(self):
        """Test WrapAsYouTypeCommand on edits to C++ block comments."""
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

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

        start_point = view.find('The function assumes', 0).begin() - 1
        end_point = start_point + 34
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number. Every\n'
            ' * subsequent number is equal to the sum of the two previous\n'
            ' * numbers.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_cpp_line_comments(self):
        """Test WrapAsYouTypeCommand on edits to C++ line comments."""
        view = self._view
        self._set_up_cpp()
        settings = view.settings()
        settings.set('wrap_width', 60)
        settings.set('rulers', [80])

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

        comment_start_point = view.find('// Iterative', 0).begin() - 4
        point = view.find('implementation of "fibonacci"', 0).end()
        self._insert(
            point,
            '. We maintain two variables: "cur", the value of the current '
            'number in the sequence, and "prev", the value of the previous '
            'number.')
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev", the value of the\n'
            '    // previous number.\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test paragraphs
        point = view.find(r'previous number\.', 0).end()
        self._insert(
            point,
            ' Here\'s what happens at each iteration:\n'
            '//     - The variable "cur" gets set to be the value of prev '
            '+ cur.\n'
            '//\n'
            '//     - The variable "prev" gets set to be the old value of '
            '"cur" - the value at the beginning of the iteration.')
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev", the value of the\n'
            '    // previous number. Here\'s what happens at each\n'
            '    // iteration:\n'
            '    //     - The variable "cur" gets set to be the value of\n'
            '    //     prev + cur.\n'
            '    //\n'
            '    //     - The variable "prev" gets set to be the old\n'
            '    //     value of "cur" - the value at the beginning of\n'
            '    //     the iteration.\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find(', and "prev",', 0).end() - 1
        end_point = view.find(r'previous number\.', 0).end() - 1
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev". Here\'s what happens at\n'
            '    // each iteration:\n'
            '    //     - The variable "cur" gets set to be the value of\n'
            '    //     prev + cur.\n'
            '    //\n'
            '    //     - The variable "prev" gets set to be the old\n'
            '    //     value of "cur" - the value at the beginning of\n'
            '    //     the iteration.\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(' - the value at the', 0).begin() + 3
        self._delete(point, 10)
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev". Here\'s what happens at\n'
            '    // each iteration:\n'
            '    //     - The variable "cur" gets set to be the value of\n'
            '    //     prev + cur.\n'
            '    //\n'
            '    //     - The variable "prev" gets set to be the old\n'
            '    //     value of "cur" - at the beginning of the\n'
            '    //     iteration.\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Make sure that inline comments don't wrap, because they don't extend
        # to the beginning of the line
        comment_start_point = view.find('int next =', 0).begin() - 8
        self._insert(
            comment_start_point + 30,
            '  // In order to make sure that we use the correct value of '
            '"prev" in the addition, we must create a temporary value "next" '
            'to store the result of the addition, before setting "prev" to be '
            '"cur".')
        expected_text = (
            '        int next = cur + prev;  // In order to make sure that we '
            'use the correct value of "prev" in the addition, we must create '
            'a temporary value "next" to store the result of the addition, '
            'before setting "prev" to be "cur".\n'
            '        prev = cur;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def _set_up_python(self):
        """Configure _view to use Python.

        This sets the "wrap_as_you_type_sections" setting to a value
        appropriate to wrapping Python block and line comments.
        """
        self._view.set_syntax_file('Packages/Python/Python.tmLanguage')
        settings = self._view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'selector':
                        'comment.block - punctuation.definition.comment',
                    'wrap_width': 72
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '#',
                    'selector': 'comment.line',
                    'wrap_width': 79,
                },
            ])
        settings.set(
            'wrap_as_you_type_paragraphs', [{'first_line_regex': r'^""?$'}])

    def test_python_block_comments(self):
        """Test WrapAsYouTypeCommand on edits to Python block comments."""
        view = self._view
        self._set_up_python()

        # Attempt to trick WrapAsYouType with an irrelevant ruler
        view.settings().set('rulers', [60])

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
        self._insert(point, '\nAssume that n >= 0.\n')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '    Assume that n >= 0.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('Assume that', 0).begin() - 1
        self._insert(
            point,
            ' The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number. Every subsequent number is equal to the sum '
            'of the two previous numbers.')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '    The Fibonacci sequence begins with 0 as the 0th number and 1 '
            'as the\n'
            '    first number. Every subsequent number is equal to the sum of '
            'the two\n'
            '    previous numbers. Assume that n >= 0.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find('Assume that', 0).begin() - 1
        end_point = start_point + 20
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence.\n'
            '    The Fibonacci sequence begins with 0 as the 0th number and 1 '
            'as the\n'
            '    first number. Every subsequent number is equal to the sum of '
            'the two\n'
            '    previous numbers.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Make sure the first line doesn't wrap
        point = view.find(r'Fibonacci sequence\.', 0).end()
        self._insert(
            point,
            ' The Fibonacci sequence is the sequence 1, 1, 2, 3, 5, 8, etc.')
        expected_text = (
            '    """Return the nth number in the Fibonacci sequence. The '
            'Fibonacci sequence is the sequence 1, 1, 2, 3, 5, 8, etc.\n'
            '    The Fibonacci sequence begins with 0 as the 0th number and 1 '
            'as the\n'
            '    first number. Every subsequent number is equal to the sum of '
            'the two\n'
            '    previous numbers.\n'
            '    """\n'
            '    # Base case\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_python_line_comments(self):
        """Test WrapAsYouTypeCommand on edits to Python line comments."""
        view = self._view
        self._set_up_python()
        view.settings().set('rulers', [60])

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

        comment_start_point = view.find('# Iterative', 0).begin() - 4
        point = view.find('implementation of "fibonacci"', 0).end()
        self._insert(
            point,
            '. We maintain two variables: "cur", the value of the current '
            'number in the sequence, and "prev", the value of the previous '
            'number.')
        expected_text = (
            '    # Iterative implementation of "fibonacci". We maintain two '
            'variables:\n'
            '    # "cur", the value of the current number in the sequence, '
            'and "prev", the\n'
            '    # value of the previous number.\n'
            '    cur = 1\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test paragraphs
        point = view.find(r'previous number\.', 0).end()
        self._insert(
            point,
            ' Here\'s what happens at each iteration:\n'
            '#     - The variable "cur" gets set to be the value of prev '
            '+ cur.\n'
            '#\n'
            '#     - The variable "prev" gets set to be the old value of '
            '"cur" - the value at the beginning of the iteration.')
        expected_text = (
            '    # Iterative implementation of "fibonacci". We maintain two '
            'variables:\n'
            '    # "cur", the value of the current number in the sequence, '
            'and "prev", the\n'
            '    # value of the previous number. Here\'s what happens at each '
            'iteration:\n'
            '    #     - The variable "cur" gets set to be the value of prev '
            '+ cur.\n'
            '    #\n'
            '    #     - The variable "prev" gets set to be the old value of '
            '"cur" - the\n'
            '    #     value at the beginning of the iteration.\n'
            '    cur = 1\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find(', and "prev",', 0).end() - 1
        end_point = view.find(r'previous number\.', 0).end() - 1
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '    # Iterative implementation of "fibonacci". We maintain two '
            'variables:\n'
            '    # "cur", the value of the current number in the sequence, '
            'and "prev".\n'
            '    # Here\'s what happens at each iteration:\n'
            '    #     - The variable "cur" gets set to be the value of prev '
            '+ cur.\n'
            '    #\n'
            '    #     - The variable "prev" gets set to be the old value of '
            '"cur" - the\n'
            '    #     value at the beginning of the iteration.\n'
            '    cur = 1\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_explicit_line_breaks(self):
        """Test WrapAsYouTypeCommand with explicit line breaks.

        Test that WrapAsYouTypeCommand refrains from deleting line
        breaks entered in by the user as he performs forward editing.
        """
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

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
        self._insert(
            point,
            ' The Fibonacci sequence begins with 0 as the 0th number and 1 as '
            'the first number.\n'
            '* Every subsequent number is equal to the sum '
            'of the two previous numbers.\n'
            '* The function assumes that n >= 0.')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number.\n'
            ' * Every subsequent number is equal to the sum of the two\n'
            ' * previous numbers.\n'
            ' * The function assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_comment_out_lines(self):
        """Test WrapAsYouTypeCommand when commenting out lines.

        Test that WrapAsYouTypeCommand does not perform word wrapping
        fixup when commenting out lines of code.
        """
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

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

        block_start_point = view.find(r'for \(int i', 0).begin() - 4
        point = view.find('int next', 0).begin()
        self._insert(point, '//')
        point = view.find('prev = cur;', 0).begin()
        self._set_selection_point(point)
        view.run_command('toggle_comment')
        point = view.find('cur = next;', 0).begin()
        self._insert(point, '//')
        expected_text = (
            '    for (int i = 1; i < n; i++) {\n'
            '        //int next = cur + prev;\n'
            '        // prev = cur;\n'
            '        //cur = next;\n'
            '    }\n')
        actual_text = view.substr(
            Region(block_start_point, block_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find('int next', 0).begin()
        end_point = view.find('cur = next;', 0).end()
        self._set_selection_region(Region(start_point, end_point))
        view.run_command('toggle_comment')
        expected_text = (
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        prev = cur;\n'
            '        cur = next;\n'
            '    }\n')
        actual_text = view.substr(
            Region(block_start_point, block_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        view.run_command('toggle_comment')
        expected_text = (
            '    for (int i = 1; i < n; i++) {\n'
            '        // int next = cur + prev;\n'
            '        // prev = cur;\n'
            '        // cur = next;\n'
            '    }\n')
        actual_text = view.substr(
            Region(block_start_point, block_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('cur = next;', 0).begin() + 4
        self._set_selection_point(point)
        view.run_command('toggle_comment')
        point = view.find('// int next', 0).begin()
        self._delete(point, 3)
        expected_text = (
            '    for (int i = 1; i < n; i++) {\n'
            '        int next = cur + prev;\n'
            '        // prev = cur;\n'
            '        cur = next;\n'
            '    }\n')
        actual_text = view.substr(
            Region(block_start_point, block_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)
