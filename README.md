# BOMGarten (ALPHA)

## THIS TOOL IS IN AN ALPHA STAGE AND IS NOT YET RECOMMENED FOR PRODUCTION USE

BOMGarten is a Bill of Materials (BOM) Management and Scraper Tool for KiCAD.

This tool provides a GUI interface to more easily manage a Bill of Materials (BOM) in KiCAD. It is written in Python 2.7 using wxGlade.

The major advantage of this tool is that it can save data to and from a KiCAD schematic directly. No more having to manage a seperate spreadsheet and manual data entry. If you delete a component or add a new one your BOM made with BOMGarten is instantly affected. BOMGarten also has features that allow a user to paste in a part number and scrape part vendors for data making making the entire BOM process that much easier.

Currently, BOMGarten is a standalone tool, and is not integrated with KiCAD in anyway other than using some of the python helper code that KiCAD team released.

This project is on-going and still under active development. The primary purpose of this Alpha release is to demonstrate functionality. Features may be added or removed, and any degree of compatibility with future releases cannot be guaranteed.

To use this Project clone the repository:

```
git clone https://github.com/volunteerlabs/BOMGarten.git

```

Then run the python script

```
python bomgarten.py

```

Chances are there are some python dependencies involved with this project, so it may or may not be as easy as running a couple of lines on the command line depending on if you have them or not. I'll update this readme when I finally run this on a clean install.
