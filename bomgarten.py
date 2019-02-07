
#BOMGarten.py

import sys
import os
import wx
import sch
import locale
import wx
import urllib2
import requests
import glob
import ntpath
import importlib
import imp
import csv

version_str = "0.1 (Alpha)"

sys.path.insert(0, os.getcwd()+'/scrapers')


from lctrlsort import ColumnSorterMixinNextGen , SmartListCtrl
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin
from bs4 import BeautifulSoup

def quote_string(inputStr):
    if not inputStr.startswith("\""):
        inputStr = "\"" + inputStr

    if not inputStr.endswith("\""):
        inputStr = inputStr + "\""

    return inputStr

def unquote_string(inputStr):
    if inputStr.startswith("\""):
        inputStr = inputStr[1:]

    if inputStr.endswith("\""):
        inputStr = inputStr[:-1]

    return inputStr

def clean_string(str):
    for i in range(0, len(str)):
        try:
            str[i].encode("ascii")
        except:
            #means it's non-ASCII
            str = str.replace(str[i]," ") #replacing it with a single space

    for char in ['\r', '\t', '\n', '\"']:
        str = str.replace(char, '')

    return str.strip()

class LCtrlSortAuto(wx.ListCtrl, ColumnSorterMixinNextGen, ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ColumnSorterMixinNextGen.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

if True:
    ListCtrlClass = LCtrlSortAuto
else:
    ListCtrlClass = wx.ListCtrl


class ListComponent:
    def __init__(self, timestamp, reference, value=None, footprint=None, datasheet=None, supplier=None, supplier_partid=None, manufacturer=None, manufacturer_partid=None, itemdescription=None, unitprice=None, notes=None, part_link=None ):
        self.timestamp = timestamp
        self.reference = reference
        self.value = value
        self.footprint = footprint
        self.datasheet = datasheet
        self.supplier = supplier
        self.footprint = footprint
        self.supplier_partid = supplier_partid
        self.manufacturer = manufacturer
        self.manufacturer_partid = manufacturer_partid
        self.itemdescription = itemdescription
        self.unitprice = unitprice
        self.notes = notes
        self.part_link = part_link

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.setter
    def timestamp(self, value):
        self.timestamp = value

    @property
    def reference(self):
        return self.reference

    @reference.setter
    def reference(self, value):
        self.reference = value

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, value):
        self.value = value

    @property
    def footprint(self):
        return self.footprint

    @footprint.setter
    def footprint(self, footprint):
        self.footprint = footprint

    @property
    def datasheet(self):
        return self.datasheet

    @datasheet.setter
    def datasheet(self, datasheet):
        self.datasheet = datasheet

    @property
    def supplier(self):
        return self.supplier

    @supplier.setter
    def supplier(self, supplier):
        self.supplier = supplier

    @property
    def supplier_partid(self):
        return self.supplier_partid

    @supplier_partid.setter
    def supplier_partid(self, supplier_partid):
        self.supplier_partid = supplier_partid

    @property
    def manufacturer(self):
        return self.manufacturer

    @manufacturer.setter
    def manufacturer(self, manufacturer):
        self.manufacturer = manufacturer

    @property
    def manufacturer_partid(self):
        return self.manufacturer_partid

    @manufacturer_partid.setter
    def manufacturer_partid(self, manufacturer_partid):
        self.manufacturer_partid = manufacturer_partid

    @property
    def itemdescription(self):
        return self.itemdescription

    @itemdescription.setter
    def itemdescription(self, itemdescription):
        self.itemdescription = itemdescription

    @property
    def unitprice(self):
        return self.unitprice

    @unitprice.setter
    def unitprice(self, unitprice):
        self.unitprice = unitprice

    @property
    def notes(self):
        return self.notes

    @notes.setter
    def notes(self, notes):
        self.notes = notes

    @property
    def part_link(self):
        return self.part_link

    @part_link.setter
    def part_link(self, part_link):
        self.part_link = part_link

class KiCADScrape(wx.Frame):


    component_dict = {}
    schem = {}
    scrapers_list = []
    modules = []
    selected_scraper = None

    selected_item = None

    def sizeColumns(self):
        self.lstComponent.SetColumnWidth(0, 150)
        self.lstComponent.SetColumnWidth(1, 150)
        size = (sum([self.lstComponent.GetColumnWidth(i) for i in (0, 1, 2)]), -1)
        self.lstComponent.SetSize(size)
        self.lstComponent.SetMinSize(size)
        self.lstComponent.PostSizeEventToParent()

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def populateScrapersList(self):

        #clear scrapers combobox
        self.cmbScraper.Clear()

        #populate scrapers list
        fileList = glob.glob("./scrapers/*.py")
        foo = 1
        for item in fileList:
            self.cmbScraper.Insert(str(item), 0)
            self.scrapers_list.append(self.path_leaf(str(item)))
            foo = imp.load_source('scrapers', str(item))

        #set active scraper to the first one
        self.selected_scraper = foo.digikey_scraper()
        self.cmbScraper.SetSelection(0)

        pass

    def __init__(self, *args, **kwds):
        # begin wxGlade: KiCADScrape.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        #wx.Frame.SetIcon(wx.IconFromLocation("tree.ico"))
        #wx.IconFromBitmap(wx.Bitmap("./tree.ico", wx.BITMAP_TYPE_ANY))
        self.SetSize((712, 586))
        self.txtFileSelect = wx.TextCtrl(self, wx.ID_ANY, "")
        self.btnFileSelect = wx.Button(self, wx.ID_ANY, "...", style=wx.BU_EXACTFIT)
        self.window_1 = wx.SplitterWindow(self, wx.ID_ANY)
        #self.wndKiCAD = wx.ScrolledWindow(self.window_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.wndKiCAD = wx.Panel(self.window_1, wx.ID_ANY)
        #HERE4
        self.lstComponent = ListCtrlClass(self.wndKiCAD, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.wndCustomData = wx.Panel(self.window_1, wx.ID_ANY)
        self.cmbScraper = wx.ComboBox(self.wndCustomData, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.txtSupplierName = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtSupplierPartID = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.btnScrape = wx.Button(self.wndCustomData, wx.ID_ANY, "Scrape")
        self.txtMfgPartID = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.btnMfgScrape = wx.Button(self.wndCustomData, wx.ID_ANY, "Scrape")
        self.txtMfrName = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtItemDescription = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtPartLink = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtDataSheet = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtUnitPrice = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.txtNotes = wx.TextCtrl(self.wndCustomData, wx.ID_ANY, "")
        self.btnSave = wx.Button(self.wndCustomData, wx.ID_ANY, "Save")
        self.btnGenerateBOM = wx.Button(self.wndCustomData, wx.ID_ANY, "Generate BOM")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self._on_btnFileSelectPush, self.btnFileSelect)
        self.Bind(wx.EVT_BUTTON, self._on_scrapebtn_supplier_clicked, self.btnScrape)
        self.Bind(wx.EVT_BUTTON, self._on_scrapebtn_mfg_clicked, self.btnMfgScrape)
        self.Bind(wx.EVT_BUTTON, self._on_savebtn_clicked, self.btnSave)
        self.Bind(wx.EVT_BUTTON, self._on_generatebom_clicked, self.btnGenerateBOM)
        #HERE5
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected, self.lstComponent)
        # end wxGlade

        self.populateScrapersList()

    def __set_properties(self):
        # begin wxGlade: KiCADScrape.__set_properties
        self.SetTitle("BOMGarten" + " - " + version_str)
        self.lstComponent.InsertColumn(0, "UID", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.lstComponent.InsertColumn(1, "Ref", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.lstComponent.InsertColumn(2, "Val", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.lstComponent.InsertColumn(3, "Footprint", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.lstComponent.InsertColumn(4, "Datasheet", format=wx.LIST_FORMAT_LEFT, width=-1)
        #self.wndKiCAD.SetScrollRate(10, 10)
        self.window_1.SetMinimumPaneSize(20)
        #self.lstComponent.DeleteColumn(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: KiCADScrape.__do_layout
        szrMain = wx.BoxSizer(wx.VERTICAL)
        szrMainSplit = wx.BoxSizer(wx.VERTICAL)
        szrCustomData = wx.BoxSizer(wx.VERTICAL)
        szrGenerateBOM = wx.BoxSizer(wx.HORIZONTAL)
        szrSave = wx.BoxSizer(wx.HORIZONTAL)
        szrNotes = wx.BoxSizer(wx.HORIZONTAL)
        szrUnitPrice = wx.BoxSizer(wx.HORIZONTAL)
        szrDataSheet = wx.BoxSizer(wx.HORIZONTAL)
        szrPartLink = wx.BoxSizer(wx.HORIZONTAL)
        szrItemDesc = wx.BoxSizer(wx.HORIZONTAL)
        szrMfrName = wx.BoxSizer(wx.HORIZONTAL)
        szrMfgPartID = wx.BoxSizer(wx.HORIZONTAL)
        szrSupplierPartID = wx.BoxSizer(wx.HORIZONTAL)
        szrSupplierName = wx.BoxSizer(wx.HORIZONTAL)
        szrScraper = wx.BoxSizer(wx.HORIZONTAL)
        szrKiCADData = wx.BoxSizer(wx.VERTICAL)
        szrFileSelect = wx.BoxSizer(wx.HORIZONTAL)
        lblFileSelect = wx.StaticText(self, wx.ID_ANY, "KiCAD Schematic:")
        szrFileSelect.Add(lblFileSelect, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrFileSelect.Add(self.txtFileSelect, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 3)
        szrFileSelect.Add(self.btnFileSelect, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrMainSplit.Add(szrFileSelect, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND, 3)
        lblKiCADData = wx.StaticText(self.wndKiCAD, wx.ID_ANY, "KiCAD Data", style=wx.ALIGN_LEFT)
        szrKiCADData.Add(lblKiCADData, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrKiCADData.Add(self.lstComponent, 1, wx.ALL | wx.EXPAND, 3)
        self.wndKiCAD.SetSizer(szrKiCADData)
        lblCustomData = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Custom Data", style=wx.ALIGN_LEFT)
        szrCustomData.Add(lblCustomData, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        lblScraper = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Scraper")
        szrScraper.Add(lblScraper, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrScraper.Add(self.cmbScraper, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrScraper, 0, wx.EXPAND, 0)
        lblSupplierName = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Supplier Name")
        szrSupplierName.Add(lblSupplierName, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrSupplierName.Add(self.txtSupplierName, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrSupplierName, 0, wx.EXPAND, 0)
        lblSupplierPartID = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Supplier Part ID")
        szrSupplierPartID.Add(lblSupplierPartID, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrSupplierPartID.Add(self.txtSupplierPartID, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrSupplierPartID.Add(self.btnScrape, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrSupplierPartID, 0, wx.EXPAND, 0)
        lblMfgPartID = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Mfg Part ID")
        szrMfgPartID.Add(lblMfgPartID, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrMfgPartID.Add(self.txtMfgPartID, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrMfgPartID.Add(self.btnMfgScrape, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrMfgPartID, 0, wx.EXPAND, 0)
        lblMfrName = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Mfg Name")
        szrMfrName.Add(lblMfrName, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrMfrName.Add(self.txtMfrName, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrMfrName, 0, wx.EXPAND, 0)
        lblItemDesc = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Description")
        szrItemDesc.Add(lblItemDesc, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrItemDesc.Add(self.txtItemDescription, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrItemDesc, 0, wx.ALL | wx.EXPAND, 0)
        lblPartLink = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Part Link")
        szrPartLink.Add(lblPartLink, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrPartLink.Add(self.txtPartLink, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrPartLink, 0, wx.ALL | wx.EXPAND, 0)
        lblDataSheet = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Data Sheet")
        szrDataSheet.Add(lblDataSheet, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrDataSheet.Add(self.txtDataSheet, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrDataSheet, 0, wx.ALL | wx.EXPAND, 0)
        lblUnitPrice = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Unit Price")
        szrUnitPrice.Add(lblUnitPrice, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrUnitPrice.Add(self.txtUnitPrice, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrUnitPrice, 0, wx.ALL | wx.EXPAND, 0)
        lblNotes = wx.StaticText(self.wndCustomData, wx.ID_ANY, "Engineering Notes")
        szrNotes.Add(lblNotes, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrNotes.Add(self.txtNotes, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrNotes, 0, wx.ALL | wx.EXPAND, 0)
        szrSave.Add(self.btnSave, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrSave, 0, wx.EXPAND, 0)
        szrGenerateBOM.Add(self.btnGenerateBOM, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        szrCustomData.Add(szrGenerateBOM, 0, wx.EXPAND, 0)
        self.wndCustomData.SetSizer(szrCustomData)
        self.window_1.SplitVertically(self.wndKiCAD, self.wndCustomData)
        szrMainSplit.Add(self.window_1, 1, wx.EXPAND, 0)
        szrMain.Add(szrMainSplit, 1, wx.EXPAND, 0)
        self.SetSizer(szrMain)
        self.Layout()
        # end wxGlade

    def _on_list_item_selected(self, event):  # wxGlade: KiCADScrape.<event_handler>
        #item = self.lstComponent.GetFirstSelected()
        if not self.selected_item == None:
            #save last selected items state
            lastSelected = self.lstComponent.GetItem(itemId=self.selected_item, col=0)
            saveItem = self.component_dict[lastSelected.GetText()]
            saveItem.manufacturer = self.txtMfrName.GetValue()
            saveItem.manufacturer_partid = self.txtMfgPartID.GetValue()
            saveItem.supplier = self.txtSupplierName.GetValue()
            saveItem.supplier_partid = self.txtSupplierPartID.GetValue()
            saveItem.itemdescription = self.txtItemDescription.GetValue()
            saveItem.part_link = self.txtPartLink.GetValue()
            saveItem.datasheet = self.txtDataSheet.GetValue()
            saveItem.unitprice = self.txtUnitPrice.GetValue()
            saveItem.notes = self.txtNotes.GetValue()

        currentItem = event.m_itemIndex
        item = self.lstComponent.GetItem(itemId=currentItem, col=0)
        dictItem = self.component_dict[item.GetText()]

        self.txtMfrName.ChangeValue(dictItem.manufacturer)
        self.txtMfgPartID.ChangeValue(dictItem.manufacturer_partid)
        self.txtSupplierName.ChangeValue(dictItem.supplier)
        self.txtSupplierPartID.ChangeValue(dictItem.supplier_partid)
        self.txtItemDescription.ChangeValue(dictItem.itemdescription)
        self.txtPartLink.ChangeValue(dictItem.part_link)
        self.txtDataSheet.ChangeValue(dictItem.datasheet)
        self.txtUnitPrice.ChangeValue(dictItem.unitprice)
        self.txtNotes.ChangeValue(dictItem.notes)

        self.selected_item = event.m_itemIndex

    def saveSelectedComponent(self):
        item = self.lstComponent.GetFirstSelected()
        currentItem = event.m_itemIndex
        item = self.lstComponent.GetItem(itemId=currentItem, col=0)
        pass

    def _on_btnFileSelectPush(self, event):  # wxGlade: KiCADScrape.<event_handler>

        open_dialog = wx.FileDialog(self, "KiCAD Schematic", "", "", "KiCAD Schmatics (*.sch)|*.sch", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if open_dialog.ShowModal() == wx.ID_CANCEL:
            return

        else:
            self.txtFileSelect.ChangeValue(open_dialog.GetPath())

            if self.schem:
                self.schem = None

            self.schem = sch.Schematic(self.txtFileSelect.GetValue())

            self.lstComponent.DeleteAllItems()
            self.component_dict.clear()

            for component in self.schem.components:
                comp_name = clean_string(str(component.fields[0]['ref']))

                if not comp_name.startswith( '#' ):

                    comp_timestamp = clean_string(str(component.unit['time_stamp']))
                    comp_val = clean_string(str(component.fields[1]['ref']))
                    comp_footprint = clean_string(str(component.fields[2]['ref']))
                    comp_datasheet = clean_string(str(component.fields[3]['ref']))
                    comp_supplier = "\"~\""
                    comp_supplier_partid = "\"~\""
                    comp_manufacturer = "\"~\""
                    comp_manufacturer_partid = "\"~\""
                    comp_itemdescription = "\"~\""
                    comp_unitprice = "\"~\""
                    comp_notes = "\"~\""
                    comp_part_link = "\"~\""


                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'mfg_name':
                            comp_manufacturer = nameItem['ref']
                            comp_manufacturer = unquote_string(comp_manufacturer)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'mfg_partid':
                            comp_manufacturer_partid = nameItem['ref']
                            comp_manufacturer_partid = unquote_string(comp_manufacturer_partid)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'supplier_name':
                            comp_supplier = nameItem['ref']
                            comp_supplier = unquote_string(comp_supplier)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'supplier_partid':
                            comp_supplier_partid = nameItem['ref']
                            comp_supplier_partid = unquote_string(comp_supplier_partid)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'description':
                            comp_itemdescription= nameItem['ref']
                            comp_itemdescription = unquote_string(comp_itemdescription)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'part_link':
                            comp_part_link = nameItem['ref']
                            comp_part_link = unquote_string(comp_part_link)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'unit_price':
                            comp_unitprice = nameItem['ref']
                            comp_unitprice = unquote_string(comp_unitprice)

                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'notes':
                            comp_notes = nameItem['ref']
                            comp_notes = unquote_string(comp_notes)

                    #Datasheet is a bit weird... KiCAD has a value for this but I'm unsure what it's there for. We'll just use our own for now.
                    for nameItem in component.fields:
                        if clean_string(nameItem['name']) == 'bom_datasheet':
                            comp_datasheet = nameItem['ref']
                            comp_datasheet = unquote_string(comp_datasheet)

                    self.component_dict[comp_timestamp] = ListComponent(comp_timestamp,comp_name,comp_val,comp_footprint,comp_datasheet,comp_supplier,comp_supplier_partid,comp_manufacturer,comp_manufacturer_partid,comp_itemdescription,comp_unitprice,comp_notes,comp_part_link)

            self._populate_list()
            self.lstComponent.SortByColumn(1)


    def _populate_list(self):
        for component in self.component_dict:
            newindex = self.lstComponent.Append([self.component_dict[component].timestamp,self.component_dict[component].reference, self.component_dict[component].value, self.component_dict[component].footprint, self.component_dict[component].datasheet])
            self.lstComponent.SetItemData(newindex, wx.NewId())
            pass

    def _on_savebtn_clicked(self, event):

        if not self.schem:
            #dlg = wx.MessageDialog(None, "You have no schematic loaded.",wx.OK | wx.ICON_ERROR)
            msg = wx.MessageDialog(self, "You have no schematic file loaded.", "No Schematic",wx.OK | wx.ICON_ERROR)
            result = msg.ShowModal()
            return

        #Warn the user that we're going to overwrite their file. This is because we're still in alpha and I imagine people being pretty mad
        # if they have their schematic overwritten without at least a warning.
        msg = wx.MessageDialog(self,"This product is in its Alpha version, and overwriting your schematic file is not recommended.", "Warning",wx.OK | wx.ICON_WARNING)
        result = msg.ShowModal()

        #Open a save dialog
        fdlg = wx.FileDialog(self, "KiCAD Schematic", "", "", "KiCAD Schmatics (*.sch)|*.sch", wx.FD_SAVE)
        save_path = ""

        if fdlg.ShowModal() == wx.ID_OK:
            save_path = fdlg.GetPath()

            #save last selected items state
            item = self.lstComponent.GetItem(itemId=self.lstComponent.GetFirstSelected(), col=0)
            saveItem = self.component_dict[item.GetText()]
            saveItem.manufacturer = self.txtMfrName.GetValue()
            saveItem.manufacturer_partid = self.txtMfgPartID.GetValue()
            saveItem.supplier = self.txtSupplierName.GetValue()
            saveItem.supplier_partid = self.txtSupplierPartID.GetValue()
            saveItem.itemdescription = self.txtItemDescription.GetValue()
            saveItem.part_link = self.txtPartLink.GetValue()
            saveItem.datasheet = self.txtDataSheet.GetValue()
            saveItem.unitprice = self.txtUnitPrice.GetValue()
            saveItem.notes = self.txtNotes.GetValue()

            #Look at our local dictionary in memory that contains our temporary component data created by the user
            for list_component_timestamp in self.component_dict:
                #Use the timestamp value (UID) and try to find a matching component in the schematic object
                for schematic_component_object in self.schem.components:
                    #The component name will allow us to filter out some noise
                    schematic_component_name_str = clean_string(str(schematic_component_object.fields[0]['ref']))
                    if not schematic_component_name_str.startswith( '#' ):
                        #Attempt to match
                        schematic_component_timestamp_str = clean_string(str(schematic_component_object.unit['time_stamp']))
                        if schematic_component_timestamp_str == list_component_timestamp:
                            #if the UIDs match then we'll want to add all of our data to the schematic object

                            #Just in case, if these values don't exist already we'll create them
                            if "\"mfg_name\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"mfg_name\"", 'ref':"\"~\""})
                            if "\"mfg_partid\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"mfg_partid\"", 'ref':"\"~\""})
                            if "\"supplier_name\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"supplier_name\"", 'ref':"\"~\""})
                            if "\"supplier_partid\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"supplier_partid\"", 'ref':"\"~\""})
                            if "\"description\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"description\"", 'ref':"\"~\""})
                            if "\"part_link\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"part_link\"", 'ref':"\"~\""})
                            if "\"unit_price\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"unit_price\"", 'ref':"\"~\""})
                            if "\"notes\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"notes\"", 'ref':"\"~\""})
                            if "\"bom_datasheet\"" not in [x['name'] for x in schematic_component_object.fields]:
                                schematic_component_object.addField({'name':"\"bom_datasheet\"", 'ref':"\"~\""})

                            #Now we set the schematic components to be the same as our local values
                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'mfg_name':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].manufacturer)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'mfg_partid':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].manufacturer_partid)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'supplier_name':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].supplier)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'supplier_partid':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].supplier_partid)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'description':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].itemdescription)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'part_link':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].part_link)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'unit_price':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].unitprice)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'notes':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].notes)

                            for nameItem in schematic_component_object.fields:
                                if clean_string(nameItem['name']) == 'bom_datasheet':
                                    nameItem['ref'] = quote_string(self.component_dict[schematic_component_timestamp_str].datasheet )



            #finally, we save the schematic
            self.schem.save(save_path)

        pass

    def _on_generatebom_clicked(self, event):  # wxGlade: KiCADScrape.<event_handler>

        fdlg = wx.FileDialog(self, "Export BOM File", "", "", "CSV files(*.csv)|*.*", wx.FD_SAVE)
        save_path = ""

        if fdlg.ShowModal() == wx.ID_OK:
            save_path = fdlg.GetPath()

            with open(save_path, 'wb') as csvfile:
                #create a CSV writer
                bomwriter = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)

                #Create the header row
                bomwriter.writerow(['UID','Reference','Value','Footprint','Datasheet','SupplierName','SupplierPartID','MfgName','MfgPartID','PartDescription','PartLink','UnitPrice','EngineeringNotes'])

                #Go through each component in the schematic
                for component in self.schem.components:
                    comp_name = clean_string(str(component.fields[0]['ref']))

                    if not comp_name.startswith( '#' ):

                        #collect the data from each component (these should be in all schematics)
                        comp_timestamp = clean_string(str(component.unit['time_stamp']))
                        comp_val = clean_string(str(component.fields[1]['ref']))
                        comp_footprint = clean_string(str(component.fields[2]['ref']))
                        comp_datasheet = clean_string(str(component.fields[3]['ref']))

                        comp_mfg_name = ""
                        comp_mfg_partid = ""
                        comp_supplier_name = ""
                        comp_supplier_partid = ""
                        comp_description = ""
                        comp_part_link = ""
                        comp_unit_price = ""
                        comp_notes = ""

                        #go into the schematic object component fields and extract each data point
                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'mfg_name':
                                comp_mfg_name = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'mfg_partid':
                                comp_mfg_partid = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'supplier_name':
                                comp_supplier_name = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'supplier_partid':
                                comp_supplier_partid = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'description':
                                comp_description = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'part_link':
                                comp_part_link = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'unit_price':
                                comp_unit_price = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'notes':
                                comp_notes = unquote_string(nameItem['ref'])

                        for nameItem in component.fields:
                            if clean_string(nameItem['name']) == 'bom_datasheet':
                                comp_datasheet = unquote_string(nameItem['ref'])

                        #write the row
                        bomwriter.writerow([comp_timestamp,comp_name,comp_val,comp_footprint, comp_datasheet, comp_supplier_name,comp_supplier_partid,comp_mfg_name,comp_mfg_partid,comp_description,comp_part_link,comp_unit_price,comp_notes])

        pass

    def _on_scrapebtn_mfg_clicked(self, event):
        #The point of this Alpha is to demonstrate functionality, and I'm eager to put BOMGarten online. We'll get back to this because it's something I want.
        wx.MessageBox('Scraping Part Info by manufacturer ID has not been implemented yet. This product is in Alpha.', 'Not Implemented', wx.OK | wx.ICON_INFORMATION)
        pass


    def _on_scrapebtn_supplier_clicked(self, event):  # wxGlade: KiCADScrape.<event_handler>

        #Determine if we have a scraper selected
        if self.selected_scraper:

            #Get the supplier part and send it to the scraper
            strSupplierPart = self.txtSupplierPartID.GetValue();

            if strSupplierPart:

                #set all of our values to what was scraped.
                self.selected_scraper.scrape(strSupplierPart.strip())

                strSupplierName = self.selected_scraper.get_supplier_name()
                strMfgName = self.selected_scraper.get_mfr_name()
                strMfgPartNum = self.selected_scraper.get_mfr_part_num()
                strDesc = self.selected_scraper.get_description()
                strUnitPrice = self.selected_scraper.get_unit_price()
                strPartLink = self.selected_scraper.get_partlink()
                strDatasheet = self.selected_scraper.get_datasheet()

                if strSupplierName:
                    self.txtSupplierName.ChangeValue(strSupplierName)

                if strMfgName:
                    self.txtMfrName.ChangeValue(strMfgName)

                if strMfgPartNum:
                    self.txtMfgPartID.ChangeValue(strMfgPartNum)

                if strDesc:
                    self.txtItemDescription.ChangeValue(strDesc)

                if strUnitPrice:
                    self.txtUnitPrice.ChangeValue(strUnitPrice)

                if strPartLink:
                    self.txtPartLink.ChangeValue(strPartLink)

                if strDatasheet:
                    self.txtDataSheet.ChangeValue(strDatasheet)


class MyApp(wx.App):
    def OnInit(self):
        self.frmKicadScrape = KiCADScrape(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frmKicadScrape)
        self.frmKicadScrape.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
