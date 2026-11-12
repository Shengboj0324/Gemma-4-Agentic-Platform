"""Licence detection must refuse to guess, and must separate the lookalikes."""

import unittest

from zenithsync.rights_review import (ABSENT, CONFIRMED, COPYLEFT,
                                      INDETERMINATE,
                                      KNOWN_FAMILIES, LICENCE_FILENAMES,
                                      LICENCE_DIRECTORIES, MISMATCH,
                                      detect_copyleft, detect_families,
                                      normalise,
                                      review_observation, summarise)

MIT = """MIT License

Copyright (c) 2024 Example

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""

MIT_ZERO = """MIT No Attribution

Copyright (c) 2024 Example

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files, to deal in the Software
without restriction.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"""

BSD3 = """Copyright (c) 2024 Example

Redistribution and use in source and binary forms are permitted provided that
the following conditions are met:

1. Redistributions of source code must retain the above copyright notice.
2. Redistributions in binary form must reproduce the above copyright notice.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS".
"""

BSD2 = """Copyright (c) 2024 Example

Redistribution and use in source and binary forms are permitted provided that
the following conditions are met:

1. Redistributions of source code must retain the above copyright notice.
2. Redistributions in binary form must reproduce the above copyright notice.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS".
"""

APACHE = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/LICENSE-2.0

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
"""

ISC = """Copyright (c) 2024 Example

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted.
"""

UNLICENSE = """This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary.
"""


class DetectionTests(unittest.TestCase):
    def test_each_family_is_detected_as_exactly_itself(self):
        for text, family in ((MIT, 'MIT'), (MIT_ZERO, 'MIT-0'),
                             (BSD3, 'BSD-3-Clause'), (BSD2, 'BSD-2-Clause'),
                             (APACHE, 'Apache-2.0'), (ISC, 'ISC'),
                             (UNLICENSE, 'Unlicense')):
            with self.subTest(family=family):
                self.assertEqual(detect_families(text), [family])

    def test_mit_and_mit_zero_are_not_confused(self):
        # MIT-0 is MIT without the notice-retention clause. Detecting one as
        # the other would silently change the obligations that follow.
        self.assertNotIn('MIT-0', detect_families(MIT))
        self.assertNotIn('MIT', detect_families(MIT_ZERO))

    def test_bsd_two_and_three_clause_are_not_confused(self):
        self.assertNotIn('BSD-2-Clause', detect_families(BSD3))
        self.assertNotIn('BSD-3-Clause', detect_families(BSD2))

    def test_formatting_differences_do_not_change_the_family(self):
        rewrapped = ' '.join(MIT.split())
        smart = MIT.replace('"', '“', 1)
        indented = '\n'.join('    ' + line for line in MIT.splitlines())
        for variant in (rewrapped, smart, indented, MIT.encode('utf-8')):
            with self.subTest():
                self.assertEqual(detect_families(variant), ['MIT'])

    def test_unrelated_text_matches_nothing(self):
        self.assertEqual(detect_families('All rights reserved. Do not copy.'), [])

    def test_normalise_rejects_a_non_text_value(self):
        with self.assertRaises(TypeError):
            normalise(42)


class ObservationTests(unittest.TestCase):
    def test_a_matching_text_is_confirmed(self):
        row = review_observation('MIT', MIT, path='LICENSE')
        self.assertEqual(row['outcome'], CONFIRMED)
        self.assertEqual(row['detected'], ['MIT'])
        self.assertEqual(row['path'], 'LICENSE')

    def test_a_different_family_is_a_mismatch_not_a_pass(self):
        row = review_observation('MIT', APACHE, path='LICENSE')
        self.assertEqual(row['outcome'], MISMATCH)
        self.assertIn('Apache-2.0', row['reason'])

    def test_no_file_is_absent_and_distinct_from_indeterminate(self):
        self.assertEqual(review_observation('MIT', None)['outcome'], ABSENT)
        self.assertEqual(
            review_observation('MIT', 'unrecognised')['outcome'], INDETERMINATE)

    def test_a_text_matching_two_families_is_never_resolved_permissively(self):
        both = MIT + '\n' + APACHE
        row = review_observation('MIT', both, path='LICENSE')
        self.assertEqual(row['outcome'], INDETERMINATE)
        self.assertIn('more than one family', row['reason'])

    def test_a_label_outside_the_known_families_is_refused(self):
        for label in ('GPL-3.0', 'custom-check-github', '', None):
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, 'not a known family'):
                    review_observation(label, MIT)


class SummaryTests(unittest.TestCase):
    def rows(self):
        return [
            {'instance_id': 'a__b-1', 'repo': 'a/b', 'base_commit': 'c' * 40,
             **review_observation('MIT', MIT, path='LICENSE')},
            {'instance_id': 'a__b-2', 'repo': 'a/b', 'base_commit': 'd' * 40,
             **review_observation('MIT', APACHE, path='LICENSE')},
            {'instance_id': 'e__f-1', 'repo': 'e/f', 'base_commit': 'f' * 40,
             **review_observation('ISC', None)},
        ]

    def test_only_confirmed_rows_are_eligible(self):
        summary = summarise(self.rows())
        self.assertEqual(summary['eligible_tasks'], 1)
        self.assertEqual(summary['withheld_tasks'], 2)
        self.assertEqual(summary['outcome_counts'][CONFIRMED], 1)
        self.assertEqual(summary['outcome_counts'][MISMATCH], 1)
        self.assertEqual(summary['outcome_counts'][ABSENT], 1)

    def test_every_withheld_task_is_named_with_its_reason(self):
        summary = summarise(self.rows())
        named = {row['instance_id'] for row in summary['withheld']}
        self.assertEqual(named, {'a__b-2', 'e__f-1'})
        for row in summary['withheld']:
            self.assertTrue(row['reason'])

    def test_the_summary_never_claims_rights_are_cleared(self):
        summary = summarise(self.rows())
        self.assertFalse(summary['rights_cleared'])
        for word in ('vendored', 'contributor', 'Not legal clearance'):
            self.assertIn(word, summary['scope'])

    def test_an_unknown_outcome_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'Unknown review outcome'):
            summarise([{'outcome': 'probably_fine'}])

    def test_an_empty_review_is_refused(self):
        for value in ([], None, {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    summarise(value)


class SurfaceTests(unittest.TestCase):
    def test_the_allowed_families_match_what_the_pool_screened_on(self):
        self.assertEqual(set(KNOWN_FAMILIES),
                         {'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC',
                          'MIT', 'MIT-0', 'Unlicense'})

    def test_every_candidate_path_is_in_an_allowed_licence_directory(self):
        # Widening the filename list must not start reading a licence out of a
        # vendored dependency's subtree and calling it the repository's.
        for name in LICENCE_FILENAMES:
            directory = name.rsplit('/', 1)[0] + '/' if '/' in name else ''
            with self.subTest(name=name):
                self.assertIn(directory, LICENCE_DIRECTORIES)

    def test_the_astropy_licence_directory_convention_is_covered(self):
        self.assertIn('licenses/LICENSE.rst', LICENCE_FILENAMES)

    def test_root_paths_are_tried_before_any_licence_directory(self):
        first_nested = min(index for index, name in enumerate(LICENCE_FILENAMES)
                           if '/' in name)
        last_root = max(index for index, name in enumerate(LICENCE_FILENAMES)
                        if '/' not in name)
        self.assertGreater(first_nested, last_root)


#: The real header of the canonical Apache-2.0 file. The LICENSE-2.0 URL that an
#: over-specific marker once required appears only in the appendix boilerplate,
#: which many projects strip — PyCQA/bandit at its pinned commit is one.
APACHE_CANONICAL_HEADER = """
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.
"""

#: botocore ships only the short grant notice, pointing at Amazon's mirror
#: rather than apache.org. The file states its own licence; reading it is an
#: observation, not an inference.
APACHE_SHORT_FORM = """Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You
may not use this file except in compliance with the License. A copy of
the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file.
"""


class ApacheFormTests(unittest.TestCase):
    """Both shipped forms of Apache-2.0 must be recognised as Apache-2.0."""

    def test_the_canonical_header_without_the_appendix_url_is_apache(self):
        self.assertEqual(detect_families(APACHE_CANONICAL_HEADER),
                         ['Apache-2.0'])
        self.assertEqual(
            review_observation('Apache-2.0', APACHE_CANONICAL_HEADER,
                               path='LICENSE')['outcome'], CONFIRMED)

    def test_the_short_grant_notice_is_apache(self):
        self.assertEqual(detect_families(APACHE_SHORT_FORM), ['Apache-2.0'])
        self.assertEqual(
            review_observation('Apache-2.0', APACHE_SHORT_FORM,
                               path='LICENSE.txt')['outcome'], CONFIRMED)

    def test_neither_form_is_mistaken_for_another_family(self):
        for text in (APACHE_CANONICAL_HEADER, APACHE_SHORT_FORM):
            with self.subTest():
                self.assertEqual(detect_families(text), ['Apache-2.0'])

    def test_a_bare_mention_of_apache_is_not_a_grant(self):
        # Naming the licence is not granting it; a README-ish mention must not
        # confirm anything.
        for text in ('See the Apache License for details.',
                     'This project is similar to Apache 2.0 licensed work.',
                     'Apache License'):
            with self.subTest(text=text):
                self.assertEqual(detect_families(text), [])


GPL3 = """                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for software.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have permission to
link or combine any covered work with a work licensed under version 3 of the
GNU Affero General Public License into a single combined work.

  If your program is a subroutine library, you may consider it more useful to
permit linking proprietary applications with the library. If this is what you
want to do, use the GNU Lesser General Public License instead of this License.
"""

LGPL3 = """                   GNU LESSER GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc.

  This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License.
"""

AGPL3 = """                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>

  The GNU Affero General Public License is a free, copyleft license. This
version of the GNU General Public License is based on it.
"""

MPL2 = """Mozilla Public License Version 2.0
==================================
"""


class CopyleftTests(unittest.TestCase):
    """A permissive label over copyleft text is the case worth shouting about.

    GridTools/gt4py and SciTools/cartopy are both labelled BSD-3-Clause in the
    pool metadata and both carry GPL-3.0 text at their pinned commits. Reporting
    that as "matches no known family" buries it among detection gaps.
    """

    def test_gpl_under_a_permissive_label_is_its_own_outcome(self):
        row = review_observation('BSD-3-Clause', GPL3, path='LICENSE.txt')
        self.assertEqual(row['outcome'], COPYLEFT)
        self.assertEqual(row['detected'], ['GPL-3.0'])
        self.assertIn('BSD-3-Clause', row['reason'])

    def test_each_copyleft_family_is_detected_as_exactly_itself(self):
        for text, family in ((GPL3, 'GPL-3.0'), (LGPL3, 'LGPL-3.0'),
                             (AGPL3, 'AGPL-3.0'), (MPL2, 'MPL-2.0')):
            with self.subTest(family=family):
                self.assertEqual(detect_copyleft(text), [family])

    def test_lesser_and_affero_are_not_read_as_plain_gpl(self):
        # All three contain "GENERAL PUBLIC LICENSE"; conflating them would
        # misstate the obligations.
        for text in (LGPL3, AGPL3):
            with self.subTest():
                self.assertNotIn('GPL-3.0', detect_copyleft(text))

    def test_permissive_texts_are_not_flagged_as_copyleft(self):
        for text in (MIT, MIT_ZERO, BSD2, BSD3, APACHE, ISC, UNLICENSE):
            with self.subTest():
                self.assertEqual(detect_copyleft(text), [])

    def test_copyleft_is_never_confirmable_even_if_declared(self):
        # KNOWN_FAMILIES holds only permissive labels, so a copyleft label
        # cannot be screened in, and copyleft text cannot be confirmed.
        self.assertNotIn('GPL-3.0', KNOWN_FAMILIES)
        for declared in KNOWN_FAMILIES:
            with self.subTest(declared=declared):
                self.assertEqual(
                    review_observation(declared, GPL3)['outcome'], COPYLEFT)

    def test_a_gpl3_file_citing_section_13_is_not_read_as_agpl(self):
        """GPL-3.0 section 13 names the Affero licence; that is not a grant.

        GridTools/gt4py and SciTools/cartopy are GPL-3.0 and each says "GNU
        Affero General Public License" three times for this reason. An earlier
        marker table keyed on the name reported both as AGPL-3.0.
        """
        self.assertIn('Affero', GPL3)
        self.assertEqual(detect_copyleft(GPL3), ['GPL-3.0'])

    def test_a_gpl3_file_recommending_the_lesser_gpl_is_not_read_as_lgpl(self):
        """GPL-3.0's closing advice names the Lesser GPL. That is not a title.

        gt4py and cartopy both carry GPL-3.0's full text, which contains the
        Lesser name once for this reason. A marker keyed on the name read both
        as LGPL-3.0.
        """
        self.assertIn('GNU Lesser General Public License', GPL3)
        self.assertEqual(detect_copyleft(GPL3), ['GPL-3.0'])

    def test_an_agpl_file_citing_the_gpl_is_not_read_as_gpl(self):
        self.assertIn('GNU General Public License', AGPL3)
        self.assertEqual(detect_copyleft(AGPL3), ['AGPL-3.0'])

    def test_an_lgpl3_file_incorporating_gpl3_terms_stays_lgpl(self):
        # The LGPL-3.0 document carries GPL-3.0's own date line.
        self.assertIn('Version 3, 29 June 2007', LGPL3)
        self.assertEqual(detect_copyleft(LGPL3), ['LGPL-3.0'])

    def test_copyleft_rows_are_withheld_and_counted(self):
        rows = [{'instance_id': 'g__t-1', 'repo': 'GridTools/gt4py',
                 'base_commit': 'a' * 40,
                 **review_observation('BSD-3-Clause', GPL3, path='LICENSE.txt')}]
        summary = summarise(rows)
        self.assertEqual(summary['eligible_tasks'], 0)
        self.assertEqual(summary['outcome_counts'][COPYLEFT], 1)
        self.assertEqual(summary['withheld'][0]['instance_id'], 'g__t-1')


class TitleLineTests(unittest.TestCase):
    """A licence is identified by its own heading, never by a mention of it."""

    def test_naming_a_family_without_its_version_line_identifies_nothing(self):
        # A licence file that cites another family's *name* must not be read as
        # that family. This is what GPL-3.0's references to the Affero and
        # Lesser licences are.
        for text in ('Compatible with the Apache License, Version 2.0.',
                     'Not the GNU Affero General Public License.',
                     'See the GNU Lesser General Public License for details.',
                     'Released under the GNU General Public License.'):
            with self.subTest(text=text):
                self.assertEqual(detect_copyleft(text), [])
                self.assertEqual(detect_families(text), [])

    def test_prose_that_states_the_full_title_is_treated_as_stating_it(self):
        """Quoting title and version line is a file declaring its own licence.

        Contiguous matching cannot separate a heading from a sentence that
        reproduces the whole title, and it should not try: a licence file saying
        "under the GNU General Public License version 3, 29 June 2007" is
        stating its terms, exactly as botocore's short Apache notice states
        its own. For copyleft the consequence is a withheld task, which is the
        conservative direction; the dangerous error would be the reverse.
        """
        prose = ('This work is distributed under the GNU General Public '
                 'License version 3, 29 June 2007.')
        self.assertEqual(detect_copyleft(prose), ['GPL-3.0'])
        self.assertEqual(review_observation('MIT', prose,
                                            path='LICENSE')['outcome'],
                         COPYLEFT)

    def test_each_gnu_heading_is_unique_to_its_family(self):
        headings = {
            'GPL-3.0': 'GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007',
            'GPL-2.0': 'GNU GENERAL PUBLIC LICENSE Version 2, June 1991',
            'LGPL-3.0': 'GNU LESSER GENERAL PUBLIC LICENSE Version 3, 29 June 2007',
            'LGPL-2.1': 'GNU LESSER GENERAL PUBLIC LICENSE Version 2.1, February 1999',
            'AGPL-3.0': 'GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007',
        }
        for family, heading in headings.items():
            with self.subTest(family=family):
                self.assertEqual(detect_copyleft(heading), [family])

    def test_a_file_carrying_two_headings_reports_both(self):
        # The LGPL convention ships its own notice beside GPL's full text.
        both = ('GNU LESSER GENERAL PUBLIC LICENSE Version 3, 29 June 2007\n'
                'GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007\n')
        self.assertEqual(detect_copyleft(both), ['GPL-3.0', 'LGPL-3.0'])
        row = review_observation('MIT', both, path='COPYING')
        self.assertEqual(row['outcome'], COPYLEFT)
        self.assertEqual(row['detected'], ['GPL-3.0', 'LGPL-3.0'])


if __name__ == '__main__':
    unittest.main()
