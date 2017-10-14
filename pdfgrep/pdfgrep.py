#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

"""
PDF grepping tool
Search for string pattern in given PDF if contains text.
Use pypdfocr to convert image pdf to text-based without altering layout

Example usage:
    pdfgrep.py -irl Bank *.pdf
"""


from __future__ import print_function

__author__ = "Amro Diab"
__author_email__ = "adiab@linuxmail.org"


import argparse
import os
import re
import sys

from glob import glob
import argcomplete
import PyPDF2

APP_NAME = sys.argv[0].split('/')[-1]

def main():
    """
    Main function, fetch command line arguments and call do_grep with given
    attibutes
    """

    parser = argparse.ArgumentParser('grep pdf files')
    parser.add_argument('-i', '--ignore-case', required=False,
                        action='store_true', default=False,
                        help='ignore case')
    parser.add_argument('-r', '--recursive', required=False,
                        action='store_true', default=False,
                        help='Read files under each directory, recursively')
    parser.add_argument('-l', '--list-files', required=False,
                        action='store_true', default=False,
                        help='list files matching pattern')
    parser.add_argument('--color', '--colour', required=False,
                        action='store_true', help='color the matched string')
    parser.add_argument('-n', '--num', required=False,
                        action='store_true', default=False,
                        help='display page and line numbers')
    parser.add_argument('grep', action="store")
    parser.add_argument('filenames', action="store", nargs='*')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not args.filenames:
        args.filenames = sorted(glob('*'))
    for filename in args.filenames:
        do_grep(filename, args.grep, ignore_case=args.ignore_case,
                num=args.num, list_files=args.list_files,
                recursive=args.recursive, color=args.color)

def do_grep(filename, grep, **kwargs):
    """ Perform the pattern matching in given files """

    for arg in ['ignore_case', 'list_files', 'num', 'recursive', 'color']:
        kwargs.setdefault(arg, False)

    # set ignore case flag
    re.IGNORECASE = 0 if not kwargs['ignore_case'] else 2

    # recurse through directory structure if filename is a dir
    if os.path.isdir(filename) and kwargs['recursive'] is True:
        for r_file in glob(filename + '/*'):
            do_grep(r_file, grep, ignore_case=kwargs['ignore_case'],
                    list_files=kwargs['list_files'],
                    num=kwargs['num'], recursive=kwargs['recursive'],
                    color=kwargs['color'])
        return

    elif os.path.isdir(filename) and kwargs['recursive'] is False:
        # ignore directory and return if recursive flag is not set
        return

    try:
        pdf_file = open(filename, 'rb')
    except IOError:
        sys.stderr.write("{0}: {1}: No such file or directory\n"
                         .format(APP_NAME, filename))
        return

    try:
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        # This will happen if file is malformed, or not a PDF
    except (PyPDF2.utils.PdfReadError, IOError):
        sys.stderr.write("{0}: Unable to read file: {1}\n "
                         .format(APP_NAME, filename))
        return

    pages = []

    for page_num in range(0, read_pdf.getNumPages()):
        # attempt to read pages and split lines approprietly
        page = read_pdf.getPage(page_num)
        page_content = page.extractText() + '\n'
        page_content = " ".join(page_content.replace(u"\xa0", " ")
                                .strip().split())
        pages.append(page_content.encode("ascii", "xmlcharrefreplace"))

        # iterate through pages
        for line_num, line in enumerate(pages):
            line = line.decode('utf-8')
            if re.search(grep, line, re.IGNORECASE):
                if kwargs['list_files']:
                    # only print file names - return after first match found
                    print(filename)
                    return
                # add page and line numbers if num flag set
                beg = ("page:{0}, line:{1}"
                       .format(page_num + 1, line_num + 1) if kwargs['num'] else "")

                if kwargs['color']:
                    # highlight matching text in red
                    red = '\033[31m'
                    end = '\033[0m'
                    text = re.compile(re.escape(grep), re.IGNORECASE)
                    line = text.sub(red + grep + end, line)

                print("{0}: {1} {2}".format(filename, beg, line))

if __name__ == '__main__':
    main()
