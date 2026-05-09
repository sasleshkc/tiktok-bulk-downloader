#!/usr/bin/env python3

import os
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# paths
LINKS_PATH = os.path.expanduser("~/Desktop/links.txt")
DOWNLOAD_FOLDER = os.path.expanduser("~/Desktop/TikTokDownloads")
FAILED_LOG = os.path.expanduser("~/Desktop/failed_links.txt")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# load links
with open(LINKS_PATH, "r") as file:
    links = [line.strip() for line in file if line.strip()]

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("TikTok Downloader")
root.geometry("520x320")
root.resizable(False, False)

mode = tk.StringVar(value="safe")

title = tk.Label(
    root,
    text="Select Download Mode",
    font=("Arial", 14)
)
title.pack(pady=12)

safe_btn = tk.Radiobutton(
    root,
    text="SAFE (stable)",
    variable=mode,
    value="safe"
)
safe_btn.pack()

fast_btn = tk.Radiobutton(
    root,
    text="FAST (aggressive + retries)",
    variable=mode,
    value="fast"
)
fast_btn.pack()

status_label = tk.Label(
    root,
    text="Waiting to start...",
    wraplength=480
)
status_label.pack(pady=12)

progress_bar = ttk.Progressbar(
    root,
    length=450,
    mode="determinate"
)
progress_bar.pack(pady=10)

progress_bar["maximum"] = len(links)

# ---------------- DOWNLOAD LOGIC ---------------- #

def download_video(link, selected_mode, attempt=1):
    command = [
        "yt-dlp",
        link,
        "--newline",
        "--no-part",
        "--ignore-errors",
        "-o",
        os.path.join(DOWNLOAD_FOLDER, "%(title).80s.%(ext)s")
    ]

    if selected_mode == "safe":
        command.extend([
            "--retries", "10",
            "--fragment-retries", "10",
            "--concurrent-fragments", "1",
            "--socket-timeout", "30"
        ])
    else:
        command.extend([
            "--retries", "2",
            "--fragment-retries", "2",
            "--socket-timeout", "10",
            "--concurrent-fragments", "8"
        ])

    status_label.config(text=f"[Attempt {attempt}] Downloading:\n{link[:60]}")
    root.update()

    process = subprocess.Popen(command)
    process.wait()

    return process.returncode == 0


def run_downloads():
    selected_mode = mode.get()
    failed_links = []

    # first pass
    for index, link in enumerate(links):
        success = download_video(link, selected_mode)

        if not success:
            failed_links.append(link)

        progress_bar["value"] = index + 1
        root.update()

        delay = 2 if selected_mode == "safe" else 0.2
        time.sleep(delay)

    # retry failed downloads in fast mode
    if selected_mode == "fast" and failed_links:
        status_label.config(
            text=f"Retrying {len(failed_links)} failed downloads..."
        )
        root.update()

        remaining_failed = []

        for link in failed_links:
            success = False

            for retry in range(1, 3):
                if download_video(link, selected_mode, retry):
                    success = True
                    break

                time.sleep(1)

            if not success:
                remaining_failed.append(link)

        failed_links = remaining_failed

    # save failed links
    if failed_links:
        with open(FAILED_LOG, "a") as file:
            for link in failed_links:
                file.write(link + "\n")

    messagebox.showinfo(
        "Finished",
        f"Download complete.\nFailed: {len(failed_links)}"
    )

    root.destroy()


start_button = tk.Button(
    root,
    text="Start Download",
    command=run_downloads,
    height=2,
    width=20
)

start_button.pack(pady=12)

root.mainloop()