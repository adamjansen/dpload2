import os
import time
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

import can
import intelhex

import wx

from ..dpload import DPLoad
from ..image import Image, ImageTlvType

from .gui import MainWindow, SettingsDialog, AboutDialog

BITRATE_STRINGS = {
    100000: "100 kbps",
    125000: "125 kbps",
    250000: "250 kbps",
    500000: "500 kbps",
    1000000: "1 Mbps",
}

BITRATE_VALUES = {value: key for (key, value) in BITRATE_STRINGS.items()}

root_dir = os.path.dirname(sys.modules[DPLoad.__module__].__file__)


def translate_image_path(_, path):
    return os.path.normpath(os.path.join(root_dir, "gui", path))


AboutDialog.GetRuntimeImagePath = translate_image_path


class ConfiguredSettingsDialog(SettingsDialog):
    GetRuntimeImagePath = translate_image_path

    def __init__(self, parent, config, *args, **kwargs):
        SettingsDialog.__init__(self, parent, *args, **kwargs)
        self.config = config
        interface = self.config.Read("/CAN/Interface", "virtual")
        self.m_choiceDriver.SetSelection(self.m_choiceDriver.FindString(interface))

        self.UpdateChannelChoices()

        bitrate = self.config.ReadInt("/CAN/Bitrate", 250000)
        bitrate_index = self.m_choiceBitrate.FindString(BITRATE_STRINGS[bitrate])
        print(f"bitrate={bitrate} index={bitrate_index}")
        self.m_choiceBitrate.SetSelection(bitrate_index)

    def OnDriverChange(self, event):
        self.UpdateChannelChoices()

    def UpdateChannelChoices(self):
        self.m_choiceChannel.Clear()
        interface = self.m_choiceDriver.GetString(self.m_choiceDriver.GetSelection())
        channels = [
            config["channel"]
            for config in can.detect_available_configs(interfaces=[interface])
        ]
        channel = self.config.Read("/CAN/Channel", "can0")
        self.m_choiceChannel.AppendItems(channels)
        channel_index = self.m_choiceChannel.FindString(channel)
        if channel_index == wx.NOT_FOUND:
            channel_index = 0
        self.m_choiceChannel.SetSelection(channel_index)

    def ShowModal(self):
        result = SettingsDialog.ShowModal(self)
        if result == wx.ID_OK:
            # Save configured values
            interface = self.m_choiceDriver.GetString(
                self.m_choiceDriver.GetSelection()
            )

            self.config.Write("/CAN/Interface", interface)
            channel = self.m_choiceChannel.GetString(
                self.m_choiceChannel.GetSelection()
            )
            self.config.Write("/CAN/Channel", channel)
            bitrate_text = self.m_choiceBitrate.GetString(
                self.m_choiceBitrate.GetSelection()
            )
            bitrate = BITRATE_VALUES[bitrate_text]
            self.config.WriteInt("/CAN/Bitrate", bitrate)
            print(f"bitrate => {bitrate}")
            return result


class GUI(MainWindow):
    GetRuntimeImagePath = translate_image_path

    def __init__(self, parent):
        MainWindow.__init__(self, parent)

        self.image = Image()
        self.da = None

        self.fileHistory = wx.FileHistory()
        self.fileHistory.UseMenu(self.m_menuFile)
        self.Bind(
            wx.EVT_MENU_RANGE, self.OnFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9
        )
        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

        self.m_toolConnect.SetDisabledBitmap(
            wx.Bitmap(self.GetRuntimeImagePath("../data/lan-pending-32.png"))
        )
        self.m_toolBar1.ToggleTool(self.m_toolConnect.GetId(), False)
        self.m_toolBar1.EnableTool(self.m_toolConnect.GetId(), False)
        self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), False)

        self._load_config()

        self.bus = can.interface.Bus(
            bustype=self.can_interface,
            channel=self.can_channel,
            bitrate=self.can_bitrate,
        )
        self.dpload = DPLoad(bus=self.bus, sa=self.sa)

    def _load_config(self):
        data_dir = wx.StandardPaths.Get().GetUserDataDir()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.config = wx.FileConfig(localFilename=os.path.join(data_dir, "dpload.cfg"))

        self.sa = self.config.ReadInt("/J1939/SA", 39)
        self.can_interface = self.config.Read("/CAN/Interface", "virtual")
        self.can_channel = self.config.Read("/CAN/Channel", "can0")
        self.can_bitrate = self.config.ReadInt("/CAN/Bitrate", 250000)

        self.fileHistory.Load(self.config)

    def OnHelpAboutClicked(self, evt):
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSettingsClicked(self, evt):
        dlg = ConfiguredSettingsDialog(self, self.config)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Todo: update configuration
                self.info("updating config")
            else:
                # Changes cancelled
                self.info("config cancelled")
        finally:
            dlg.Destroy()

    def OnFileHistory(self, evt):
        fileNum = evt.GetId() - wx.ID_FILE1
        path = self.fileHistory.GetHistoryFile(fileNum)
        self.m_filePicker.SetPath(path)
        evt = wx.FileDirPickerEvent(
            wx.EVT_FILEPICKER_CHANGED.typeId, self, wx.ID_ANY, path
        )
        self.fileChanged(evt)

    def Cleanup(self, *args):
        self.fileHistory.Save(self.config)
        self.config.Flush()

    def log(self, msg, level=logging.INFO):
        colors = {
            logging.DEBUG: wx.LIGHT_GREY,
            logging.INFO: wx.BLUE,
            logging.WARN: wx.YELLOW,
            logging.ERROR: wx.RED,
        }
        rt = self.m_richTextLog
        rt.BeginTextColour(colors[level])
        name = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARN: "WARN",
            logging.ERROR: "ERROR",
        }[level]
        rt.WriteText(f"{name}: ")
        rt.EndTextColour()
        rt.WriteText(f"{msg}\n")

        rt.ShowPosition(-1)

    def debug(self, msg):
        self.log(msg, level=logging.DEBUG)

    def info(self, msg):
        self.log(msg, level=logging.INFO)

    def error(self, msg):
        self.log(msg, level=logging.ERROR)

    def warn(self, msg):
        self.log(msg, level=logging.WARN)

    def fileExitClicked(self, event):
        self.log("Exit!")

    def toolOpenClicked(self, event):
        filePickerButton = self.m_filePicker.GetChildren()[1]
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, filePickerButton.GetId())
        wx.PostEvent(filePickerButton, evt)

    def updateFileInfo(self):
        format = (
            "Intel HEX records file"
            if self.image.filename.lower().endswith(".hex")
            else "Raw binary data"
        )
        properties = {
            "Format": format,
            "Size": self.image.size,
            "Version": self.image.version,
            "Hash": self.image.get_tlv(ImageTlvType.SHA256),
            "Software Part Number": self.image.get_tlv(ImageTlvType.DP_SW_PART_NUMBER),
            "Hardware Part Number": self.image.get_tlv(ImageTlvType.DP_HW_PART_NUMBER),
        }
        for label, value in properties.items():
            self.m_propertyGridFileInfo.GetPropertyByName(label).SetValue(value)

    def fileChanged(self, event):
        path = event.GetPath()
        self.info(f"Processing {path}")
        self.fileHistory.AddFileToHistory(path)
        self.m_statusBar.SetStatusText(os.path.basename(path), 0)

        if self.m_toolBar1.GetToolState(self.m_toolConnect.GetId()):
            self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
        self.image.load(path)
        self.updateFileInfo()

    def toolDownloadClicked(self, event):
        self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), False)
        self.info("Erasing flash")
        wx.Yield()
        try:
            self.dpload.erase(da=self.da, timeout=5.0)
        except ValueError:
            self.error("Unexpected response")
            self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
            return
        except TimeoutError:
            self.error("Timeout waiting for response")
            self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
            return
        wx.Yield()

        self.dpload.dm13_control(True)
        start = time.time()
        total_bytes = 0
        chunk = b""
        n = 0
        lines = self.image.hexdata.splitlines()
        self.m_progressBar.SetRange(len(lines))
        self.info(f"Programming {len(lines)} records")
        for lineNum, lineText in enumerate(lines):
            self.m_progressBar.SetValue(lineNum)
            record = bytes.fromhex(lineText[1:].strip())
            n += 1
            chunk += record
            if n == 8:
                total_bytes += len(chunk)
                try:
                    self.dpload.program_flash(chunk, da=self.da, timeout=2.0)
                except TimeoutError:
                    self.error("Timeout waiting for response! Programming failed.")
                    self.dpload.dm13_control(False)
                    return
                speed_kb_per_sec = (total_bytes / 1024) / (time.time() - start)
                self.m_statusBar.SetStatusText(f"{speed_kb_per_sec:0.1f} kByte/sec", 1)
                chunk = b""
                n = 0
            wx.Yield()
        if n:
            try:
                self.dpload.program_flash(chunk, da=self.da, timeout=2.0)
            except TimeoutError:
                self.error("Timeout waiting for response! Programming failed.")
                self.dpload.dm13_control(False)
                self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
                return
        wx.Yield()
        elapsed = time.time() - start
        self.info(f"Programming address {self.da} complete in {elapsed:0.3f} seconds")
        self.dpload.jump(da=self.da)

        self.dpload.dm13_control(False)
        self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)

    def toolScanClicked(self, event):
        self.info("Scanning for devices")
        nodes = self.dpload.scan()

        self.m_nameList.DeleteAllItems()
        for addr, name in nodes:
            self.m_nameList.AppendItem([f"{addr} ({addr:02x})", f"{name.hex()}", False])

        self.info(f"Found {len(nodes)} active nodes")

    def addressSelectChanged(self, event):
        row = self.m_nameList.GetSelectedRow()
        if row == wx.NOT_FOUND:
            self.m_toolBar1.EnableTool(self.m_toolConnect.GetId(), False)
            self.da = None
        else:
            self.m_toolBar1.EnableTool(self.m_toolConnect.GetId(), True)
            addr = int(self.m_nameList.GetTextValue(row, 0).split(" ")[0])
            self.da = addr
            self.info(f"Selected address {addr}")

    def toolConnectClicked(self, event):
        if self.m_toolBar1.GetToolState(self.m_toolConnect.GetId()):
            self.m_toolBar1.ToggleTool(self.m_toolConnect.GetId(), True)
            print(f"image_size={self.image.size}")
            if self.image.size > 0:
                self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)

            self.dpload.enter(da=self.da)
            self.info(f"Connecting to {self.da}")
        else:
            self.m_toolBar1.ToggleTool(self.m_toolDownload.GetId(), False)

            self.m_toolBar1.ToggleTool(self.m_toolConnect.GetId(), False)
            self.info(f"Disconnecting from {self.da}")

        #    # clear labels
        #    self.m_labelAppVersion.SetLabel("")
        #    self.m_labelOemVersion.SetLabel("")
        #    self.m_labelPartNumber.SetLabel("")
        # addr = int(self.m_nameList.GetTextValue(row, 0).split(" ")[0])
        # self.da = addr
        # self.info(f"Selected address {addr}")
        # app_major, app_minor = self.dpload.get_app_info(da=addr, timeout=0.5)
        # self.m_labelAppVersion.SetLabel(f"{app_major:02d}.{app_minor:02d}")
        # sa, pn, oem_major, oem_minor = self.dpload.get_oem_info(da=addr, timeout=0.5)
        # self.m_labelOemVersion.SetLabel(f"{oem_major:02d}.{oem_minor:02d}")
        # self.m_labelPartNumber.SetLabel(f"{pn}")


if __name__ == "__main__":
    app = wx.App(redirect=True)
    app.AppDisplayName = "DPLoader2"
    app.AppName = "dpload2"
    app.VendorDisplayName = "Data Panel Corporation"
    app.VendorName = "datapanel"

    try:
        frame = GUI(None)
        frame.Show(True)
        app.MainLoop()
    except:
        import traceback

        message = "".join(traceback.format_exception(*sys.exc_info()))
        dialog = wx.MessageDialog(None, message, "Error!", wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()
