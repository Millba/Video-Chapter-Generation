import pandas as pd
import os, glob
import json
import re
from make_video_chapter_dataset import TIMESTAMP_DELIMITER


def extract_timestamp(s):
    r = re.search("\d{2}:\d{2}:\d{2}", s)
    if r:
        si, ei = r.regs[0]
    else:
        r = re.search("\d{1}:\d{2}:\d{2}", s)
        if r:
            si, ei = r.regs[0]
        else:
            r = re.search("\d{2}:\d{2}", s)
            if r:
                si, ei = r.regs[0]
            else:
                r = re.search("\d{1}:\d{2}", s)
                if r:
                    si, ei = r.regs[0]
                else:
                    return "", -1, -1, -1

    timestamp = s[si:ei]
    ts = timestamp.split(":")
    ts.reverse()
    sec = 0
    for i in range(len(ts)):
        if i == 0:
            sec += int(ts[i])
        elif i == 1:
            sec += int(ts[i]) * 60
        elif i == 2:
            sec += int(ts[i]) * 3600

    return s[si:ei], sec, si, ei


def extract_first_timestamp(s):
    t, sec, si, ei = extract_timestamp(s)
    min_sec = sec
    description = s[:si] + s[ei:]

    while sec != -1:
        t, sec, si, ei = extract_timestamp(description)
        if sec != -1:
            if min_sec > sec:
                min_sec = sec
            description = description[:si] + description[ei:]
    
    return min_sec, description


def clean_str(s):
    """
    Remove all special char at the beginning and the end.
    Use to clean chapter title string
    """
    start_idx = 0
    for i in range(len(s)):
        if s[i].isalnum():
            start_idx = i
            break

    end_idx = len(s)
    for i in reversed(range(len(s))):
        if s[i].isalnum():
            end_idx = i + 1
            break
    
    return s[start_idx : end_idx]



def parse_csv_to_list(csv_file, w_duration=True):
    data = pd.read_csv(csv_file)
    vids = list(data["videoId"].values)
    titles = list(data["title"].values)
    if w_duration:
        durations = list(data["duration"].values)
    timestamps = list(data["timestamp"].values)
    timestamps = [x.split(TIMESTAMP_DELIMITER) for x in timestamps]

    if w_duration:
        return vids, titles, durations, timestamps
    else:
        return vids, titles, timestamps

def load_dataset_with_subtitle(asr_files):
    vids_with_asr = []
    titles_with_asr = []
    timestamps_with_asr = []
    subtitles = []

    for asr_file in asr_files:
        dirname = os.path.dirname(asr_file)
        csv_file = os.path.join(dirname, "data.csv")

        # load vid and timestamp
        vids, titles, timestamps = parse_csv_to_list(csv_file, w_duration=False)
        vid2index = dict()
        for index, vid in enumerate(vids):
            vid2index[vid] = index

        # load subtitle
        filename = os.path.basename(asr_file)
        vid = filename.split(".")[0][9:]
        with open(asr_file, "r") as f:
            subtitle = json.load(f)

        index = vid2index[vid]
        title = titles[index]
        timestamp = timestamps[index]

        vids_with_asr.append(vid)
        titles_with_asr.append(title)
        timestamps_with_asr.append(timestamp)
        subtitles.append(subtitle)

    return vids_with_asr, titles_with_asr, timestamps_with_asr, subtitles



if __name__ == "__main__":
    # csv_file = "../dataset/top steam games/data.csv"
    # vids, titles, timestamps = parse_csv_to_list(csv_file)
    # vid = "-SUlsj5a6iw"
    #
    # idx = vids.index(vid)
    #
    # title = titles[idx]
    # timestamp = timestamps[idx]
    # print(vid)
    # print(titles)
    # print(timestamp)
    #
    # # asr_files = glob.glob("../dataset/top steam games/*.json")
    # # vids_with_asr, titles_with_asr, timestamps_with_asr, subtitles = load_dataset_with_subtitle(asr_files)


    s = "June 26-27, 20200:00 "
    timepoint, sec, si, ei = extract_timestamp(s)
    print(timepoint, sec, si, ei)


    # urls = []
    # all_data_file = glob.glob("../dataset/*/data.csv")
    # for data_file in all_data_file:
    #     vids, titles, timestamps = parse_csv_to_list(data_file)
    #     vids = vids[:5]
    #     for vid in vids:
    #         url = f"https://www.youtube.com/watch?v={vid}"
    #         urls.append(url)
    #         print(url)
    #
    # print()
