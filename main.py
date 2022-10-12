import os
import requests
import datetime
import tempfile
import zipfile

from pathlib import Path


# URL was copied from https://s3-us-west-1.amazonaws.com/umbrella-static/index.html
TOP_DOMAINS_URL = "http://s3-us-west-1.amazonaws.com/umbrella-static/"


class TopDomainsFile:
    _FILE_NAME = "top-1m.csv"
    _DATED_FILE_NAME_TEMPLATE = "top-1m-{}-{:02d}-01.csv.zip"
    _TMP_DIR = tempfile.gettempdir()

    def __init__(self):
        today = datetime.date.today()
        month = 12 if today.month == 1 else today.month-1
        self.dated_file_name = self._DATED_FILE_NAME_TEMPLATE.format(today.year, month)
        self._file_path = Path(self._TMP_DIR) / self._FILE_NAME

        if self._file_path.is_file():
            print("\nTop domains file already exists.")
            delete_file = (input("Do you want to reload it? (y/N): ").strip() or "N") in "yY"
            if delete_file:
                os.remove(self._file_path)

        if not self._file_path.is_file():
            downloaded_file = self.download()
            zipfile.ZipFile(downloaded_file).extract(self._FILE_NAME, self._TMP_DIR)
            os.remove(downloaded_file)

        self._file = open(self._file_path)

    def download(self):
        print("\nDownloading top domains file, please wait...")
        download_url = f"{TOP_DOMAINS_URL}{self.dated_file_name}"
        print(download_url)
        response = requests.get(download_url, allow_redirects=True)

        if response.status_code == 200:
            zip_file_path = Path(self._TMP_DIR) / self.dated_file_name
            open(zip_file_path, "wb").write(response.content)
            return zip_file_path

        raise RuntimeError(f"Can't download domains file:\nStatus code: {response.status_code}")

    def get_domains(self):
        return map(lambda dom_str: dom_str.split(",")[1], self._file.readlines())

    def filter_and_save(self, save_path: str, filter_func):
        with open(save_path, "w") as s_f:
            s_f.writelines(filter(filter_func, self.get_domains()))


if __name__ == '__main__':
    tld = input(f"Please enter TLD (for example '.com'): ").strip() + "\n"
    top_domains_file = TopDomainsFile()

    print(f"\nSaving top '{tld.strip()}' domains...")
    top_domains_file.filter_and_save("top_domains.csv", lambda l: l.endswith(tld))

    print("Done!!!")
