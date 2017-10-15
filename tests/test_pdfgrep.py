#!/usr/bin/env python

"""
Unit tests for pdfgrep
"""

import unittest
import pdfgrep.pdfgrep as grep

class TestPdfgrep(unittest.TestCase):
    """ pdfgrep test class """

    def test_lines(self):
        """ test number of lines from grep """

        gen = grep.do_grep('tests/pdfs/ImageOnly_ocr.pdf',
                           'This is a', ignore_case=True)
        outputs = [output for output in gen]

        self.assertEqual(len(outputs), 16)

    def test_files(self):
        """ test number of files from grep """

        gen = grep.do_grep('tests/pdfs/ImageOnly_ocr.pdf',
                           'This is a', ignore_case=True, list_files=True)
        outputs = [output for output in gen]
        self.assertEqual(len(outputs), 1)
