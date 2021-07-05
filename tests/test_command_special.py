from sublime import Region

from WrapAsYouType.tests.command_test_base import WrapAsYouTypeCommandTestBase


class TestWrapAsYouTypeCommandSpecial(WrapAsYouTypeCommandTestBase):
    """Test WrapAsYouTypeCommand under "unusual" editing behavior."""

    def test_c_sharp(self):
        """Test WrapAsYouTypeCommand on edits to C# comments."""
        view = self._view
        view.set_syntax_file('Packages/C#/C#.tmLanguage')
        settings = view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'line_start': ' * ',
                    'selector':
                        'comment.block - (comment.block.documentation | '
                        'punctuation.definition.comment.begin | '
                        'punctuation.definition.comment.end)',
                },
                {
                    # For kicks, put the line start in an allowed_line_starts
                    # list
                    'allowed_line_starts': ['///'],

                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'selector':
                        'comment.line.documentation | '
                        'comment.block.documentation',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '//',
                    'selector': 'comment.line - comment.line.documentation',
                },
            ])
        settings.set('rulers', [60, 80])

        self._append(
            'namespace HelloWorld\n'
            '{\n'
            '    /// A class for printing, "Hello, world!"\n'
            '    class HelloWorld\n'
            '    {\n'
            '        static void Main()\n'
            '        {\n'
            '            System.Console.WriteLine("Hello, world!");\n'
            '        }\n'
            '    }\n'
            '}\n')

        # Test mixed double-slash and triple-slash comments
        comment_start_point = view.find('///', 0).begin() - 4
        point = view.find('A class for printing', 0).end() + 17
        self._insert(
            point,
            '\n// This is program written in the C# programming language that '
            'simply prints the string, "Hello, world!" to the standard '
            'output.')
        expected_text = (
            '    /// A class for printing, "Hello, world!"\n'
            '    // This is program written in the C# programming\n'
            '    // language that simply prints the string, "Hello,\n'
            '    // world!" to the standard output.\n'
            '    class HelloWorld\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('A class for printing', 0).end() + 17
        self._insert(
            point,
            ' This is the traditional program to write when one starts '
            'learning a programming language.')
        expected_text = (
            '    /// A class for printing, "Hello, world!" This is the\n'
            '    /// traditional program to write when one starts\n'
            '    /// learning a programming language.\n'
            '    // This is program written in the C# programming\n'
            '    // language that simply prints the string, "Hello,\n'
            '    // world!" to the standard output.\n'
            '    class HelloWorld\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        self._insert(comment_start_point, '\n')
        self._insert(
            comment_start_point,
            '    // Check out this program I just finished writing. Isn\'t '
            'it great?')
        expected_text = (
            '    // Check out this program I just finished writing. Isn\'t\n'
            '    // it great?\n'
            '    /// A class for printing, "Hello, world!" This is the\n'
            '    /// traditional program to write when one starts\n'
            '    /// learning a programming language.\n'
            '    // This is program written in the C# programming\n'
            '    // language that simply prints the string, "Hello,\n'
            '    // world!" to the standard output.\n'
            '    class HelloWorld\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test mixing in /* */ comments
        point = view.find('A class for printing', 0).begin() - 8
        self._insert(point, '\n')
        self._insert(point, '/**\n\n */')
        self._insert(
            point + 4,
            ' * This is the class for a "Hello World" program. The '
            'implementation is highly intricate and can only be understood by '
            'the most seasoned developers.')
        expected_text = (
            '    // Check out this program I just finished writing. Isn\'t\n'
            '    // it great?\n'
            '/**\n'
            ' * This is the class for a "Hello World" program. The\n'
            ' * implementation is highly intricate and can only be\n'
            ' * understood by the most seasoned developers.\n'
            ' */\n'
            '    /// A class for printing, "Hello, world!" This is the\n'
            '    /// traditional program to write when one starts\n'
            '    /// learning a programming language.\n'
            '    // This is program written in the C# programming\n'
            '    // language that simply prints the string, "Hello,\n'
            '    // world!" to the standard output.\n'
            '    class HelloWorld\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('A class for printing', 0).begin() - 8
        self._backspace(Region(point, point + 4))
        point = view.find('traditional program', 0).begin() - 8
        self._backspace(Region(point, point + 4))
        point = view.find(r'learning a programming language\.', 0).begin() - 8
        self._backspace(Region(point, point + 4))
        start_point = view.find('This is the class ', 0).begin()
        end_point = view.find(r'a "Hello World" program\. ', 0).end()
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '    // Check out this program I just finished writing. Isn\'t\n'
            '    // it great?\n'
            '/**\n'
            ' * The implementation is highly intricate and can only be\n'
            ' * understood by the most seasoned developers.\n'
            ' */\n'
            '/// A class for printing, "Hello, world!" This is the\n'
            '/// traditional program to write when one starts learning a\n'
            '/// programming language.\n'
            '    // This is program written in the C# programming\n'
            '    // language that simply prints the string, "Hello,\n'
            '    // world!" to the standard output.\n'
            '    class HelloWorld\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_no_line_start(self):
        """Test a section with no "line_start" or "allowed_line_starts" entry.
        """
        view = self._view
        view.set_syntax_file('Packages/C++/C++.tmLanguage')
        settings = view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'selector':
                        'comment.block - punctuation.definition.comment',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '//',
                    'selector': 'comment.line',
                },
            ])
        settings.set('rulers', [60, 50])
        settings.set('trim_automatic_white_space', False)

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n'
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence.\n'
            '*/\n'
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
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence.  The function assumes that n >= 0.\n'
            '*/\n')
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
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test paragraphs
        point = view.find(r'assumes that n >= 0\.', 0).end()
        self._insert(
            point,
            '\n'
            '\n'
            'Here\'s some background information on Fibonacci:\n'
            '    - Born around 1175.\n'
            '\n'
            '- The Fibonacci sequence is named after him.\n'
            '\n'
            '- Died around 1240-50.')
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Died around 1240-50.\n'
            '*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('some background information', 0).end() + 14
        self._insert(
            point,
            ', also known as Leonardo Bonacci, Leonardo of Pisa, Leonardo '
            'Pisano Bigollo, or Leonardo Fibonacci')
        self._delete(point - 1, 1)
        self._insert(point + 97, ':')
        point = view.find(r'Died around 1240-50\.', 0).end() + 1
        self._insert(point, '\n')
        self._insert(point, 'Truly, a great man.')
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci, also known\n'
            'as Leonardo Bonacci, Leonardo of Pisa, Leonardo Pisano\n'
            'Bigollo, or Leonardo Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Died around 1240-50.\n'
            'Truly, a great man.\n'
            '*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'Died around 1240-50\.', 0).end()
        self._insert(
            point,
            ' Scholars have been unable to determine the precise year of his '
            'death.')
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci, also known\n'
            'as Leonardo Bonacci, Leonardo of Pisa, Leonardo Pisano\n'
            'Bigollo, or Leonardo Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Died around 1240-50. Scholars have been unable to\n'
            '    determine the precise year of his death.\n'
            'Truly, a great man.\n'
            '*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'Died around 1240-50\.', 0).begin()
        self._delete(point, 21)
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci, also known\n'
            'as Leonardo Bonacci, Leonardo of Pisa, Leonardo Pisano\n'
            'Bigollo, or Leonardo Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Scholars have been unable to determine the precise\n'
            '    year of his death.\n'
            'Truly, a great man.\n'
            '*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test text on the same line as the */
        point = view.find(r'\*/', 0).begin()
        self._insert(point, '\n')
        self._insert(
            point + 1,
            'It is worth noting that the limit of the ratio of consecutiv')
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci, also known\n'
            'as Leonardo Bonacci, Leonardo of Pisa, Leonardo Pisano\n'
            'Bigollo, or Leonardo Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Scholars have been unable to determine the precise\n'
            '    year of his death.\n'
            'Truly, a great man.\n'
            '\n'
            'It is worth noting that the limit of the ratio of consecutiv*/\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'\*/', 0).begin()
        self._insert(
            point,
            'e terms in the Fibonacci sequence is equal to the golden ratio. ')
        expected_text = (
            '/**\n'
            'The "fibonacci" function returns the nth number in the\n'
            'Fibonacci sequence. The Fibonacci sequence begins with 0 as\n'
            'the 0th number and 1 as the first number. Every subsequent\n'
            'number is equal to the sum of the two previous numbers. The\n'
            'function assumes that n >= 0.\n'
            '\n'
            'Here\'s some background information on Fibonacci, also known\n'
            'as Leonardo Bonacci, Leonardo of Pisa, Leonardo Pisano\n'
            'Bigollo, or Leonardo Fibonacci:\n'
            '    - Born around 1175.\n'
            '    \n'
            '    - The Fibonacci sequence is named after him.\n'
            '    \n'
            '    - Scholars have been unable to determine the precise\n'
            '    year of his death.\n'
            'Truly, a great man.\n'
            '\n'
            'It is worth noting that the limit of the ratio of\n'
            'consecutive terms in the Fibonacci sequence is equal to the\n'
            'golden ratio. */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_whitespace_line_start(self):
        """Test a "line_start" entry that consists exclusively of whitespace.

        Test a "line_start" entry (other than '') that consists
        exclusively of whitespace.
        """
        view = self._view
        view.set_syntax_file('Packages/C++/C++.tmLanguage')
        settings = view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'line_start': ' \t ',
                    'selector':
                        'comment.block - punctuation.definition.comment',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '//',
                    'selector': 'comment.line',
                },
            ])
        settings.set('rulers', [60])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\t \t\t \t \t  \n'
            '\t \t\t \t \t  /**\n'
            '\t \t\t \t \t  The responsibility of the\n'
            '\t \t\t \t \t  returnSomething() function is to\n'
            '\t \t\t \t \t  return something - anything.\n'
            '\t \t\t \t \t  */\n'
            '\t \t\t \t \t  int returnSomething() {\n'
            '\t \t\t \t \t      return 42;\n'
            '\t \t\t \t \t  }\n')

        # Test indentation that matches the line start in multiple places
        comment_start_point = view.find(r'/\*\*', 0).begin() - 10
        point = view.find(r'return something - anything\.', 0).end()
        self._insert(
            point,
            ' Well, anything of type int at least. In C++, an int with a '
            'width of 32 bits must be in the range -2^31 to 2^31 - 1.')
        expected_text = (
            '\t \t\t \t \t  /**\n'
            '\t \t\t \t \t  The responsibility of the\n'
            '\t \t\t \t \t  returnSomething() function is to\n'
            '\t \t\t \t \t  return something - anything. Well,\n'
            '\t \t\t \t \t  anything of type int at least. In C++,\n'
            '\t \t\t \t \t  an int with a width of 32 bits must be\n'
            '\t \t\t \t \t  in the range -2^31 to 2^31 - 1.\n'
            '\t \t\t \t \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Make sure that a line that doesn't start with the line start is not
        # wrapped
        settings.set('trim_automatic_white_space', False)
        point = view.find(r'2\^31 - 1\.', 0).end()
        self._insert(point, '\n\n')
        self._delete(point + 18, 1)
        self._insert(
            point + 21,
            'Integers are not the same thing as natural numbers, as the '
            'latter must be nonnegative.')
        expected_text = (
            '\t \t\t \t \t  /**\n'
            '\t \t\t \t \t  The responsibility of the\n'
            '\t \t\t \t \t  returnSomething() function is to\n'
            '\t \t\t \t \t  return something - anything. Well,\n'
            '\t \t\t \t \t  anything of type int at least. In C++,\n'
            '\t \t\t \t \t  an int with a width of 32 bits must be\n'
            '\t \t\t \t \t  in the range -2^31 to 2^31 - 1.\n'
            '\t \t\t \t \t  \n'
            '\t \t\t \t\t  Integers are not the same thing as natural '
            'numbers, as the latter must be nonnegative.\n'
            '\t \t\t \t \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_allowed_line_starts(self):
        """Test the "allowed_line_starts" entry in "wrap_as_you_type_sections".

        Test setting "allowed_line_starts" entry in an element of the
        "wrap_as_you_type_sections" setting.
        """
        view = self._view
        view.set_syntax_file('Packages/C++/C++.tmLanguage')
        settings = view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'line_start': ' * ',
                    'selector':
                        'comment.block - punctuation.definition.comment',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'allowed_line_starts': ['// ', '/// '],
                    'selector': 'comment.line',
                },
            ])
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

        point = view.find(r'previous number\.', 0).end()
        self._insert(
            point,
            '\n/// We initialize "prev" to the 0th number, 0, and "next" to '
            'the first number, 1.')
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev", the value of the\n'
            '    // previous number.\n'
            '    /// We initialize "prev" to the 0th number, 0, and\n'
            '    /// "next" to the first number, 1.\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'first number, 1\.', 0).end()
        self._insert(
            point,
            '\n// Inside the loop, we have to be careful to assign the sum '
            'cur + prev to a temporary value "next" before overwriting the '
            'value of "cur", which we will need to store as "prev".')
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev", the value of the\n'
            '    // previous number.\n'
            '    /// We initialize "prev" to the 0th number, 0, and\n'
            '    /// "next" to the first number, 1.\n'
            '    // Inside the loop, we have to be careful to assign the\n'
            '    // sum cur + prev to a temporary value "next" before\n'
            '    // overwriting the value of "cur", which we will need to\n'
            '    // store as "prev".\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find('0th number, 0', 0).end()
        end_point = view.find('first number, 1', 0).end()
        self._backspace(Region(start_point, end_point))
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev", the value of the\n'
            '    // previous number.\n'
            '    /// We initialize "prev" to the 0th number, 0.\n'
            '    // Inside the loop, we have to be careful to assign the\n'
            '    // sum cur + prev to a temporary value "next" before\n'
            '    // overwriting the value of "cur", which we will need to\n'
            '    // store as "prev".\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('and "prev"', 0).end()
        self._delete(point, 34)
        expected_text = (
            '    // Iterative implementation of "fibonacci". We maintain\n'
            '    // two variables: "cur", the value of the current number\n'
            '    // in the sequence, and "prev".\n'
            '    /// We initialize "prev" to the 0th number, 0.\n'
            '    // Inside the loop, we have to be careful to assign the\n'
            '    // sum cur + prev to a temporary value "next" before\n'
            '    // overwriting the value of "cur", which we will need to\n'
            '    // store as "prev".\n'
            '    int cur = 1;\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_tabs_and_spaces(self):
        """Test indenting with mixed tabs and spaces."""
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\t  \t \n'
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something - anything.\n'
            '\t  \t  */\n'
            '\t  \t int returnSomething() {\n'
            '\t  \t     return 42;\n'
            '\t  \t }\n')

        # Test mixed spaces and tabs before the line start
        comment_start_point = view.find(r'/\*\*', 0).begin() - 5
        point = view.find(r'return something - anything\.', 0).end()
        self._insert(
            point,
            ' Well, anything of type int at least. In C++, an int with a '
            'width of 32 bits must be in the range -2^31 to 2^31 - 1.')
        expected_text = (
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something - anything.\n'
            '\t  \t  * Well, anything of type int at least. In C++, an\n'
            '\t  \t  * int with a width of 32 bits must be in the range\n'
            '\t  \t  * -2^31 to 2^31 - 1.\n'
            '\t  \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Make sure that a line that doesn't start with the line start is not
        # wrapped
        point = view.find(r'2\^31 - 1\.', 0).end()
        self._insert(point, '\n* \n')
        self._delete(point + 14, 2)
        self._insert(
            point + 14,
            '* Integers are not the same thing as natural numbers, as the '
            'latter must be nonnegative.')
        expected_text = (
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something - anything.\n'
            '\t  \t  * Well, anything of type int at least. In C++, an\n'
            '\t  \t  * int with a width of 32 bits must be in the range\n'
            '\t  \t  * -2^31 to 2^31 - 1.\n'
            '\t  \t  * \n'
            '\t  \t* Integers are not the same thing as natural numbers, as '
            'the latter must be nonnegative.\n'
            '\t  \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        point = view.find('return something - anything', 0).begin() + 16
        self._delete(point, 48)
        expected_text = (
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something. In C++, an int\n'
            '\t  \t  * with a width of 32 bits must be in the range\n'
            '\t  \t  * -2^31 to 2^31 - 1.\n'
            '\t  \t  * \n'
            '\t  \t* Integers are not the same thing as natural numbers, as '
            'the latter must be nonnegative.\n'
            '\t  \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test mixed spaces and tabs after the line start
        point = view.find('must be nonnegative.', 0).end()
        self._insert(point, '\n')
        self._delete(point + 1, 4)
        self._insert(
            point + 1,
            ' * \t \tNor are they the same as rational numbers.  Rational '
            'numbers are repeating or terminating decimals, or equivalently, '
            'fractions.')
        expected_text = (
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something. In C++, an int\n'
            '\t  \t  * with a width of 32 bits must be in the range\n'
            '\t  \t  * -2^31 to 2^31 - 1.\n'
            '\t  \t  * \n'
            '\t  \t* Integers are not the same thing as natural numbers, as '
            'the latter must be nonnegative.\n'
            ' * \t \tNor are they the same as rational numbers.  Rational\n'
            ' * \t \tnumbers are repeating or terminating decimals, or\n'
            ' * \t \tequivalently, fractions.\n'
            '\t  \t  */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        # Test a word that exceeds the wrap width, and code that exceeds the
        # wrap width
        point = view.find(r'2\^31 - 1\.', 0).end()
        self._insert(
            point,
            ' See '
            'http://www.example.com/integers/this-website-is-too-long-for-one-'
            'line for more details.')
        point = view.find('return 42;', 0).begin()
        self._backspace(Region(point, point + 10))
        self._insert(
            point,
            'return 73 * 184 + ((1704 - 1600) * (305 - 16) / ((9 + 16) % 8));')
        expected_text = (
            '\t  \t /**\n'
            '\t  \t  * The responsibility of the returnSomething()\n'
            '\t  \t  * function is to return something. In C++, an int\n'
            '\t  \t  * with a width of 32 bits must be in the range\n'
            '\t  \t  * -2^31 to 2^31 - 1. See\n'
            '\t  \t  * http://www.example.com/integers/this-website-is-too-'
            'long-for-one-line\n'
            '\t  \t  * for more details.\n'
            '\t  \t  * \n'
            '\t  \t* Integers are not the same thing as natural numbers, as '
            'the latter must be nonnegative.\n'
            ' * \t \tNor are they the same as rational numbers.  Rational\n'
            ' * \t \tnumbers are repeating or terminating decimals, or\n'
            ' * \t \tequivalently, fractions.\n'
            '\t  \t  */\n'
            '\t  \t int returnSomething() {\n'
            '\t  \t     return 73 * 184 + ((1704 - 1600) * (305 - 16) / ((9 + '
            '16) % 8));\n'
            '\t  \t }\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_beginning_of_document(self):
        """Test word wrapping at the beginning of the document.

        Test word wrapping of a section of line comments that starts at
        the beginning of the document.
        """
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

        comment_start_point = 0
        self._insert(
            comment_start_point,
            '// Lorem ipsum dolor sit amet, iudicabit interpretaris ius eu, '
            'et sit iudico aperiri scaevola. Ad solum eleifend sea, ex ius '
            'graeci alienum accusamus, diam mandamus expetenda quo ei.\n')
        expected_text = (
            '// Lorem ipsum dolor sit amet, iudicabit interpretaris ius\n'
            '// eu, et sit iudico aperiri scaevola. Ad solum eleifend\n'
            '// sea, ex ius graeci alienum accusamus, diam mandamus\n'
            '// expetenda quo ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'aperiri scaevola\.', 0).end()
        self._insert(
            point,
            ' Vim case eros choro et, te deserunt iudicabit assentior eum, id '
            'his assum nobis primis.')
        expected_text = (
            '// Lorem ipsum dolor sit amet, iudicabit interpretaris ius\n'
            '// eu, et sit iudico aperiri scaevola. Vim case eros choro\n'
            '// et, te deserunt iudicabit assentior eum, id his assum\n'
            '// nobis primis. Ad solum eleifend sea, ex ius graeci\n'
            '// alienum accusamus, diam mandamus expetenda quo ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find('Lorem ipsum', 0).begin()
        self._delete(point, 92)
        expected_text = (
            '// Vim case eros choro et, te deserunt iudicabit assentior\n'
            '// eum, id his assum nobis primis. Ad solum eleifend sea, ex\n'
            '// ius graeci alienum accusamus, diam mandamus expetenda quo\n'
            '// ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)

    def test_end_of_document(self):
        """Test word wrapping at the end of the document.

        Test word wrapping of a C++ block comment that isn't closed with
        a */, and so extends to the end of the document.
        """
        view = self._view
        self._set_up_cpp()
        view.settings().set('rulers', [60])

        self._append(
            '#include <iostream>\n'
            '\n'
            'using namespace std;\n'
            '\n')

        comment_start_point = view.size()
        self._insert(
            comment_start_point,
            '/**\n'
            ' * Lorem ipsum dolor sit amet, iudicabit interpretaris ius eu, '
            'et sit iudico aperiri scaevola. Ad solum eleifend sea, ex ius '
            'graeci alienum accusamus, diam mandamus expetenda quo ei.')
        expected_text = (
            '/**\n'
            ' * Lorem ipsum dolor sit amet, iudicabit interpretaris ius\n'
            ' * eu, et sit iudico aperiri scaevola. Ad solum eleifend\n'
            ' * sea, ex ius graeci alienum accusamus, diam mandamus\n'
            ' * expetenda quo ei.')
        actual_text = view.substr(Region(comment_start_point, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'aperiri scaevola\.', 0).end()
        self._insert(
            point,
            ' Vim case eros choro et, te deserunt iudicabit assentior eum, id '
            'his assum nobis primis.')
        expected_text = (
            '/**\n'
            ' * Lorem ipsum dolor sit amet, iudicabit interpretaris ius\n'
            ' * eu, et sit iudico aperiri scaevola. Vim case eros choro\n'
            ' * et, te deserunt iudicabit assentior eum, id his assum\n'
            ' * nobis primis. Ad solum eleifend sea, ex ius graeci\n'
            ' * alienum accusamus, diam mandamus expetenda quo ei.')
        actual_text = view.substr(Region(comment_start_point, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find('Lorem ipsum', 0).begin()
        self._delete(point, 92)
        expected_text = (
            '/**\n'
            ' * Vim case eros choro et, te deserunt iudicabit assentior\n'
            ' * eum, id his assum nobis primis. Ad solum eleifend sea, ex\n'
            ' * ius graeci alienum accusamus, diam mandamus expetenda quo\n'
            ' * ei.')
        actual_text = view.substr(Region(comment_start_point, view.size()))
        self.assertEqual(actual_text, expected_text)

    def test_bulk_insert_delete(self):
        """Test insertion and deletion of multiple characters at a time.

        This is meant to simulate operations such as pasting text and
        selecting multiple characters and pressing backspace.
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
        point = view.find('The function assumes', 0).begin() - 1
        self._set_selection_point(point)
        view.run_command(
            'insert', {
                'characters':
                    ' The Fibonacci sequence begins with 0 as the 0th number '
                    'and 1 as the first number. Every subsequent number is '
                    'equal to the sum of the two previous numbers.',
            })
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

        start_point = view.find(r'1 as the first number\.', 0).end() + 1
        end_point = view.find('The function assumes', 0).begin()
        self._set_selection_region(Region(start_point, end_point))
        view.run_command('left_delete')
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence begins with 0\n'
            ' * as the 0th number and 1 as the first number. The function\n'
            ' * assumes that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

        start_point = view.find('begins with 0', 0).begin()
        end_point = view.find('1 as the first number', 0).end()
        self._set_selection_region(Region(start_point, end_point))
        view.run_command(
            'insert',
            {'characters': 'is the sequence 1, 1, 2, 3, 5, 8, 13, etc'})
        expected_text = (
            '/**\n'
            ' * The "fibonacci" function returns the nth number in the\n'
            ' * Fibonacci sequence. The Fibonacci sequence is the\n'
            ' * sequence 1, 1, 2, 3, 5, 8, 13, etc. The function assumes\n'
            ' * that n >= 0.\n'
            ' */\n')
        actual_text = view.substr(
            Region(
                comment_start_point, comment_start_point + len(expected_text)))
        self.assertEqual(actual_text, expected_text)

    def test_wrap_entire_document(self):
        """Test a "wrap_as_you_type_sections" setting that wraps everything.

        Test a "wrap_as_you_type_sections" setting that performs word
        wrapping on the entire document.
        """
        view = self._view
        view.set_syntax_file('Packages/Text/Plain text.tmLanguage')
        settings = view.settings()
        settings.set(
            'wrap_as_you_type_sections', [{'selector': 'source | text'}])
        settings.set('rulers', [60])

        self._insert(
            0,
            'Lorem ipsum dolor sit amet, iudicabit interpretaris ius eu, et '
            'sit iudico aperiri scaevola. Ad solum eleifend sea, ex ius '
            'graeci alienum accusamus, diam mandamus expetenda quo ei.\n')
        expected_text = (
            'Lorem ipsum dolor sit amet, iudicabit interpretaris ius eu,\n'
            'et sit iudico aperiri scaevola. Ad solum eleifend sea, ex\n'
            'ius graeci alienum accusamus, diam mandamus expetenda quo\n'
            'ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find(r'aperiri scaevola\.', 0).end()
        self._insert(
            point,
            ' Vim case eros choro et, te deserunt iudicabit assentior eum, id '
            'his assum nobis primis.')
        expected_text = (
            'Lorem ipsum dolor sit amet, iudicabit interpretaris ius eu,\n'
            'et sit iudico aperiri scaevola. Vim case eros choro et, te\n'
            'deserunt iudicabit assentior eum, id his assum nobis primis.\n'
            'Ad solum eleifend sea, ex ius graeci alienum accusamus, diam\n'
            'mandamus expetenda quo ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)

        point = view.find('Lorem ipsum', 0).begin()
        self._delete(point, 92)
        expected_text = (
            'Vim case eros choro et, te deserunt iudicabit assentior eum,\n'
            'id his assum nobis primis. Ad solum eleifend sea, ex ius\n'
            'graeci alienum accusamus, diam mandamus expetenda quo ei.\n')
        actual_text = view.substr(Region(0, view.size()))
        self.assertEqual(actual_text, expected_text)
