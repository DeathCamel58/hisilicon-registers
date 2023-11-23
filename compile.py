import os

from systemrdl import *
from peakrdl_html import HTMLExporter

roots = {}


def get_rdl_folders():
    """
    Gets all the RDL chip folders
    :return: The list chip names
    """
    folders = os.listdir("rdl")

    print("Found RDL folders:")
    if len(folders) == 0:
        print("\tNo RDL folders found!")
        exit(1)
    else:
        # Remove the `common` folder, as this is only an include folder
        for i in range(len(folders) - 1, -1, -1):
            if folders[i] == "common":
                folders.pop(i)
        for folder in folders:
            print("\t%s" % folder)

    return folders


def process_chip(chip):
    """
    Compiles each chip in a chip folder, and appends them to the `roots` array
    :param chip: The chip folder name
    :return: None
    """
    print("Processing RDL files in rdl/%s" % chip)

    chips = []
    with open("rdl/%s/chips.txt" % chip) as chip_file:
        for line in chip_file:
            chips.append(line.replace("\n", ""))

    # Include all the common RDL files
    includes = os.listdir("rdl/common")
    for i in range(len(includes) - 1, -1, -1):
        includes[i] = "rdl/common/%s" % includes[i]

    # Include all the RDL files in the chip's directory
    rdl_files = os.listdir("rdl/%s" % chip)
    for i in range(len(rdl_files) - 1, -1, -1):
        # Fix the filename of the RDL files, and remove the base RDL file from the array
        if rdl_files[i] != "%s.rdl" % chip:
            includes.append("rdl/%s/%s" % (chip, rdl_files[i]))

    try:
        for chip_file in chips:
            rdl = RDLCompiler()

            print("\tProcessing chip file at rdl/%s/%s.rdl" % (chip, chip_file))
            rdl.compile_file("rdl/%s/%s.rdl" % (chip, chip_file), includes)

            root = rdl.elaborate()
            roots[chip_file] = root
    except RDLCompileError as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    folders = get_rdl_folders()

    for folder in folders:
        process_chip(folder)

    # Alphabetize the chips
    roots = sorted(roots.items())
    chiparray = []
    for key, value in roots:
        chiparray.append(value)

    # Generate the documentation site
    exporter = HTMLExporter(user_template_dir="webTemplate/")
    exporter.export(chiparray,
                    "out/web/",
                    title="HiSilicon Registers",
                    home_url="https://github.com/DeathCamel58/hisilicon-registers",
                    footer="File an issue on GitHub if you need additional information on any of these chips.")
