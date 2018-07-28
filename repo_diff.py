#!/usr/bin/env python
# filename: repo_diff.py
#
# desc: It will compare initial repo template and latest repo template and
# write differences into html.
#

import sys
import difflib

diff1 = "repoTemplate.txt"
diff2 = "repoTemplate_newer.txt"
diff_html = "repoDiff.html"


def diff_u(text1_lines, text2_lines):
    """Show only includes modified lines and a bit of context"""
    diff = difflib.unified_diff(
        text1_lines,
        text2_lines,
        lineterm='',
    )
    print('\n'.join(diff))


def diff_h(text1_lines, text2_lines):
    """Produces HTML output with the different information into Diff file"""
    d = difflib.HtmlDiff()
    result = d.make_file(text1_lines, text2_lines)
    try:
        with open(diff_html, "w+") as result_file:
            result_file.write(result)
            print("Write diff into {0} successfully".format(diff_html))
    except IOError as error:
        print('Error writing HTML file: {0}'.format(error))


def read_file(filename):
    """Return a list of the lines in the string, breaking at line boundaries"""
    try:
        with open(filename, 'r+') as fileHandle:
            text = fileHandle.read().splitlines()
        return text
    except IOError as error:
        print('Read file Error:' + str(error))
        sys.exit(1)


def main_proc():
    # write diff into html
    diff_1 = read_file(diff1)
    diff_2 = read_file(diff2)
    diff_h(diff_1, diff_2)

    # output diff to stdout
    # diff_u(read_file(diff1), read_file(diff2))


if __name__ == '__main__':
    main_proc()
