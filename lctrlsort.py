import wx
import locale

class ColumnSorterMixinNextGen(object):
    '''
    Self contained version of ColumnSorterMixin

    As a user you just need to use it in conjunction with ListCtrl to create a child class
    and call the constructor

    In comparison with the original there is no need to keep an itemDataMap or define the
    GetListCtrl (the latter because it is asumed the Mixin will only be used with a ListCtrl)

    I have tried to keep the interface of the ColumSorterMixin as it was. Any error can be
    assigned to me.

    Additionally I have removed the __ mangling code (may anyone be willing to subclass in the future?)
    '''

    def __init__(self):
        self.col = -1 # Keeps a reference to the last sorte column
        self.sortflags = list() # Keeps ascending/descending reference for columns
        self.sortdata = dict() # Holder for column text for he sort process

        # Assumption: always mixin with a ListCtrl
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self) # Bind to column header click

        # Replace ListCtrl.InsertColumn with own method and keep a reference
        setattr(self, 'InsertColumnOrig', self.InsertColumn)
        setattr(self, 'InsertColumn', self.InsertColumnMixin)

        # Replace ListCtrl.DeleteColumn with own method and keep a reference
        setattr(self, 'DeleteColumnOrig', self.DeleteColumn)
        setattr(self, 'DeleteColumn', self.DeleteColumnMixin)

    def OnSortOrderChanged(self):
        print("List Sorted")
        ''' Callback execute after the sorting process is over'''
        pass

    def SortByColumn(self, col):
        '''
        When the event happens a list of column text is gathered on the fly to use it
        during the sorting process.

        This is key to avoid the user keeping external data sync'ed: the data is already in the
        control

        The rest from the original
        '''

        #event.Skip()
        oldcol = col # refernce to last sorted column
        self.col = col # = event.GetColumn() # current column to be sorted
        self.sortflags[col] = not self.sortflags[col] # invert the last sorting order

        self.sortdata = dict() # prepare the data holder
        for index in xrange(0, self.GetItemCount()):
            # loop over all items and gather the ItemData and ColumnText
            itemdata = self.GetItemData(index)
            item = self.GetItem(index, col)
            self.sortdata[itemdata] = item.GetText()

        self.SortItems(self.GetColumnSorter()) # Sort
        if wx.Platform != "__WXMAC__" or \
           wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") == 1:
            # If needed and possible update the images
            self.UpdateImages(oldcol)

        self.OnSortOrderChanged() # go to the notification callback

    def OnColClick(self, event):
        '''
        When the event happens a list of column text is gathered on the fly to use it
        during the sorting process.

        This is key to avoid the user keeping external data sync'ed: the data is already in the
        control

        The rest from the original
        '''
        self.SortByColumn(event.GetColumn())


    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""
        return self.ColumnSorter

    def GetSecondarySortValues(self, col, key1, key2):
        """Returns a tuple of 2 values to use for secondary sort values when the
           items in the selected column match equal.  The default just returns the
           item data values."""
        return (key1, key2)

    def ColumnSorter(self, key1, key2):

        '''
        In comparison with the original we don't need the column, because the
        data for the specific column has been already gathered and saved along the key (item data)
        '''
        ascending = self.sortflags[self.col]
        item1 = self.sortdata[key1]
        item2 = self.sortdata[key2]

        #--- Internationalization of string sorting with locale module
        if type(item1) == unicode and type(item2) == unicode:
            cmpVal = locale.strcoll(item1, item2)
        elif type(item1) == str or type(item2) == str:
            cmpVal = locale.strcoll(str(item1), str(item2))
        else:
            cmpVal = cmp(item1, item2)

        # If the items are equal then pick something else to make the sort value unique
        if not cmpVal:
            cmpVal = apply(cmp, self.GetSecondarySortValues(self.col, key1, key2))

        return cmpVal if ascending else -cmpVal

    def InsertColumnMixin(self, col, heading, format=wx.LIST_FORMAT_LEFT, width=-1):
        '''
        Replaces ListCtrl InsertColumn to keep the ascending/descending sort flags sync'ed
        with column insertion

        The reason to do this: if put on the right hand side of the "base classes" list
        a plain InsertColumn method would not be found and Mixins are usually put on the right
        hand side
        '''
        index = self.InsertColumnOrig(col, heading, format, width)
        if index != -1:
            # Colum inserte: Insert a sorting flag in the returned index
            self.sortflags.insert(index, False)
            if self.col >= index:
                # Fix the index of the last sorted column because we added to the left
                self.col += 1

        return index

    def DeleteColumnMixin(self, col):
        '''
        Replaces ListCtrl DeleteColumn to keep the ascending/descending sort flags sync'ed
        with column insertion

        The reason to do this: if put on the right hand side of the "base classes" list
        a plain InsertColumn method would not be found and Mixins are usually put on the right
        hand side
        '''
        deleted = self.DeleteColumnOrig(col)
        if deleted:
            self.sortflags.pop(col)
            if self.col == col:
                # Last sorted column ... removed ... invalidate index
                self.col = -1
            elif self.col > col:
                # Keep the index sync'ed, since we removed from the left
                self.col -= 1

    def GetSortState(self):
        """
        Return a tuple containing the index of the column that was last sorted
        and the sort direction of that column.
        Usage:
        col, ascending = self.GetSortState()
        # Make changes to list items... then resort
        self.SortListItems(col, ascending)
        """
        return (self.col, self.sortflags[self.col])

    def GetSortImages(self):
        """
        Returns a tuple of image list indexesthe indexes in the image list for an image to be put on the column
        header when sorting in descending order.
        """
        return (-1, -1)  # (decending, ascending) image IDs

    def UpdateImages(self, oldcol):
        sortImages = self.GetSortImages()
        if self.col != -1 and sortImages[0] != -1:
            img = sortImages[self.sortflags[self.col]]
            if oldcol != -1:
                self.ClearColumnImage(oldcol)
            self.SetColumnImage(self.col, img)

    def GetColumnWidths(self):
        """
        Returns a list of column widths.  Can be used to help restore the current
        view later.
        """
        rv = list()
        for col in range(self.GetColumnCount()):
            rv.append(self.GetColumnWidth(col))
        return rv

    def SortListItems(self, col=-1, ascending=True):
        """Sort the list on demand.  Can also be used to set the sort column and order."""
        oldcol = self.col
        if col != -1:
            self.col = col
            self.sortflags[col] = ascending
        self.SortItems(self.GetColumnSorter())
        self.UpdateImages(oldcol)



class SmartListCtrl(wx.ListCtrl, ColumnSorterMixinNextGen):
    def __init__(self, *args, **kwargs):
        # *args, **kwargs ensures it can be used with GUI builders unmodified
        wx.ListCtrl.__init__(self, *args, **kwargs)
        ColumnSorterMixinNextGen.__init__(self)
