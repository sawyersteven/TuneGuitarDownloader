import requests
import re
import os

# CONFIG -------------------- #

# Change this to download all gp5s to this directory
# Leave as None to be asked each time where to download files
default_download_dir = None
# --------------------------- #

tab_url = r"https://tab.tuneguitar.net/Player/DownloadSong?Type=1&SongId={}"


def get_tab_data(url):
    """
    Returns [id, song name, artist]
    If name and artist can't be found, both will be None"""
    result = [None, None, None]
    try:
        resp = session.get(url)
    except Exception as e:
        print(f"❌ Could not retreive URL: {e}")
        return None

    if resp.status_code != 200:
        print(f"❌ URL response: {resp.status_code}")
        return None

    search = re.search("SongId=([0-9]*)", resp.text)
    if search is None:
        print("❌ Can't find song ID in html response")
        return None

    if search.group(1).isnumeric():
        result[0] = search.group(1)
    else:
        print(f"❌ Malformed song ID {search.group(0)} (should be a number eg 123456)")
        return None

    search = re.search("<h1>(.*) - tab - (.*)<\/h1>", resp.text)
    try:
        result[1], result[2] = search.group(1), search.group(2)
    except Exception as _:
        pass

    return result


def get_gp5(tab_data):
    url = tab_url.format(tab_data[0])
    try:
        return session.get(url).content
    except Exception as e:
        print(f"❌ Could not retreive URL: {e}")
        return None


def save_gp5_to_disk(gp5, tab_data):
    dldir = default_download_dir
    if default_download_dir is None:
        print("❔ Enter download directory:")
        dldir = input(">")

    fname = (
        f"{tab_data[1]} - {tab_data[2]}.gp5"
        if tab_data[1] is not None
        else f"{tab_data[0]}.gp5"
    )

    filepath = os.path.join(dldir, fname)
    try:
        with open(filepath, "wb") as f:
            f.write(gp5)
        print(f"✅ Tab saved as {filepath}")
    except Exception as e:
        print(f"❌ Writing file failed: {e}")


def mainloop():
    while True:
        print("🎸 Enter full url of song page.\nEnter 'q' to quit")
        url = input(">")
        if url == "q":
            return
        tab_data = get_tab_data(url)
        if tab_data is None:
            print("\n")
            continue

        gp5 = get_gp5(tab_data)
        if gp5 is None:
            print("\n")
            continue

        save_gp5_to_disk(gp5, tab_data)
        print("\n")


session = requests.Session()
mainloop()
