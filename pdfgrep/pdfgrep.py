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
import pdftotext
import magic


APP_NAME = sys.argv[0].split('/')[-1]

def main():
    """
    Main function, fetch command line arguments and call do_grep with given
    attibutes
    """

    parser = argparse.ArgumentParser('grep pdf files')
    parser.add_argument('-q', '--quiet', required=False,
                        action='store_true', default=False,
                        help='suppress error messages')
    parser.add_argument('-i', '--ignore-case', required=False,
                        action='store_true', default=False,
                        help='ignore case')
    parser.add_argument('-r', '--recursive', required=False,
                        action='store_true', default=False,
                        help='Read files under each directory, recursively')
    parser.add_argument('-l', '--list-files', required=False,
                        action='store_true', default=False,
                        help='list files matching pattern')
    parser.add_argument('-c', '--colour', '--color', required=False, dest='color',
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
        try:
            for output in \
                do_grep(filename, args.grep, ignore_case=args.ignore_case,
                        num=args.num, list_files=args.list_files,
                        recursive=args.recursive, color=args.color,
                        suppress_errors=args.suppress_errors):
                print(output)
        except KeyboardInterrupt:
            sys.exit(1)

def do_grep(filename, grep, **kwargs):
    """ Perform the pattern matching in given files """

    for arg in ['ignore_case', 'list_files', 'num', 'recursive', 'color', 'suppress_errors']:
        kwargs.setdefault(arg, False)

    def write_error(message):
        """Print given message to stderr if not suppressed"""
        if not kwargs['suppress_errors']:
            sys.stderr.write(message)

    # set ignore case flag
    re.IGNORECASE = 0 if not kwargs['ignore_case'] else 2

    # recurse through directory structure if filename is a dir
    if os.path.isdir(filename) and kwargs['recursive'] is True:
        for r_file in glob(filename + '/*'):
            for output in \
                do_grep(r_file, grep, ignore_case=kwargs['ignore_case'],
                        list_files=kwargs['list_files'],
                        num=kwargs['num'], recursive=kwargs['recursive'],
                        color=kwargs['color'], suppress_errors=kwargs['suppress_errors']):

                print(output)
        return

    elif os.path.isdir(filename) and kwargs['recursive'] is False:
        # ignore directory and return if recursive flag is not set
        return
    elif not os.path.isfile(filename):
        write_error("{0}: {1}: No such file or directory\n"
                    .format(APP_NAME, filename))
        return

    elif magic.from_file(filename, mime=True) != 'application/pdf':
        write_error("{0}: Not a pdf file: {1}\n "
                    .format(APP_NAME, filename))
        return

    try:
        pdf_file = open(filename, 'rb')
    except IOError:
        write_error("{0}: {1}: No such file or directory\n"
                    .format(APP_NAME, filename))
        return

    try:
        read_pdf = pdftotext.PDF(pdf_file)

        # This will happen if file is malformed, or not a PDF
    except (pdftotext.Error, IOError):
        write_error("{0}: Unable to read file: {1}\n "
                    .format(APP_NAME, filename))
        return

    for page_num, _ in enumerate(read_pdf):
        # attempt to read pages and split lines approprietly
        page = read_pdf[page_num]
        page_content = page.split('\n')

        # iterate through pages
        for line_num, line in enumerate(page_content):
            line = str(line.encode('utf-8'))
            if re.search(grep, line, re.IGNORECASE):
                if kwargs['list_files']:
                    # only print file names - return after first match found
                    yield filename
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

                yield "{0}: {1} {2}".format(filename, beg, line.strip())

if __name__ == '__main__':
    main()
