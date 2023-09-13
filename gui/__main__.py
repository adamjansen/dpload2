import os
import time
import sys
import logging


import can
import intelhex

import wx

from ..dpload import DPLoad
from ..image import Image, ImageTlvType

from .gui import MainWindow, SettingsDialog, AboutDialog

logging.basicConfig(level=logging.DEBUG)


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
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def OnFileHistory(self, evt):
        fileNum = evt.GetId() - wx.ID_FILE1
        path = self.fileHistory.GetHistoryFile(fileNum)
        self.OpenFile(path)

    def Cleanup(self, *args):
        self.fileHistory.Save(self.config)
        self.config.Flush()

    def fileExitClicked(self, event):
        # TODO
        sys.exit(0)

    def toolOpenClicked(self, event):
        dlg = wx.FileDialog(
            self,
            message="Select a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="All supported images (*.hex;*.bin)|*.bin;*.hex|Intel HEX files (*.hex)|*.hex|Binary files (*.bin)|*.bin",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST,
        )
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        path = dlg.GetPaths()[0]
        self.OpenFile(path)

    def OpenFile(self, path):
        self.fileHistory.AddFileToHistory(path)
        self.m_statusBar.SetStatusText(os.path.basename(path), 0)

        if self.m_toolBar1.GetToolState(self.m_toolConnect.GetId()):
            self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
        self.image.load(path)
        format = (
            "Intel HEX records file"
            if self.image.filename.lower().endswith(".hex")
            else "Raw binary data"
        )
        properties = {
            "File Path": self.image.filename,
            "Format": format,
            "Size": self.image.size,
            "Version": self.image.version,
            "Hash": self.image.get_tlv(ImageTlvType.SHA256),
            "Software Part Number": self.image.get_tlv(ImageTlvType.DP_SW_PART_NUMBER),
            "Hardware Part Number": self.image.get_tlv(ImageTlvType.DP_HW_PART_NUMBER),
            "Security Counter": self.image.get_tlv(ImageTlvType.SEC_CNT),
        }
        for label, value in properties.items():
            self.m_propertyGridFileInfo.GetPropertyByName(label).SetValue(value)

    def toolDownloadClicked(self, event):
        self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), False)
        self.m_statusBar.SetStatusText("Erasing flash...", 0)
        wx.Yield()
        try:
            self.dpload.erase(da=self.da, timeout=5.0)
        except ValueError:
            self.m_statusBar.SetStatusText("Unexpected response", 0)
            self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
            return
        except TimeoutError:
            self.m_statusBar.SetStatusText("Timeout waiting for response", 0)
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
        self.m_statusBar.SetStatusText(f"Programming {len(lines)} records")
        for lineNum, lineText in enumerate(lines):
            self.m_progressBar.SetValue(lineNum)
            record = bytes.fromhex(lineText[1:].strip())
            n += 1
            chunk += record
            if n == 16:
                total_bytes += len(chunk)
                try:
                    self.dpload.program_flash(chunk, da=self.da, timeout=2.0)
                except TimeoutError:
                    self.m_statusBar.SetStatusText(
                        "Timeout waiting for response. Programming failed"
                    )
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
                self.m_statusBar.SetStatusText(
                    "Timeout waiting for response. Programming failed"
                )
                self.dpload.dm13_control(False)
                self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)
                return
        wx.Yield()
        elapsed = time.time() - start
        self.m_statusBar.SetStatusText(
            f"Programmed {self.da} in {elapsed:0.3f} seconds"
        )
        wx.Yield()
        self.dpload.jump(da=self.da)

        self.dpload.dm13_control(False)
        self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)

    def toolScanClicked(self, event):
        self.m_statusBar.SetStatusText("Scanning for devices...")
        wx.Yield()
        nodes = self.dpload.scan()

        self.m_nameList.DeleteAllItems()
        root = self.m_nameList.GetRootItem()
        for addr, name in nodes:
            node = self.m_nameList.AppendItem(root, f"{addr} ({addr:02x})")
            name_node = self.m_nameList.AppendItem(node, f"NAME: {name.hex().upper()}")
            name64 = int.from_bytes(name, 'little')
            decoded_name = {
                "Identity": name64 & 0x1FFFFF,
                "Manufacturer Code": (name64 >> 21) & 0x7FF,
                "ECU Instance": (name64 >> 32) & 0x7,
                "Function Instance": (name64 >> 35) & 0x1f,
                "Function": (name64 >> 49) & 0x7f,
                "Vehicle System": (name64 >> 56) & 0xf,
                "Industry Group": (name64 >> 60) & 0x7,
                "Self Configurable Address": (name64 >> 63) & 0x1,
            }

            for label, value in decoded_name.items():
                self.m_nameList.AppendItem(name_node, f"{label}: {value}")

            ecu_info = self.dpload.ecu_info(addr)

            # The last field is empty, or contains fields we can't interpret
            pn, sn, location, type, mfg_name, hw_id, _ = ecu_info.split('*', 6)
            if pn:
                self.m_nameList.AppendItem(node, f"Part Number: {pn}")
            if hw_id:
                self.m_nameList.AppendItem(node, f"HW Revision: {hw_id}")
            if type:
                self.m_nameList.AppendItem(node, f"Type: {type}")
            if sn:
                self.m_nameList.AppendItem(node, f"Serial Number: {sn}")
            if mfg_name:
                self.m_nameList.AppendItem(node, f"Manufacturer: {mfg_name}")

            software_node = self.m_nameList.AppendItem(node, f"Software Versions")
            soft_info = self.dpload.soft_info(addr)
            components = soft_info.split('*')[:-1]
            for component in components:
                name, version = component.split(' ', 1)
                self.m_nameList.AppendItem(software_node, f"{name}: {version}")

        self.m_statusBar.SetStatusText(f"Found {len(nodes)} active nodes")

    def addressSelectChanged(self, event):
        item = self.m_nameList.GetSelection()
        if item == wx.NOT_FOUND:
            self.m_toolBar1.EnableTool(self.m_toolConnect.GetId(), False)
            self.da = None
            return

        self.m_toolBar1.EnableTool(self.m_toolConnect.GetId(), True)

        while (parent := self.m_nameList.GetItemParent(item)) != self.m_nameList.GetRootItem():
            item = parent

        text = self.m_nameList.GetItemText(item)

        addr = int(text.split(" ", 1)[0])
        self.da = addr
        self.m_statusBar.SetStatusText(f"Selected address {addr}")

    def toolConnectClicked(self, event):
        if self.m_toolBar1.GetToolState(self.m_toolConnect.GetId()):
            self.m_toolBar1.ToggleTool(self.m_toolConnect.GetId(), True)
            if self.image.size > 0:
                self.m_toolBar1.EnableTool(self.m_toolDownload.GetId(), True)

            self.dpload.enter(da=self.da)
            self.m_statusBar.SetStatusText(f"Connecting to {self.da}")
        else:
            self.m_toolBar1.ToggleTool(self.m_toolDownload.GetId(), False)

            self.m_toolBar1.ToggleTool(self.m_toolConnect.GetId(), False)
            self.m_statusBar.SetStatusText(f"Disconnecting from {self.da}")


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
