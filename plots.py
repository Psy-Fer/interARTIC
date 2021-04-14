import os
import sys
import argparse
import gzip
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
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

def print_verbose(message):
    '''verbose printing'''
    sys.stderr.write('info: %s\n' % message)

def main():
    '''
    main func directing which plots to make
    '''
    VERSION = "0.0.1"
    NAME = "interArtic plots"
    parser = MyParser(
        description="Plots for interArtic",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # main options for base level checks and version output
    parser.add_argument("--version", action='version', version="{} version: {}".format(NAME, VERSION),
                        help="Prints version")

    parser.add_argument("-v", "--vcf_file",
                        help="full path to vcf file")


    parser.add_argument("-d1", "--depth_file_1",
                        help="full path to depth file 1")
    parser.add_argument("-d2", "--depth_file_2",
                        help="full path to depth file 2")

    parser.add_argument("-b", "--bed",
                        help="full path to scheme bed file")


    args = parser.parse_args()
    print_verbose("arg list: {}".format(args))

    # print help if no arguments given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    bed_1, bed_2 = get_bed(args)

    if args.vcf_file and not args.depth_file_1:
        vcfx_snv, vcfy_snv, vcfx_id, vcfy_id = vcf_pipeline(args)
        plot(args, bed_1, bed_2, vcfx_snv=vcfx_snv, vcfy_snv=vcfy_snv, vcfx_id=vcfx_id, vcfy_id=vcfy_id)
    elif args.depth_file_1 and args.depth_file_2 and not args.vcf_file:
        covx, covy = cov_pipeline(args)
        plot(args, bed_1, bed_2, covx=covx, covy=covy)
    elif args.vcf_file and args.depth_file_1 and args.depth_file_2:
        vcfx_snv, vcfy_snv, vcfx_id, vcfy_id = vcf_pipeline(args)
        covx, covy = cov_pipeline(args)
        plot(args, bed_1, bed_2, vcfx_snv=vcfx_snv, vcfy_snv=vcfy_snv, vcfx_id=vcfx_id, vcfy_id=vcfy_id, covx=covx, covy=covy)
    else:
        sys.stderr.write("Command unknown: {}".format(args.command))
        parser.print_help(sys.stderr)
        sys.exit(1)

def get_bed(args):
    """
    create 2 lists of cordinates for overlapping amplicons
    """
    tmp_1 = []
    tmp_2 = []
    bed_1 = []
    bed_2 = []
    with open(args.bed, 'r') as f:
        for l in f:
            l = l.strip('\n')
            l = l.strip('\t')
            l = l.split('\t')
            print(l)
            if "alt" in l[3]:
                continue
            if l[-1][-1] == '1':
                tmp_1.append(int(l[1]))
                tmp_1.append(int(l[2]))
            elif l[-1][-1] == '2':
                tmp_2.append(int(l[1]))
                tmp_2.append(int(l[2]))
            else:
                sys.stderr.write("bed format unknown: {}\n, please contact developers\n".format(l[-1]))

    tmp_1.sort()
    tmp_2.sort()

    for i in range(0,len(tmp_1)-3+1,4):
        bed_1.append((tmp_1[i], tmp_1[i+3]))
    for i in range(0,len(tmp_2)-3+1,4):
        bed_2.append((tmp_2[i], tmp_2[i+3]))


    return np.array(bed_1), np.array(bed_2)



def vcf_pipeline(args):
    """
    Plot vcf histogram
    x-axis = genome
    y-axis = depth
    each bar represents a variant, anotated
    Add genes/orfs/annoation to bottom (or maybe even top?) of plot for context
    """
    data = []
    x_snv = []
    y_snv = []
    x_id = []
    y_id = []
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
            if len(row["REF"]) == len(row["ALT"]):
                x_snv.append(int(row["POS"]))
                y_snv.append(int(row["INFO"].split(";")[0].split("=")[1]))
            else:
                x_id.append(int(row["POS"]))
                y_id.append(int(row["INFO"].split(";")[0].split("=")[1]))

    if x_snv:
        nx_snv = np.array(x_snv)
        ny_snv = np.array(y_snv)
    if x_id:
        nx_id = np.array(x_id)
        ny_id = np.array(y_id)
    if x_snv and x_id:
        return nx_snv, ny_snv, nx_id, ny_id
    if x_snv and not x_id:
        return nx_snv, ny_snv, None, None
    if not x_snv and x_id:
        return None, None, nx_id, ny_id
    return None, None, None, None


def cov_pipeline(args):
    """
    Plot coverage histogram
    x-axis = genome
    y-axis = depth
    each bar is a bin of read depth
    """
    dp1x = []
    dp1y = []
    dp2y = []
    bothy = []

    with open(args.depth_file_1, 'r') as f:
        for l in f:
            l = l.strip("\n")
            l = l.split("\t")
            dp1x.append(int(l[2]))
            dp1y.append(int(l[3]))

    with open(args.depth_file_2, 'r') as f:
        for l in f:
            l = l.strip("\n")
            l = l.split("\t")
            dp2y.append(int(l[3]))

    for i in range(len(dp1y)):
        k = dp1y[i] + dp2y[i]
        bothy.append(k)

    bothy_trimmed = np.array([i for i in bothy])
    dp1x_trimmed = np.array([i for i in dp1x])

    return dp1x_trimmed, bothy_trimmed

    # plt.fill_between(dp1x_trimmed, bothy_trimmed, color="skyblue", alpha=0.4)
    # plt.show()


def plot(args, bed_1, bed_2, vcfx_snv=None, vcfy_snv=None, vcfx_id=None, vcfy_id=None, covx=None, covy=None):
    """
    Plot everything separate or at one
    """

    fig, ax = plt.subplots()
    if args.vcf_file and not args.depth_file_1:
        # ax.stem(vcfx, vcfy, markerfmt= ' ')
        if vcfx_snv is not None:
            plt.vlines(vcfx_snv, 0, vcfy_snv, colors='red')
        if vcfx_id is not None:
            plt.vlines(vcfx_id, 0, vcfy_id, colors='green')
            plt.title("Variants", fontsize=20)
    elif args.depth_file_1 and args.depth_file_2 and not args.vcf_file:
        if covx is not None:
            plt.fill_between(covx, covy, color="skyblue", alpha=0.6)
            plt.title("Coverage", fontsize=20)
    elif args.vcf_file and args.depth_file_1 and args.depth_file_2:
        # ax.stem(vcfx, vcfy, markerfmt= ' ')
        if vcfx_snv is not None:
            plt.vlines(vcfx_snv, 0, vcfy_snv, colors='red')
        if vcfx_id is not None:
            plt.vlines(vcfx_id, 0, vcfy_id, colors='green')
        if covx is not None:
            plt.fill_between(covx, covy, color="skyblue", alpha=0.6)
        plt.title("Variants and Coverage", fontsize=20)


    print(bed_1)
    for i, j in bed_1:
        ax.add_patch(plt.Rectangle((i,-20),j-i, 15,facecolor='silver',
                              clip_on=False,linewidth = 1))

    for i, j in bed_2:
        ax.add_patch(plt.Rectangle((i,-40),j-i, 15,facecolor='silver',
                              clip_on=False, linewidth = 1))

    plt.axhline(y=20, color='grey', linestyle='--')

    plt.xlabel("Genome position", fontsize=20)
    plt.ylabel("Depth", fontsize=20)
    # plt.tick_params(labelsize=20)



    plt.show()


if __name__ == '__main__':
    main()
