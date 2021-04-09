import os
import sys
import argparse
import gzip
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['figure.figsize'] = [10.0, 6.0]
matplotlib.rcParams['figure.dpi'] = 80
'''

    James M. Ferguson (j.ferguson@garvan.org.au)
    Genomic Technologies
    Garvan Institute
    Copyright 2021



    ----------------------------------------------------------------------------
    version 0.0 - initial



    TODO:
        -

    ----------------------------------------------------------------------------
    MIT License

    Copyright (c) 2021 James Ferguson

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
'''


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    '''
    main func directing which plots to make
    '''
    VERSION = "0.0.1"
    NAME = "interArtic plots"
    parser = MyParser(
        description="Plots for interArtic",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subcommand = parser.add_subparsers(help='subcommand --help for help messages', dest="command")

    # main options for base level checks and version output
    parser.add_argument("--version", action='version', version="{} version: {}".format(NAME, VERSION),
                        help="Prints version")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Verbose output [v/vv/vvv]")

    # sub-module for vcf ploter
    vcf = subcommand.add_parser('vcf', help='plots vcf variants',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    vcf.add_argument("-v", "--vcf_file",
                        help="full path to vcf file")

    # sub-module for coverage ploter
    cov = subcommand.add_parser('cov', help='plots coverage',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cov.add_argument("-d", "--depth_file", nargs='+',
                        help="full path to depth file")


    args = parser.parse_args()

    # print help if no arguments given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.command == "vcf":
        vcf_pipeline(args)
    elif args.command == "cov":
        cov_pipeline(args)
    else:
        sys.stderr.write("Command unknown: {}".format(args.command))
        parser.print_help(sys.stderr)
        sys.exit(1)


def vcf_pipeline(args):
    """
    Plot vcf histogram
    x-axis = genome
    y-axis = depth
    each bar represents a variant, anotated
    Add genes/orfs/annoation to bottom (or maybe even top?) of plot for context
    """
    data = []
    x = []
    y = []
    header = []
    row = {}
    with gzip.open(args.vcf_file, 'rt') as f:
        for l in f:
            if l[0] == "##":
                continue
            if l[0] == "#":
                l = l[1:].strip('\n')
                l = l[1:].split('\t')
                header = l
                continue

            l = l.strip('\n')
            l = l.split('\t')
            row = dict(zip(header, l))
            x.append(int(row["POS"]))
            y.append(int(row["INFO"].split(";")[0].split("=")[1]))


    fig, ax = plt.subplots()
    ax.stem(x, y, markerfmt= ' ')
    plt.show()






    # plt.hist(data, bins=range(0, 30000), align='right', color='red')
    # plt.title("Variants")
    # plt.xlabel("Genome position", fontsize=35)
    # plt.ylabel("Depth", fontsize=35)
    # plt.tick_params(labelsize=20)
    # plt.show()
    # plt.clf()




def cov_pipeline(args):
    """
    Plot coverage histogram
    x-axis = genome
    y-axis = depth
    each bar is a bin of read depth
    """
    return

    # plt.hist(data, bins=range(-50, 50), align='right', color='green', alpha=0.6)
    # plt.title("Meth calls")
    # plt.xlabel("Score", fontsize=35)
    # plt.ylabel("Count", fontsize=35)
    # plt.tick_params(labelsize=20)
    # plt.show()
    # plt.clf()

if __name__ == '__main__':
    main()
