# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-88b0f50)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.propgrid as pg
import wx.richtext
import wx.dataview

###########################################################################
## Class MainWindow
###########################################################################

class MainWindow ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"DPLoader2", pos = wx.DefaultPosition, size = wx.Size( 500,502 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_menubar = wx.MenuBar( 0 )
        self.m_menuFile = wx.Menu()
        self.m_FileExit = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"E&xit"+ u"\t" + u"CTRL+q", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_FileExit )

        self.m_menubar.Append( self.m_menuFile, u"File" )

        self.m_menuEdit = wx.Menu()
        self.m_menubar.Append( self.m_menuEdit, u"Edit" )

        self.m_menuAbout = wx.Menu()
        self.m_menubar.Append( self.m_menuAbout, u"About" )

        self.SetMenuBar( self.m_menubar )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar1 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL|wx.TB_TEXT )
        self.m_toolOpen = self.m_toolBar1.AddTool( wx.ID_ANY, u"Open", wx.Bitmap( self.GetRuntimeImagePath( u"../data/file-code-outline.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, u"Open a software update file", None )

        self.m_toolScan = self.m_toolBar1.AddTool( wx.ID_ANY, u"Scan", wx.Bitmap( self.GetRuntimeImagePath( u"../data/radar.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Scan for devices", u"Look for devices on CAN network", None )

        self.m_toolConnect = self.m_toolBar1.AddTool( wx.ID_ANY, u"Connect", wx.Bitmap( self.GetRuntimeImagePath( u"../data/lan-connect.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_CHECK, wx.EmptyString, u"Connect to selected device", None )

        self.m_toolDownload = self.m_toolBar1.AddTool( wx.ID_ANY, u"Download", wx.Bitmap( self.GetRuntimeImagePath( u"../data/download-circle.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, u"Update software on device", None )

        self.m_toolBar1.Realize()

        bSizer8.Add( self.m_toolBar1, 0, wx.EXPAND, 5 )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"File Info" ), wx.VERTICAL )

        self.m_filePicker = wx.FilePickerCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"All supported images (*.hex;*.bin)|*.bin;*.hex|Intel HEX files (*.hex)|*.hex|Binary files (*.bin)|*.bin", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN|wx.FLP_SMALL|wx.FLP_USE_TEXTCTRL )
        sbSizer1.Add( self.m_filePicker, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_propertyGridFileInfo = pg.PropertyGrid(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE)
        self.m_propertyGridFileInfo.Enable( False )

        self.m_propertyGridItem1 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Format", u"Format" ) )
        self.m_propertyGridItem2 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Size", u"Size" ) )
        self.m_propertyGridItem3 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Hash", u"Hash" ) )
        self.m_propertyGridItem4 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Version", u"Version" ) )
        self.m_propertyGridItem5 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Software Part Number", u"Software Part Number" ) )
        self.m_propertyGridItem6 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Hardware Part Number", u"Hardware Part Number" ) )
        sbSizer1.Add( self.m_propertyGridFileInfo, 0, wx.ALL|wx.EXPAND, 5 )


        bSizer13.Add( sbSizer1, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer8.Add( bSizer13, 1, wx.EXPAND, 5 )

        self.m_progressBar = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.m_progressBar.SetValue( 0 )
        bSizer8.Add( self.m_progressBar, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_richTextLog = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
        bSizer8.Add( self.m_richTextLog, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.m_nameList = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_nameListColumnAddress = self.m_nameList.AppendTextColumn( u"Address", wx.dataview.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_nameListColumnNAME = self.m_nameList.AppendTextColumn( u"Name", wx.dataview.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_nameListColumnNAME.GetRenderer().EnableEllipsize( wx.ELLIPSIZE_START );
        bSizer7.Add( self.m_nameList, 2, wx.ALL|wx.EXPAND, 5 )


        bSizer8.Add( bSizer7, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer8 )
        self.Layout()
        self.m_statusBar = self.CreateStatusBar( 3, wx.STB_SIZEGRIP, wx.ID_ANY )

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.fileExitClicked, id = self.m_FileExit.GetId() )
        self.Bind( wx.EVT_TOOL, self.toolOpenClicked, id = self.m_toolOpen.GetId() )
        self.Bind( wx.EVT_TOOL, self.toolScanClicked, id = self.m_toolScan.GetId() )
        self.Bind( wx.EVT_TOOL, self.toolConnectClicked, id = self.m_toolConnect.GetId() )
        self.Bind( wx.EVT_TOOL, self.toolDownloadClicked, id = self.m_toolDownload.GetId() )
        self.m_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.fileChanged )
        self.m_nameList.Bind( wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.addressSelectChanged, id = wx.ID_ANY )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def fileExitClicked( self, event ):
        event.Skip()

    def toolOpenClicked( self, event ):
        event.Skip()

    def toolScanClicked( self, event ):
        event.Skip()

    def toolConnectClicked( self, event ):
        event.Skip()

    def toolDownloadClicked( self, event ):
        event.Skip()

    def fileChanged( self, event ):
        event.Skip()

    def addressSelectChanged( self, event ):
        event.Skip()

    # Virtual image path resolution method. Override this in your derived class.
    def GetRuntimeImagePath( self, bitmap_path ):
        return bitmap_path


