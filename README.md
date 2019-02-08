# BOMGarten (ALPHA)

## THIS TOOL IS IN AN ALPHA STAGE AND IS NOT YET RECOMMENED FOR PRODUCTION USE

BOMGarten is a Bill of Materials (BOM) Management and Scraper Tool for KiCAD.

This tool provides a GUI interface to more easily manage a Bill of Materials (BOM) in KiCAD. It is written in Python 2.7 using wxGlade.

The major advantage of this tool is that it can save data to and from a KiCAD schematic directly. The real world part numbers and data that goes into a BOM becomes part of your schematic. No more having to manage a seperate document in order to manage your BOM. If you delete a component or add a new one your BOM is instantly affected. BOMGarten also has features that allow a user to paste in a part number and scrape part vendors for data making making the entire BOM process that much easier.

Currently, BOMGarten is a standalone tool, and is not integrated with KiCAD in anyway other than using some of the python schematic helper code that KiCAD has released.

This project is on-going and still under active development. The primary purpose of this Alpha release is to demonstrate functionality. Features may be added or removed, and any degree of compatibility with future releases cannot be guaranteed.

To use this Project clone the repository:

```
git clone https://github.com/volunteerlabs/BOMGarten.git

```

Then run the python script

```
python bomgarten.py

```

