#!/bin/python3

from enum import Enum
from typing import Self
from urllib import request
import json


class Board(Enum):
    POCKETBEAGLE2 = 1
    BEAGLEPLAY = 2
    BEAGLEBONEAI64 = 3

    @staticmethod
    def from_search_str(s: str) -> Self:
        for i in SUPPORTED_BOARDS:
            if i.search_str() == s:
                return i

    def search_str(self) -> str:
        if self == Board.POCKETBEAGLE2:
            return "Pocketbeagle2"
        elif self == Board.BEAGLEPLAY:
            return "Beagleplay"
        elif self == Board.BEAGLEBONEAI64:
            return "Beaglebone-ai64"

        raise ValueError("Unsupported Board")

    def board_name(self) -> str:
        if self == Board.POCKETBEAGLE2:
            return "PocketBeagle 2"
        elif self == Board.BEAGLEPLAY:
            return "BeaglePlay"
        elif self == Board.BEAGLEBONEAI64:
            return "BeagleBone AI-64"

        raise ValueError("Unsupported Board")

    def device_tag(self) -> str:
        if self == Board.POCKETBEAGLE2:
            return "pocketbeagle2-am62"
        elif self == Board.BEAGLEPLAY:
            return "beagle-am62"
        elif self == Board.BEAGLEBONEAI64:
            return "beagle-tda4vm"

        raise ValueError("Unsupported Board")


ARMBIAN_ROLLIING_URL = "https://api.github.com/repos/armbian/os/releases/latest"
ARMBIAN_ICON = "https://www.beagleboard.org/app/uploads/2025/04/armbian-logo.jpg"
SUPPORTED_BOARDS = [Board.POCKETBEAGLE2, Board.BEAGLEPLAY, Board.BEAGLEBONEAI64]


def fetch_release():
    req = request.urlopen(ARMBIAN_ROLLIING_URL)
    return json.loads(req.read())


def create_image_list(data):
    beagle_images = filter(
        lambda x: any(b.search_str() in x["name"] for b in SUPPORTED_BOARDS)
        and x["name"].endswith(".img.xz"),
        data,
    )
    res = []

    for img in beagle_images:
        _, _, board_name, release, branch, kernel_version, _ = img["name"].split("_")
        board = Board.from_search_str(board_name)
        board_name = board.board_name()
        name = f"{board_name} Armbian ({release}) v{kernel_version} {branch}"
        description = f"Armbian ({release}) Minimal for {board_name}"
        entry = {
            "name": name,
            "description": description,
            "icon": ARMBIAN_ICON,
            "url": img["browser_download_url"],
            "release_date": img["updated_at"].split("T")[0],
            "image_download_sha256": img["digest"].lstrip("sha256:"),
            "init_format": "Armbian",
            "tags": ["armbian"],
            "devices": [board.device_tag()],
        }
        res.append(entry)

    return res


if __name__ == "__main__":
    parsed = fetch_release()
    images = create_image_list(parsed["assets"])
    output = {
        "imager": {},
        "os_list": [
            {
                "name": "Armbian Images (rolling)",
                "description": "Here be Dragons, images for testing!!!",
                "icon": ARMBIAN_ICON,
                "flasher": "SdCard",
                "subitems": images,
            }
        ],
    }
    print(json.dumps(output, indent=4))
