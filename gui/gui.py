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
import wx.adv

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
        self.m_FileExit.SetBitmap( wx.Bitmap( self.GetRuntimeImagePath( u"../data/exit-to-app-16.png" ), wx.BITMAP_TYPE_ANY ) )
        self.m_menuFile.Append( self.m_FileExit )

        self.m_menubar.Append( self.m_menuFile, u"File" )

        self.m_menuEdit = wx.Menu()
        self.m_menuItem2 = wx.MenuItem( self.m_menuEdit, wx.ID_ANY, u"Settings", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuItem2.SetBitmap( wx.Bitmap( self.GetRuntimeImagePath( u"../data/cog-16.png" ), wx.BITMAP_TYPE_ANY ) )
        self.m_menuEdit.Append( self.m_menuItem2 )

        self.m_menubar.Append( self.m_menuEdit, u"Edit" )

        self.m_menuHelp = wx.Menu()
        self.m_menuHelpAbout = wx.MenuItem( self.m_menuHelp, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuHelpAbout.SetBitmap( wx.Bitmap( self.GetRuntimeImagePath( u"../data/information-outline-16.png" ), wx.BITMAP_TYPE_ANY ) )
        self.m_menuHelp.Append( self.m_menuHelpAbout )

        self.m_menubar.Append( self.m_menuHelp, u"Help" )

        self.SetMenuBar( self.m_menubar )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar1 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL|wx.TB_TEXT )
        self.m_toolOpen = self.m_toolBar1.AddTool( wx.ID_ANY, u"Open", wx.Bitmap( self.GetRuntimeImagePath( u"../data/file-code-outline-32.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, u"Open a software update file", None )

        self.m_toolScan = self.m_toolBar1.AddTool( wx.ID_ANY, u"Scan", wx.Bitmap( self.GetRuntimeImagePath( u"../data/radar-32.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Scan for devices", u"Look for devices on CAN network", None )

        self.m_toolConnect = self.m_toolBar1.AddTool( wx.ID_ANY, u"Connect", wx.Bitmap( self.GetRuntimeImagePath( u"../data/lan-connect-32.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_CHECK, wx.EmptyString, u"Connect to selected device", None )

        self.m_toolDownload = self.m_toolBar1.AddTool( wx.ID_ANY, u"Download", wx.Bitmap( self.GetRuntimeImagePath( u"../data/download-circle-32.png" ), wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, u"Update software on device", None )

        self.m_toolBar1.Realize()

        bSizer8.Add( self.m_toolBar1, 0, wx.EXPAND, 5 )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"File Info" ), wx.VERTICAL )

        self.m_filePicker = wx.FilePickerCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"All supported images (*.hex;*.bin)|*.bin;*.hex|Intel HEX files (*.hex)|*.hex|Binary files (*.bin)|*.bin", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN|wx.FLP_SMALL|wx.FLP_USE_TEXTCTRL )
        sbSizer1.Add( self.m_filePicker, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_propertyGridFileInfo = pg.PropertyGrid(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE|wx.propgrid.PG_HIDE_MARGIN|wx.propgrid.PG_TOOLTIPS)
        self.m_propertyGridFileInfo.SetExtraStyle( wx.propgrid.PG_EX_HELP_AS_TOOLTIPS )
        self.m_propertyGridItem1 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Format", u"Format" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem1, u"Type of software update file" )
        self.m_propertyGridItem2 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Size", u"Size" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem2, u"Total length, in bytes" )
        self.m_propertyGridItem3 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Hash", u"Hash" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem3, u"SHA256 digest for checking data integrity" )
        self.m_propertyGridItem4 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Version", u"Version" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem4, u"Software revision information" )
        self.m_propertyGridItem5 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Software Part Number", u"Software Part Number" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem5, u"Data Panel part number for firmware" )
        self.m_propertyGridItem6 = self.m_propertyGridFileInfo.Append( pg.StringProperty( u"Hardware Part Number", u"Hardware Part Number" ) )
        self.m_propertyGridFileInfo.SetPropertyHelpString( self.m_propertyGridItem6, u"Compatible Data Panel products" )
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
        self.Bind( wx.EVT_MENU, self.OnSettingsClicked, id = self.m_menuItem2.GetId() )
        self.Bind( wx.EVT_MENU, self.OnHelpAboutClicked, id = self.m_menuHelpAbout.GetId() )
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

    def OnSettingsClicked( self, event ):
        event.Skip()

    def OnHelpAboutClicked( self, event ):
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


###########################################################################
## Class SettingsDialog
###########################################################################

class SettingsDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Settings", pos = wx.DefaultPosition, size = wx.Size( 410,452 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.Size( -1,-1 ), wx.DefaultSize )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_listbook1 = wx.Listbook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT )
        m_listbook1ImageSize = wx.Size( 32,32 )
        m_listbook1Index = 0
        m_listbook1Images = wx.ImageList( m_listbook1ImageSize.GetWidth(), m_listbook1ImageSize.GetHeight() )
        self.m_listbook1.AssignImageList( m_listbook1Images )
        self.m_scrolledWindow1 = wx.ScrolledWindow( self.m_listbook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow1.SetScrollRate( 5, 5 )
        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Hardware" ), wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText5 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Driver", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )

        bSizer9.Add( self.m_staticText5, 0, wx.ALL, 5 )

        m_choiceDriverChoices = [ u"socketcan", u"socketcand", u"pcan", u"virtual", wx.EmptyString ]
        self.m_choiceDriver = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceDriverChoices, 0 )
        self.m_choiceDriver.SetSelection( 3 )
        bSizer9.Add( self.m_choiceDriver, 1, wx.ALL, 5 )


        sbSizer2.Add( bSizer9, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText7 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Channel", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        bSizer11.Add( self.m_staticText7, 0, wx.ALL, 5 )

        m_choiceChannelChoices = []
        self.m_choiceChannel = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceChannelChoices, 0 )
        self.m_choiceChannel.SetSelection( 0 )
        bSizer11.Add( self.m_choiceChannel, 1, wx.ALL, 5 )


        sbSizer2.Add( bSizer11, 1, wx.EXPAND, 5 )

        bSizer10 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText6 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Bitrate", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )

        bSizer10.Add( self.m_staticText6, 0, wx.ALL, 5 )

        m_choiceBitrateChoices = [ u"100 kbps", u"125 kbps", u"250 kbps", u"500 kbps", u"1 Mbps" ]
        self.m_choiceBitrate = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceBitrateChoices, 0 )
        self.m_choiceBitrate.SetSelection( 2 )
        bSizer10.Add( self.m_choiceBitrate, 1, wx.ALL, 5 )


        sbSizer2.Add( bSizer10, 1, wx.EXPAND, 5 )

        self.m_checkBoxConnectAtStartup = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Connect at startup", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_checkBoxConnectAtStartup, 0, wx.ALL, 5 )


        sbSizer2.Add( ( 0, 0), 3, wx.EXPAND, 5 )


        self.m_scrolledWindow1.SetSizer( sbSizer2 )
        self.m_scrolledWindow1.Layout()
        sbSizer2.Fit( self.m_scrolledWindow1 )
        self.m_listbook1.AddPage( self.m_scrolledWindow1, u"Interface", True )
        m_listbook1Bitmap = wx.Bitmap( self.GetRuntimeImagePath( u"../data/connection-32.png" ), wx.BITMAP_TYPE_ANY )
        if ( m_listbook1Bitmap.IsOk() ):
            m_listbook1Images.Add( m_listbook1Bitmap )
            self.m_listbook1.SetPageImage( m_listbook1Index, m_listbook1Index )
            m_listbook1Index += 1

        self.m_scrolledWindow2 = wx.ScrolledWindow( self.m_listbook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow2.SetScrollRate( 5, 5 )
        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow2, wx.ID_ANY, u"Protocol Settings" ), wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Address", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )

        bSizer5.Add( self.m_staticText2, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_spinAddress = wx.SpinCtrl( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 250, 39 )
        bSizer5.Add( self.m_spinAddress, 1, wx.ALL, 5 )


        sbSizer3.Add( bSizer5, 1, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText4 = wx.StaticText( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Priority", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        bSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.EXPAND, 5 )

        m_choicePriorityChoices = [ u"7 - Lowest", u"6 - Lower", u"5 - Low", u"4 - Normal", u"3  - Elevated", u"2 - High", u"1 - Higher", u"0 - Highest", wx.EmptyString, wx.EmptyString ]
        self.m_choicePriority = wx.Choice( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choicePriorityChoices, 0 )
        self.m_choicePriority.SetSelection( 2 )
        bSizer7.Add( self.m_choicePriority, 1, wx.ALL|wx.EXPAND, 5 )


        sbSizer3.Add( bSizer7, 1, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( sbSizer3.GetStaticBox(), wx.ID_ANY, u"NAME", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )

        bSizer6.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.m_textNAME = wx.TextCtrl( sbSizer3.GetStaticBox(), wx.ID_ANY, u"0000000000000000", wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP )
        self.m_textNAME.SetMaxLength( 16 )
        bSizer6.Add( self.m_textNAME, 1, wx.ALL, 5 )


        sbSizer3.Add( bSizer6, 1, wx.EXPAND, 5 )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )


        bSizer8.Add( ( 0, 0), 0, wx.EXPAND, 5 )

        self.m_checkBoxSendAddressClaim = wx.CheckBox( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Send address claim", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_checkBoxSendAddressClaim, 1, wx.ALL|wx.SHAPED, 5 )


        sbSizer3.Add( bSizer8, 1, wx.EXPAND, 5 )


        sbSizer3.Add( ( 0, 0), 4, wx.ALL|wx.EXPAND, 5 )


        self.m_scrolledWindow2.SetSizer( sbSizer3 )
        self.m_scrolledWindow2.Layout()
        sbSizer3.Fit( self.m_scrolledWindow2 )
        self.m_listbook1.AddPage( self.m_scrolledWindow2, u"Protocol", False )
        m_listbook1Bitmap = wx.Bitmap( self.GetRuntimeImagePath( u"../data/protocol-32.png" ), wx.BITMAP_TYPE_ANY )
        if ( m_listbook1Bitmap.IsOk() ):
            m_listbook1Images.Add( m_listbook1Bitmap )
            self.m_listbook1.SetPageImage( m_listbook1Index, m_listbook1Index )
            m_listbook1Index += 1


        bSizer4.Add( self.m_listbook1, 1, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 5 )


        bSizer13.Add( bSizer4, 10, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 5 )

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();

        bSizer13.Add( m_sdbSizer1, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer13 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_choiceDriver.Bind( wx.EVT_CHOICE, self.OnDriverChange )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def OnDriverChange( self, event ):
        event.Skip()

    # Virtual image path resolution method. Override this in your derived class.
    def GetRuntimeImagePath( self, bitmap_path ):
        return bitmap_path


###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About DPLoader2", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( self.GetRuntimeImagePath( u"../data/datapanel-logo.png" ), wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer13.Add( self.m_bitmap1, 0, 0, 5 )

        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"<big><b>DPLoader2 v0.0.0</b></big>\n\nSoftware update utility for Data Panel I/O blocks", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText12.SetLabelMarkup( u"<big><b>DPLoader2 v0.0.0</b></big>\n\nSoftware update utility for Data Panel I/O blocks" )
        self.m_staticText12.Wrap( -1 )

        bSizer13.Add( self.m_staticText12, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"<b>Data Panel Corporation</b>\n<small>181 Cheshire Ln. Suite 300\nPlymouth, MN 55441 USA</small>", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText11.SetLabelMarkup( u"<b>Data Panel Corporation</b>\n<small>181 Cheshire Ln. Suite 300\nPlymouth, MN 55441 USA</small>" )
        self.m_staticText11.Wrap( -1 )

        bSizer13.Add( self.m_staticText11, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_hyperlink1 = wx.adv.HyperlinkCtrl( self, wx.ID_ANY, u"datapanel.com", u"http://www.datapanel.com", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
        bSizer13.Add( self.m_hyperlink1, 0, wx.ALL|wx.EXPAND, 5 )

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        m_sdbSizer2.Realize();

        bSizer13.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer13 )
        self.Layout()
        bSizer13.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass

    # Virtual image path resolution method. Override this in your derived class.
    def GetRuntimeImagePath( self, bitmap_path ):
        return bitmap_path


