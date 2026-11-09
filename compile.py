import os
import re
import shutil

from systemrdl import *
from peakrdl_html import HTMLExporter

roots = {}

# Markdown links and images: `[text](target)` / `![alt](target)`
MD_LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)(\))")
# Targets that aren't files in the repository
EXTERNAL_LINK = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|#|/)")


def publish_path(rdl_file, target):
    """
    Maps a link in a description to where its file is published on the site.

    Descriptions link to files relative to the RDL file they are written in
    (`assets/foo.pdf` next to `rdl/<folder>/x.rdl`). Each `rdl/<folder>/assets/`
    is published as `assets/<folder>/`, so different folders can reuse file names.
    :param rdl_file: The RDL file the description comes from
    :param target: The link target, as written
    :return: The link target on the site
    """
    path, sep, fragment = target.partition("#")
    file = os.path.normpath(os.path.join(os.path.dirname(rdl_file), path))
    parts = os.path.relpath(file, "rdl").split(os.sep)

    if len(parts) < 3 or parts[1] != "assets" or not os.path.isfile(file):
        raise ValueError("%s: broken link `%s` (no such file in rdl/<folder>/assets/)" % (rdl_file, target))

    return "/".join(["assets", parts[0]] + parts[2:]) + sep + fragment


def rewrite_links(root):
    """
    Rewrites the links in every description to where their files are published
    :param root: The elaborated root node
    :return: None
    """
    errors = []
    seen = set()
    for node in root.descendants(unroll=False):
        inst = node.inst
        desc = inst.properties.get("desc")
        if id(inst) in seen or not desc or "](" not in desc:
            continue
        seen.add(id(inst))
        rdl_file = inst.property_src_ref["desc"].filename

        def replace(match):
            target = match.group(2)
            if EXTERNAL_LINK.match(target):
                return match.group(0)
            try:
                return match.group(1) + publish_path(rdl_file, target) + match.group(3)
            except ValueError as e:
                errors.append(str(e))
                return match.group(0)

        inst.properties["desc"] = MD_LINK.sub(replace, desc)

    if errors:
        for error in sorted(set(errors)):
            print("\t%s" % error)
        exit(1)


def copy_assets(output_dir):
    """
    Copies each `rdl/<folder>/assets/` folder to `<output_dir>/assets/<folder>/`
    :param output_dir: The generated site's folder
    :return: None
    """
    for folder in sorted(os.listdir("rdl")):
        source = os.path.join("rdl", folder, "assets")
        if os.path.isdir(source):
            shutil.copytree(source, os.path.join(output_dir, "assets", folder), dirs_exist_ok=True)


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
            rewrite_links(root)
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

    # Publish the files the descriptions link to
    copy_assets("out/web/")
