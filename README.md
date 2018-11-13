# Summary
WrapAsYouType is a plugin for the Sublime Text text editor.  The plugin
automatically performs hard word wrapping within specified sections of a file,
in real time as the user types.  For example, WrapAsYouType could limit lines of
C++ code contained in block comments (between `/*` and `*/`) and sequences of
line comments (after `//`) to a width of 80 columns.

Note that you must set the `"wrap_as_you_type_sections"` setting for
WrapAsYouType to operate; see the ["Quick start"](#quick-start) section.

# Table of contents

* [Features](#features)
* [Limitations](#limitations)
* [Quick start](#quick-start)
* [Description](#description)
* [Settings](#settings)
  * [`"wrap_as_you_type_sections"`](#wrap_as_you_type_sections)
    * [Example, C, C++, Go, JavaScript, Objective-C, PHP, Scala, and similar](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
    * [Example, Python in Sublime 3](#example-python-in-sublime-3)
    * [Example, Python in Sublime 2](#example-python-in-sublime-2)
    * [Example, Rust](#example-rust)
    * [Example, wrap the entire document](#example-wrap-the-entire-document)
    * [Example, CSS](#example-css)
    * [Example, Java](#example-java)
    * [Example, Bash, R, Ruby, and similar](#example-bash-r-ruby-and-similar)
    * [Example, C#](#example-c)
    * [Example, Perl](#example-perl)
    * [Additional notes](#additional-notes)
  * [`"wrap_as_you_type_word_regex"`](#wrap_as_you_type_word_regex)
  * [`"wrap_as_you_type_space_between_words"`](#wrap_as_you_type_space_between_words)
  * [`"wrap_as_you_type_paragraphs"`](#wrap_as_you_type_paragraphs)
  * [`"wrap_as_you_type_disabled"`](#wrap_as_you_type_disabled)
* [Comparison with Auto (Hard) Wrap](#comparison-with-auto-hard-wrap)

# Features
* Compatible with Sublime Text 2 and 3.
* Performs hard word wrapping in real time.
* Changes to the middle of a paragraph can result in reflowing the rest of the
  paragraph.
* Able to limit word wrapping to user-specified sections.  The boundaries of
  word-wrapped sections are identified using Sublime scopes.
* Maintains the initial indentation of each wrappable section.
* Allows for different paragraphs with different internal levels of indentation,
  without word wrapping text from one paragraph to another.
* Allows the user to specify text for the beginning of each line.  For example,
  in C++ block comments, the user may want to start each line with `" * "`.
* Provides additional settings for further customization.

# Limitations
* Not likely to be useful for automatically wrapping code or similar non-text
  content.
* Only operates when there is a single selection cursor and nothing is selected.
* Pollutes the undo history.
* Could misbehave if used simultaneously with another Sublime plugin that also
  modifies a document in response to changes to the document.

# Quick start
To install WrapAsYouType, copy the `WrapAsYouType` folder to your Sublime
installation's packages directory.  On macOS, this is `~/Library/Application
Support/Sublime Text 3/Packages`.  On Linux, it is
`~/.config/sublime-text-3/Packages`.  On Windows, it is
`%appdata%\Sublime Text 3\Packages`.  (For Sublime 2, replace `"3"` with `"2"`.)

Once installed, open the syntax-specific settings of your favorite file type.
To do so, open a file of the desired type (e.g. a `*.java` file).  In the menu
bar, go to "Preferences" > "Settings - Syntax Specific" (in Sublime 2, it's
"Preferences" > "Settings - More" > "Syntax Specific - User").

Then, set the `"wrap_as_you_type_sections"` setting to one of the sample values.
To do so, click one of the following links, copy-paste the example configuration
into your syntax-specific settings, and save.

* [Bash](#example-bash-r-ruby-and-similar)
* [C](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [C++](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [C#](#example-c)
* [CSS](#example-css)
* [Go](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [Java](#example-java)
* [JavaScript](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [Objective-C](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [Perl](#example-perl)
* [PHP](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [Plain text](#example-wrap-the-entire-document)
* [Python in Sublime 2](#example-python-in-sublime-2)
* [Python in Sublime 3](#example-python-in-sublime-3)
* [R](#example-bash-r-ruby-and-similar)
* [Ruby](#example-bash-r-ruby-and-similar)
* [Rust](#example-rust)
* [Scala](#example-c-c-go-javascript-objective-c-php-scala-and-similar)
* [Other](#additional-notes)

# Description
WrapAsYouType automatically performs hard word wrapping within specified
sections of a file, in real time as the user types.  For example, WrapAsYouType
could limit lines of C++ code contained in block comments (between `/*` and
`*/`) and sequences of line comments (after `//`) to a width of 80 columns.

A WrapAsYouType "fixup" function operates whenever a document is modified and
there is a single, empty selection cursor.  This function attempts to fix word
wrapping in the vicinity of the cursor.  For example, this may have the effect
of moving text from the end of the current line to the beginning of the next
line or into a new line, or moving text from the beginning of the current line
to the end of the previous line, or moving text from the beginning of the next
line to the end of the current line and reflowing the entire paragraph after the
current line.

WrapAsYouType allows the user to specify the wrap width in the
`"wrap_as_you_type_sections"` setting.  If a wrap width is not provided in that
setting, WrapAsYouType falls back to the value of the `"wrap_width"` setting,
then to the first element of the `"rulers"` setting, then to 80.

WrapAsYouType also allows the user to specify text for the beginning of each
line, such as `" * "` for C++ block comments and `"//"` for C++ line comments.
For example:

```cpp
/**
 * This is how a block comment might look in C++ when each line starts with an
 * asterisk.
 */
```

On a given line, when identifying the text to wrap, WrapAsYouType ignores any
whitespace before and after the "line start" string.

WrapAsYouType has the notion of a "paragraph."  It will only move text within a
single paragraph, and not from one paragraph to another.  By default, two
consecutive lines are in the same paragraph if they have the same indentation,
both before and after the "line start" string.

Example:

```cpp
/**
 * Part 1:
 *     This is a description of part 1.  WrapAsYouType will not attempt to move
 *     the word "This" to the end of the line containing "Part 1", because they
 *     are considered to be in different paragraphs.
 * Part 2:
 *     Description of part 2.  There are four paragraphs in this example.
 */
```

If a line does not start with optional whitespace followed by the line start,
then it is not eligible for wrapping.  In addition, the first line of a
wrappable section (such as a block comment) is not eligible for wrapping, unless
the section extends to the beginning of the first line.  WrapAsYouType never
breaks up an individual word, so if a word is so long that it extends beyond the
wrap width, WrapAsYouType leaves the word on its own line.

You may find that occasionally, WrapAsYouType gets in the way of what you are
trying to type.  Perhaps you are creating a diagram using ASCII art, or perhaps
your comment contains a code sample.  In these cases, it is recommended that you
use the `"toggle_wrap_as_you_type"` command to temporarily disable
WrapAsYouType in the current tab.  You can bind the command to a key combination
by going to the "Preferences" > "Key Bindings" menu item.

Example:

```json
[
    {
        "command": "toggle_wrap_as_you_type",
        "keys": ["super+alt+w"]
    }
]
```

# Settings
## `"wrap_as_you_type_sections"`
`"wrap_as_you_type_sections"` is a critical setting that informs WrapAsYouType
of where in the document to perform word wrapping.  You must set
`"wrap_as_you_type_sections"` for WrapAsYouType to operate.  Typically, you
should set it as a syntax-specific setting, by going to "Preferences" >
"Settings - Syntax Specific" in the menu bar.

### Example, C, C++, Go, JavaScript, Objective-C, PHP, Scala, and similar
```json
{
    "wrap_as_you_type_sections": [
        {
            "line_start": " * ",
            "selector_rules": {
                "and": [
                    "comment.block",
                    {"not": "punctuation.definition.comment"}
                ]
            }
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "//",
            "selector_rules": "comment.line"
        }
    ]
}
```

`"wrap_as_you_type_sections"` is an array of objects.  Each element has the
following entries:

* `"line_start"` (optional): The text appearing at the start of each line, as
  elaborated in the ["Description" section](#description) above.  Defaults to
  the empty string `""`.  Note that sections for single-line comments should
  specify a value that starts with the line comment punctuation - `"//"` in the
  above example.
* `"allowed_line_starts"` (optional): A non-empty list of allowable
  `"line_start"` values.  See the [example for Rust](#example-rust) for details.
  It is an error to include both an `"allowed_line_starts"` entry and a
  `"line_start"` entry.
* `"wrap_width"` (optional): The wrap width for this section type.
* `"selector_rules"`: A "rule set" for identifying text that is in the section.
  See below for details.
* `"combining_selector_rules"` (optional): A "rule set" for extending a section.
  See below for details.

The location of a section is described using a "rule set," which is a
high-level construct that makes use of
[Sublime selectors](https://www.sublimetext.com/docs/3/scope_naming.html).  A
rule set indicates whether we match a given set of scope names.  For example, a
rule set may be used to determine whether the scope
`"source.c++ meta.class.c++ meta.block.c++ comment.block.c"` is a match.  To see
the scope names at a given point in a document, use the `"show_scope_name"`
command.  By default, this is bound to Ctrl+Shift+P on macOS and
Ctrl+Alt+Shift+P on Linux and Windows.

A "rule set" is defined to be any of the following:

* A string indicating the selector to check.  A scope matches if one of the
  scope names is equal to the selector, or starts with the selector followed by
  a dot.
* An array of rule sets.  A scope matches the array if it matches any of its
  elements.
* An object `{"or": rule_sets}`, where `rule_sets` is an array.  A scope
  matches if it matches any of the array's elements.  This is equivalent to
  simply `rule_sets`, per the preceding bullet point; it's just longer and more
  explicit.
* An object `{"and": rule_sets}`, where `rule_sets` is an array.  A scope
  matches if it matches all of the array's elements.
* An object `{"not": rule_set}`.  A scope matches if it does not match
  `rule_set`.

To determine whether a given starting position is inside a given section, we
check whether it matches the `"selector_rules"` rule set.  From there, the
section extends forwards and backwards to include positions that also match the
`"selector_rules"` rule set, or that match the `"combining_selector_rules"` rule
set, if there is one.  The section stops extending in the forwards and backwards
directions once we reach positions that do not match either of the rule sets.

The motivation behind having a separate `"combining_selector_rules"` rule set is
to support word wrapping within sequences of indented single-line comments.  The
single-line comments themselves match the `"comment.line"` selector, but the
indentation does not match that selector.  We must have some way of treating all
of these comments as part of a single combined section; hence,
`"combining_selector_rules"`.

The above sample value of `"wrap_as_you_type_sections"` illustrates how we can
combine consecutive line comments into a single section.  The
`"combining_selector_rules"` rule set matches any text that does not contain
various code elements; i.e. it only matches whitespace.  This instructs
WrapAsYouType to combine a sequence of line comments separated by nothing but
whitespace into a single section.

### Example, Python in Sublime 3
```json
{
    "wrap_as_you_type_sections": [
        {
            "selector_rules": {
                "and": [
                    "comment.block",
                    {"not": "punctuation.definition.comment"}
                ]
            },
            "wrap_width": 72
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "#",
            "selector_rules": "comment.line",
            "wrap_width": 79
        }
    ],
    "wrap_as_you_type_paragraphs": [
        {
            "first_line_regex": "^(\"\"?|''?)$",
            "single_line": true
        }
    ]
}
```

This example applies to Python files in version 3 of Sublime Text.  Here, we
specify different `"wrap_width"` values for block comments and line comments.
This way, we wrap line comments at 79 columns and block comments at 72 columns,
per the recommendations in [PEP8](https://www.python.org/dev/peps/pep-0008/).

Note that in Python, it is recommended to start a block comment with a concise
description of the commented element, on the same line as the opening `"""`.
With the above configuration, WrapAsYouType will not perform word wrapping on
that summary, because WrapAsYouType does not perform wrapping on the first line
of a section, unless the section includes the entire first line.

### Example, Python in Sublime 2
```json
{
    "wrap_as_you_type_sections": [
        {
            "selector_rules": {
                "and": [
                    [
                        "string.quoted.double.block",
                        "string.quoted.single.block"
                    ],
                    {"not": "punctuation.definition.string"}
                ]
            },
            "wrap_width": 72
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "#",
            "selector_rules": "comment.line",
            "wrap_width": 79
        }
    ],
    "wrap_as_you_type_paragraphs": [
        {
            "first_line_regex": "^(\"\"?|''?)$",
            "single_line": true
        }
    ]
}
```

In version 2 of Sublime Text, the built-in syntax file for Python does not scope
docstring comments as `"comment.block"`, so we need to use
`"string.quoted.*.block"` selectors instead.  This has the side effect of
causing WrapAsYouType to wrap all triple-quoted strings, not just docstrings.

### Example, Rust
```json
{
    "wrap_as_you_type_sections": [
        {
            "line_start": " * ",
            "selector_rules": {
                "and": [
                    "comment.block",
                    {"not": "punctuation.definition.comment"}
                ]
            }
        },
        {
            "allowed_line_starts": ["// ", "/// ", "//! "],
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "selector_rules": "comment.line"
        }
    ]
}
```

The `"allowed_line_starts"` entry allows us to specify multiple possible line
starts for a section object.  Logically speaking, such a section object
describes multiple separate section types: one for each allowed line start.  In
the above example, WrapAsYouType distinguishes among double-slash, triple-slash,
and double-slash-bang comments.  It will not move text between two adjacent
sections with different line starts, e.g. from a triple-slash comment to a
double-slash comment.

Depending on the value of `"wrap_as_you_type_sections"`, it may be possible for
the selection cursor to match multiple allowed line starts in a given section
type, or to match multiple section types.  If this happens, WrapAsYouType uses
the earliest matching line start in the earliest matching section type.

### Example, wrap the entire document
```json
{
    "wrap_as_you_type_sections": [
        {
            "selector_rules": {"and": []}
        }
    ]
}
```

### Example, CSS
```json
{
    "wrap_as_you_type_sections": [
        {
            "line_start": " * ",
            "selector_rules": {
                "and": [
                    "comment.block",
                    {"not": "punctuation.definition.comment"}
                ]
            }
        }
    ]
}
```

### Example, Java
```json
{
    "wrap_as_you_type_sections": [
        {
            "line_start": " * ",
            "selector_rules": {
                "and": [
                    "comment.block",
                    {
                        "not": [
                            "punctuation.definition.comment.begin",
                            "punctuation.definition.comment.end"
                        ]
                    }
                ]
            }
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "//",
            "selector_rules": "comment.line"
        }
    ]
}
```

### Example, Bash, R, Ruby, and similar
```json
{
    "wrap_as_you_type_sections": [
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "#",
            "selector_rules": "comment.line"
        }
    ]
}
```

### Example, C#
```json
{
    "wrap_as_you_type_sections": [
        {
            "line_start": " * ",
            "selector_rules": {
                "and": [
                    "comment.block",
                    {
                        "not": [
                            "comment.block.documentation",
                            "punctuation.definition.comment"
                        ]
                    }
                ]
            }
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "///",
            "selector_rules": "comment.block.documentation"
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "//",
            "selector_rules": "comment.line"
        }
    ]
}
```

### Example, Perl
```json
{
    "wrap_as_you_type_sections": [
        {
            "selector_rules": {
                "and": [
                    "comment.block",
                    {"not": "punctuation.definition.comment"}
                ]
            }
        },
        {
            "combining_selector_rules": {
                "not": [
                    "comment", "constant", "entity", "invalid", "keyword",
                    "punctuation", "storage", "string", "variable"
                ]
            },
            "line_start": "#",
            "selector_rules": "comment.line"
        }
    ]
}
```

### Additional notes
If your favorite syntax is not listed above, and you want to wrap comments, it
shouldn't be too difficult to take an example for a similar syntax and modify it
to work with your syntax.

In languages like C++, if you don't like starting each line of a block comment
with an asterisk, then remove `"line_start": " * ",` from the appropriate
example.  You should also add the following setting:

```json
{
    "wrap_as_you_type_paragraphs": [
        {
            "first_line_regex": "^\\*$",
            "single_line": true
        }
    ]
}
```

Some people prefer to put a space after the single-line comment punctuation when
writing text comments, and not to put a space when commenting out code.  For
example:

```cpp
// This is a text comment
void foo(bool condition) {
    // This is also a text comment, but the below comments are code comments
    //if (condition) {
    //    bar1();
    //} else {
    //    bar2();
    //    bar3();
    //}
    bar4();
}
```

In this case, you would benefit by changing the appropriate `"line_start"` entry
from `"//"` to `"// "` (or from `"#"` to `"# "`, etc.).  This causes
WrapAsYouType to refrain from performing word wrapping inside of non-indented
code comments.  However, note that WrapAsYouType will identify indented code
comments as wrappable text.  In the example, it will move `bar3();` to the same
line as `bar2();`, if given the chance.  This could be considered a limitation
of WrapAsYouType.

## `"wrap_as_you_type_word_regex"`
`"wrap_as_you_type_word_regex"` is a
[Python regular expression](https://docs.python.org/3/library/re.html) used to
determine where the words are, i.e. where WrapAsYouType is allowed to insert
line breaks.  When matched against a non-empty string with no leading or
trailing whitespace, it identifies all of the words in that line of text.  We
obtain a list of non-overlapping words by scanning a line of text from beginning
to end, looking for matches.  `"wrap_as_you_type_word_regex"` defaults to
`"\\S+"`, which defines a "word" as a maximal sequence of non-whitespace
characters.

`"wrap_as_you_type_word_regex"` may match a string that has a space in it.  This
prevents WrapAsYouType from splitting that string at the internal space.

Example:

```json
{
    "wrap_as_you_type_word_regex": "[^\\s\\{]+|\\{[^\\}]*\\}?"
}
```

The above example forces WrapAsYouType to keep all text appearing between `{`
and `}` together as a single word.  It's unclear why you would want to do this,
but it's just an example.

`"wrap_as_you_type_word_regex"` may also match two words that do not have a
space between them.  In conjunction with the
`"wrap_as_you_type_space_between_words"` setting, this can be used to indicate
optional mid-"word" breaking points.

Example:

```json
{
    "wrap_as_you_type_space_between_words": [
        {
            "first_word_regex": "[^\\-]-+$",
            "space": ""
        }
    ],
    "wrap_as_you_type_word_regex": "[^\\s\\-]+-*|-+[^\\s\\-]*-*"
}
```

The above example permits WrapAsYouType to split words right after hyphens.  For
example, WrapAsYouType is permitted to break up "cookie-cutter" so that
"cookie-" appears at the end of one line and "cutter" appears at the beginning
of the next line.

`"wrap_as_you_type_word_regex"` is not permitted to produce zero-length words,
or to leave any non-whitespace characters unmatched (not part of any word).  Any
regular expression that permits this is invalid as a
`"wrap_as_you_type_word_regex"` setting.

## `"wrap_as_you_type_space_between_words"`
The `"wrap_as_you_type_space_between_words"` setting enables the user to specify
custom spacing between pairs of words.

Example:

```json
{
    "wrap_as_you_type_space_between_words": [
        {
            "first_word_regex": "^(?!e\\.g\\.|i\\.e\\.).*[.?!]$",
            "space": "  "
        }
    ]
}
```

The above example causes WrapAsYouType to put two spaces after each word ending
in a period, question mark, or exclamation mark, excluding the abbreviations
"e.g." and "i.e."

`"wrap_as_you_type_space_between_words"` is an array of objects.  Each object
has the following entries:

* `"first_word_regex"` (optional): A
  [Python regular expression](https://docs.python.org/3/library/re.html) to
  match the pre-space word against.
* `"second_word_regex"` (optional): A
  [Python regular expression](https://docs.python.org/3/library/re.html) to
  match the post-space word against.
* `"space"`: The space to use between the words, if there is a match.  This must
  consist exclusively of whitespace.

If the `"first_word_regex"` pattern matches anywhere in the pre-space word, or
the `"first_word_regex"` entry is absent, then the pre-space word matches.
Similarly for `"second_word_regex"` and the post-space word.  If both the
pre-space word and the post-space word match, then we use the `"space"` entry as
the spacing between the two words.  Note that if multiple elements of
`"wrap_as_you_type_space_between_words"` match a given pair of words, we use the
first matching element.  If no elements match, then we default to `" "`.

The `"space"` entry may be the empty string `""`, in which case no space is
added between the words.  In conjunction with the
`"wrap_as_you_type_word_regex"` setting, this can be used to indicate optional
mid-"word" breaking points.

Example:

```json
{
    "wrap_as_you_type_space_between_words": [
        {
            "first_word_regex": "[^\\-]-+$",
            "space": ""
        }
    ],
    "wrap_as_you_type_word_regex": "[^\\s\\-]+-*|-+[^\\s\\-]*-*"
}
```

The above example permits WrapAsYouType to split words right after hyphens.  For
example, WrapAsYouType is permitted to break up "cookie-cutter" so that
"cookie-" appears at the end of one line and "cutter" appears at the beginning
of the next line.

## `"wrap_as_you_type_paragraphs"`
Note: The `"wrap_as_you_type_paragraphs"` setting might be removed in a future
release; see the discussion below.

The `"wrap_as_you_type_paragraphs"` setting provides a way to identify paragraph
breaks, where these cannot be determined based on the indentation.  One possible
use case is Javadoc tags, as in the following example:

```java
public class Sqrt {
    /**
     * Computes a square root.
     * @param value The value to compute the square root of.  This must be at
     *        least 0.
     * @return The square root of "value".
     */
    public static double sqrt(double value) {
        ...
    }
}
```

In this example, the block comment has three paragraphs: one beginning with
`"Computes"`, one beginning with `"@param"`, and one beginning with `"@return"`.
Each line that begins with an `@` symbol starts a new paragraph.  We can use the
`"wrap_as_you_type_paragraphs"` setting to get WrapAsYouType to respect this
rule, as in the following example:

```json
{
    "wrap_as_you_type_paragraphs": [
        {
            "first_line_regex": "^@([a-zA-Z]+(\\s+|$)|[a-zA-Z]*$)",
            "indent_group": 0
        }
    ]
}
```

`"wrap_as_you_type_paragraphs"` is an array of objects.  Each object has the
following entries:

* `"first_line_regex"`: A
  [Python regular expression](https://docs.python.org/3/library/re.html) to
  match a line's text against.  If the pattern matches anywhere in a given
  line's text, then WrapAsYouType regards that line as the first line in a
  paragraph.  A line's "text" is given by taking the line and removing the
  section's line start, and then removing any leading and trailing whitespace.
  Note that if a line has no text, then it is never considered as part of any
  paragraph.
* `"indent"` (optional): The indentation of the lines in the paragraph after the
  first line, relative to the indentation of the first line.  This must consist
  exclusively of whitespace.  Defaults to `""`.
* `"indent_group"` (optional): The regular expression group to use to determine
  the indentation of the lines in the paragraph after the first line, relative
  to the indentation of the first line.  This can be a group number or a group
  name.  If the `"indent_group"` entry is present and the group exists as part
  of the earliest `"first_line_regex"` match, then the indentation string is the
  same as the group string, but with each character that is not a tab replaced
  with a space.  If `"indent"` and `"indent_group"` entries are both present,
  then the `"indent_group"` entry predominates.
* `"single_line"` (optional): Whether the paragraph consists of only one line:
  the line matching `"first_line_regex"`.  Defaults to false.  If
  `"single_line"` is true, then the `"indent"` and `"indent_group"` entries may
  not be present.

The above example uses an `"indent_group"` entry to specify the indentation of a
paragraph's lines after the first.  `"indent_group"` is 0.  This refers to the
group that contains the entire match, which consists of the Javadoc tag and the
following space(s).  The indentation has the same length as the match.  Thus,
the lines after a Javadoc tag are aligned with the word after the tag.

If a line of text matches multiple elements' `"first_line_regex"` patterns, then
the first matching element's indentation predominates.

While the `"wrap_as_you_type_paragraphs"` setting has some utility, it is also
somewhat problematic from a design perspective.  It doesn't offer the user a way
to describe the difference between a line that is part of an earlier paragraph
and a line that starts a new paragraph.  For example, suppose the user wants to
create bulleted lists, which consist of items that start with `"- "` and are
indented with two spaces.  If the user describes these lists using
`"wrap_as_you_type_paragraphs"`, then WrapAsYouType may interpret the middle of
a sentence that has a dash as the beginning of a bulleted list item.  In
addition, `"wrap_as_you_type_paragraphs"` only checks one line of text for
matches; it doesn't support multiline constructs.  Because of these
shortcomings, `"wrap_as_you_type_paragraphs"` might be altered or replaced with
another setting in a future release.

## `"wrap_as_you_type_disabled"`
`"wrap_as_you_type_disabled"` is a boolean indicating whether the WrapAsYouType
plugin should cease to operate.  The `"toggle_wrap_as_you_type"` command inverts
`"wrap_as_you_type_disabled"` in the current tab.

You may find that occasionally, WrapAsYouType gets in the way of what you are
trying to type.  Perhaps you are creating a diagram using ASCII art, or perhaps
your comment contains a code sample.  In these cases, it is recommended that you
use the `"toggle_wrap_as_you_type"` command to temporarily disable
WrapAsYouType.  You can bind the command to a key combination by going to the
"Preferences" > "Key Bindings" menu item.

Example:

```json
[
    {
        "command": "toggle_wrap_as_you_type",
        "keys": ["super+alt+w"]
    }
]
```

If you want to permanently disable WrapAsYouType, consider uninstalling it or
adding it to the `"ignored_packages"` setting instead.

Example:

```json
{
    "ignored_packages": ["WrapAsYouType"]
}
```

# Comparison with Auto (Hard) Wrap

WrapAsYouType is similar to the
[Auto (Hard) Wrap](https://packagecontrol.io/packages/AutoWrap) plugin in that
both automatically perform hard word wrapping as the user types.  However,
WrapAsYouType has a number of advantages over Auto (Hard) Wrap.

Advantages of WrapAsYouType over Auto (Hard) Wrap:

* Auto (Hard) Wrap does not reflow entire paragraphs.  For example, adding a
  little bit of text to the middle of a correctly flowed paragraph results in a
  nearly full line, followed by a nearly empty line, followed by a nearly full
  line.
* Auto (Hard) Wrap wraps all text, not just comments.  By contrast,
  WrapAsYouType gives users the option to only wrap comments, or even to
  configure which sections to wrap.
* Auto (Hard) Wrap does not always respect indentation.
* Auto (Hard) Wrap does not support custom line starts, such as starting each
  line in a C++ block comment with `" * "`.

Advantages of Auto (Hard) Wrap over WrapAsYouType:

* WrapAsYouType requires the user to provide special settings for each
  programming language.
* For some use cases, it may be preferable not to move text from the beginning
  of the current line to the end of the previous line, but only to perform
  forward-looking word wrapping.
