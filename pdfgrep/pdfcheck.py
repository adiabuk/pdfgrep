#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

"""
PDF checking tool
Check if file(s) is a valid PDF and contains parsable text

Example usage:
    pdfcheck.py -r .
"""


from __future__ import print_function

__author__ = "Amro Diab"
__author_email__ = "adiab@linuxmail.org"


import argparse
import os

from glob import glob
import argcomplete
import magic
import pdftotext


def main():
    """
    Main function, fetch command line arguments and call do_grep with given
    attibutes
    """

    parser = argparse.ArgumentParser('check pdf files')
    parser.add_argument('-r', '--recursive', required=False,
                        action='store_true', default=False,
                        help='Read files under each directory, recursively')
    parser.add_argument('filenames', action="store", nargs='*')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not args.filenames:
        args.filenames = sorted(glob('*'))
    for filename in args.filenames:
        for output in do_check(filename, recursive=args.recursive):
            print(output)

def do_check(filename, recursive=False):
    """ check given file(s) for text """

    # recurse through directory structure if filename is a dir
    if os.path.isdir(filename) and recursive is True:
        for r_file in glob(filename + '/*'):
            for output in do_check(r_file, recursive=recursive):
                print(output)
        return

    elif os.path.isdir(filename) and recursive is False:
        # ignore directory and return if recursive flag is not set
        return
    elif not os.path.isfile(filename):
        string = "{0}: No such file or directory" .format(filename)
        yield get_status(string, success=False)
        return

    elif magic.from_file(filename, mime=True) != 'application/pdf':
        string = "{0}: Not a pdf file".format(filename)
        yield get_status(string, success=False)
        return

    try:
        pdf_file = open(filename, 'rb')
    except IOError:
        string = "{0}: No such file or directory".format(filename)
        yield get_status(string, success=False)
        return

    try:
        read_pdf = pdftotext.PDF(pdf_file)
        # This will happen if file is malformed, or not a PDF
    except (pdftotext.Error, IOError):
        string = "{0}: Unable to read file".format(filename)
        yield get_status(string, success=False)
        return
    except KeyboardInterrupt:
        return

    pages = ''.join(read_pdf)

    if pages:
        string = "{0}: valid OCR PDF".format(filename)
        success = True
    else:
        string = "{0}: No readable text content".format(filename)
        success = False

    yield get_status(string, success)

def get_status(string, success):
    """ Print status of file check: OK/FAILED """

    bold = '\033[1m'
    green = '\033[92m'
    red = '\033[31m'
    end = '\033[0m'

    status = green + "  OK  " if success else red + 'FAILED'
    status_block = (bold + '[ ' + status + end + bold
                    + ' ]' + end)
    _, columns = os.popen('stty size', 'r').read().split()
    spaces = ' ' * (int(columns) - len(status) - len(string))
    return '{0}{1}{2}'.format(string, spaces, status_block)

if __name__ == '__main__':
    main()
