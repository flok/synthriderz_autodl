# stuff for downloading
import os, requests, threading
from queue import Queue

# some registry shinenigang
from winreg import HKEY_LOCAL_MACHINE, OpenKey, QueryValueEx, CloseKey, KEY_READ

class DownloadThread(threading.Thread):
    def __init__(self, queue, destfolder):
        super(DownloadThread, self).__init__()
        self.queue = queue
        self.destfolder = destfolder
        self.daemon = True

    def run(self):
        while True:
            item = self.queue.get()
            try:
                self.download_url('http://synthriderz.com{}'.format(item['download_url']), item['filename_original'])
            except Exception as e:
                print("Exception {}", e)
            self.queue.task_done()

    def download_url(self, url, name):
        dest = os.path.join(self.destfolder, name)
        print(dest)
        data = requests.get(url)
        with open(dest, 'wb') as f:
            f.write(data.content)
        
def download(urls, destfolder, numthreads=4):
    queue = Queue()
    for url in urls:
        queue.put(url)

    for i in range(numthreads):
        t = DownloadThread(queue, destfolder)
        t.start()

    queue.join()

def getSynthRiderInstallFolder():
    try:
        registry_key = OpenKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 885000', 0,
                                       KEY_READ)
        value, _ = QueryValueEx(registry_key, r'InstallLocation')
        CloseKey(registry_key)
        return value
    except WindowsError:
        return None

if __name__ == "__main__":
    # get Synth Rider install directory from registry
    folder = getSynthRiderInstallFolder()
    folder += r'\CustomSongs' # add CustomSongs folder to it
    # get songs through the SynthRiderz api
    data = requests.get('https://synthriderz.com/api/beatmaps').json()
    # start downloader with data and destination folder
    download(data, folder)