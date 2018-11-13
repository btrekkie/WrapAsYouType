import unittest

from WrapAsYouType.section import Section


class TestSection(unittest.TestCase):
    def _matches(self, scope, rule_set):
        """Return whether "scope" matches rule_set, according to Section.

        Construct a new Section with the specified selector rule set,
        and whether "scope" matches the rule set, according to the
        section's matches_selector_rules method.

        str scope - The scope to test.
        object rule_set - The selector rule set.
        return bool - Whether the scope matches.
        """
        section = Section(None, [''], rule_set, None)
        return section.matches_selector_rules(scope)

    def test_matches_selector_rules_str(self):
        """Test Section.matches_selector_rules on string rule sets."""
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                'comment.block'))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                'keyword.control'))
        self.assertFalse(self._matches('', 'comment.block'))
        self.assertTrue(self._matches('comment.block.c', 'comment.block'))

    def test_matches_selector_rules_list(self):
        """Test Section.matches_selector_rules on list rule sets."""
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                ['meta.block.c++']))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                ['comment.block', 'keyword.control', 'string.quoted.double']))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                ['keyword.control', 'string.quoted.double', 'comment.block']))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    'string.quoted.double',
                    'entity.name.class',
                ]))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    ['string.quoted.double', 'comment.block'],
                ]))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    ['string.quoted.double', 'entity.class.name'],
                ]))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                []))
        self.assertFalse(
            self._matches(
                '',
                ['comment.block', 'keyword.control', 'string.quoted.double']))
        self.assertFalse(self._matches('', []))

    def test_matches_selector_rules_not(self):
        """Test Section.matches_selector_rules on rule sets with nots."""
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'not': 'comment.block'}))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'not': 'keyword.control'}))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': [
                        'keyword.control',
                        'comment.block',
                        'string.quoted.double',
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': [
                        'keyword.control',
                        'string.quoted.double',
                        'entity.class.name',
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    {'not': 'string.quoted.double'},
                    'entity.class.name',
                ]))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    {'not': 'comment.block'},
                    'entity.class.name',
                ]))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', [
                    'keyword.control',
                    {'not': {'not': 'comment.block'}},
                    'entity.class.name',
                ]))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': [
                        'keyword.control',
                        {'not': {'not': 'comment.block'}},
                        'entity.class.name',
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'not': []}))
        self.assertTrue(self._matches('', {'not': 'comment.block'}))
        self.assertTrue(self._matches('', {'not': []}))

    def test_matches_selector_rules_and(self):
        """Test Section.matches_selector_rules on rule sets with ands."""
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'and': ['source', 'comment.block']}))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'and': ['keyword.control', 'comment.block']}))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'and': [['keyword.control', 'comment.block']]}))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'and': [{'not': 'keyword.control'}, 'comment.block']}))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'and': []}))
        self.assertFalse(
            self._matches('', {'and': ['keyword.control', 'comment.block']}))
        self.assertTrue(self._matches('', {'and': []}))
        self.assertFalse(
            self._matches(
                'comment.block.c',
                {'and': ['keyword.control', 'comment.block']}))
        self.assertTrue(
            self._matches('comment.block.c', {'and': ['comment.block']}))

    def test_matches_selector_rules_or(self):
        """Test Section.matches_selector_rules on rule sets with ors."""
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'or': ['meta.block.c++']}))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'or': [
                        'comment.block',
                        'keyword.control',
                        'string.quoted.double',
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'or': [
                        'keyword.control',
                        'string.quoted.double',
                        'comment.block',
                    ],
                }))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'or': [
                        'keyword.control',
                        'string.quoted.double',
                        'entity.name.class',
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'or': [
                        'keyword.control',
                        ['string.quoted.double', 'comment.block'],
                    ],
                }))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'or': [
                        'keyword.control',
                        ['string.quoted.double', 'entity.class.name'],
                    ],
                }))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c',
                {'or': []}))
        self.assertFalse(
            self._matches(
                '', {
                    'or': [
                        'comment.block',
                        'keyword.control',
                        'string.quoted.double',
                    ]
                }))
        self.assertFalse(self._matches('', {'or': []}))

    def test_matches_selector_rules_nested(self):
        """Test Section.matches_selector_rules on nested rule sets.

        Test Section.matches_selector_rules on complex rule sets with a
        bunch of nesting.
        """
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'and': [
                        ['meta.block.c++', 'keyword.control'],
                        ['string.quoted.double', {'not': 'source'}],
                    ],
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'and': [
                        ['meta.block.c++', 'keyword.control'],
                        [{'not': 'string.quoted.double'}, {'not': 'source'}],
                    ],
                }))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': {
                        'and': [
                            ['meta.block.c++', 'keyword.control'],
                            [
                                {'not': 'string.quoted.double'},
                                {'not': 'source'},
                            ],
                        ],
                    },
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': {
                        'and': [
                            ['meta.block.c++', 'keyword.control'],
                            {
                                'not': [
                                    {'not': 'string.quoted.double'},
                                    {'not': 'source'},
                                ],
                            },
                        ],
                    },
                }))
        self.assertTrue(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': [
                        {
                            'and': ['comment', 'string.quoted.double'],
                        },
                        {
                            'and': [
                                'source.c++',
                                'comment.block',
                                'keyword.control',
                            ],
                        }
                    ],
                }))
        self.assertFalse(
            self._matches(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c', {
                    'not': [
                        {
                            'and': [
                                'comment',
                                {'not': 'string.quoted.double'},
                            ],
                        },
                        {
                            'and': [
                                'source.c++',
                                'comment.block',
                                'keyword.control',
                            ],
                        }
                    ],
                }))
        self.assertTrue(
            self._matches(
                '', {
                    'not': [
                        {
                            'and': [
                                'comment',
                                {'not': 'string.quoted.double'},
                            ],
                        },
                        {
                            'and': [
                                'source.c++',
                                'comment.block',
                                'keyword.control',
                            ],
                        }
                    ],
                }))
        self.assertFalse(
            self._matches(
                '', {
                    'not': [
                        {
                            'and': [
                                {'not': 'comment'},
                                {'not': 'string.quoted.double'},
                            ],
                        },
                        {
                            'and': [
                                'source.c++',
                                'comment.block',
                                'keyword.control',
                            ],
                        }
                    ],
                }))

    def test_matches_combining_selector_rules(self):
        section = Section(
            None, [''], 'comment.block',
            ['keyword.control', 'string.quoted.double'])
        self.assertFalse(
            section.matches_combining_selector_rules(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c'))
        self.assertTrue(
            section.matches_combining_selector_rules('keyword.control'))
        self.assertFalse(section.matches_combining_selector_rules(''))

        section = Section(
            None, [''], {'and': ['string.quoted.double', 'comment.block']}, {
                'not': [
                    {'and': ['keyword.control', 'source.c++']},
                    'string.quoted.double',
                ],
            })
        self.assertTrue(
            section.matches_combining_selector_rules(
                'source.c++ meta.class.c++ meta.block.c++ comment.block.c'))
        self.assertTrue(section.matches_combining_selector_rules(''))
