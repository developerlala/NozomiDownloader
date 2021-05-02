import traceback

import requests
import wx
import re
import webbrowser

from wxglade_out import NozomiDownloader
from threading import Thread
from pathlib import Path
from nozomi import api


class NozomiDownloaderBody(NozomiDownloader):
    def __init__(self, *args, **kw):
        self.downloading = False
        super(NozomiDownloaderBody, self).__init__(*args, **kw)
        self.btnToggleStart.Bind(wx.EVT_BUTTON, self.startButtonClick)
        self.tbPositiveTags.Bind(wx.EVT_TEXT, self.tagChanged)
        self.tbNegativeTags.Bind(wx.EVT_TEXT, self.tagChanged)
        self.btnYoutube.Bind(wx.EVT_BUTTON, self.youtube)
        self.enableControls()

    def disableControls(self):
        self.tbPositiveTags.SetBackgroundColour(wx.LIGHT_GREY)
        self.tbNegativeTags.SetBackgroundColour(wx.LIGHT_GREY)
        self.tbDirectoryName.SetBackgroundColour(wx.LIGHT_GREY)
        self.tbPositiveTags.SetEditable(False)
        self.tbNegativeTags.SetEditable(False)
        self.tbDirectoryName.SetEditable(False)

    def enableControls(self):
        self.tbPositiveTags.SetBackgroundColour(wx.WHITE)
        self.tbNegativeTags.SetBackgroundColour(wx.WHITE)
        self.tbDirectoryName.SetBackgroundColour(wx.WHITE)
        self.tbPositiveTags.SetEditable(True)
        self.tbNegativeTags.SetEditable(True)
        self.tbDirectoryName.SetEditable(True)

    def youtube(self, event):
        webbrowser.open('https://youtube.com/c/devlala')

    def startButtonClick(self, event):
        if not self.tbPositiveTags.GetLineText(0):
            wx.MessageBox("태그를 입력하세요")
            return

        if self.downloading:
            self.btnToggleStart.SetLabelText('Start Download')
            self.downloading = False
            self.print("Download Stopped")
            self.enableControls()
        else:
            self.btnToggleStart.SetLabelText('Stop Download')
            self.downloading = True
            self.startDownload()
            self.disableControls()

    def tagChanged(self, event: wx.CommandEvent):
        p = self.tbPositiveTags.GetLineText(0)
        n = self.tbNegativeTags.GetLineText(0)

        if (not p) and (not n):
            self.tbDirectoryName.SetLabelText("Downloads")
        else:
            pattern = re.compile('\s*,\s*')
            positive_tags = pattern.split(p)
            directoryName = ','.join(positive_tags);
            if len(n) > 0:
                negative_tags = pattern.split(n)
                directoryName = directoryName + ' Not ' + ','.join(negative_tags)
            self.tbDirectoryName.SetLabelText(directoryName.strip())

    def startDownload(self):
        pattern = re.compile('\s*,\s*')
        p = self.tbPositiveTags.GetLineText(0)
        n = self.tbNegativeTags.GetLineText(0)

        positive_tags = pattern.split(p) if p else None
        negative_tags = pattern.split(n) if n else None

        downloadThread = Thread(target=self.run, args=(self.tbDirectoryName.GetLineText(0), positive_tags, negative_tags))
        downloadThread.start()

    def run(self, directory, positive_tags, negative_tags=None):
        self.print("Download Start")
        try:
            for post in api.get_posts(positive_tags, negative_tags):
                if not self.downloading: return
                self.print("Post-width:" + str(post.width))
                self.print("Post-height:" + str(post.height))
                self.print("Post-id:" + str(post.sourceid))
                retry = 3
                while True:
                    try:
                        result = api.download_media(post, Path(Path.cwd(), directory))
                        if result: self.print(post.imageurl + ": Download Success")
                        else: self.print(post.imageurl + ": File Already Exists")
                        break;
                    except Exception as e:
                        if retry == 0: break;
                        self.print(post.imageurl + ": IO Error (Read Timeout... or something) retry " + str(retry))
                        retry = retry - 1

            wx.MessageBox("다운로드 완료")
            self.downloading = False
            self.btnToggleStart.SetLabelText('Start Download')
            self.enableControls()
        except Exception as e:
            traceback.print_exc()
            wx.MessageBox("태그검색결과 오류")
            self.downloading = False
            self.btnToggleStart.SetLabelText('Start Download')
            self.enableControls()

    def print(self, string):
        if self.tbConsole.GetLineText(0):
            self.tbConsole.AppendText("\n")
        self.tbConsole.AppendText(string)


def main():
    app = wx.App()
    ex = NozomiDownloaderBody(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
