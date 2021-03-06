"""
Import ZDF point cloud without Zivid Software.
Note: ZIVID_DATA needs to be set to the location of Zivid Sample Data files.
"""

from pathlib import Path
import os
from netCDF4 import Dataset
from matplotlib import pyplot as plt
import numpy as np


def _main():

    filename_zdf = Path() / f"{str(os.environ['ZIVID_DATA'])}/Zivid3D.zdf"

    print(f"Reading {filename_zdf} point cloud")
    with Dataset(filename_zdf) as data:
        # Extracting the point cloud
        xyz = data["data"]["pointcloud"][:, :, :]

        # Extracting the RGB image
        rgb = data["data"]["rgba_image"][:, :, :3]

        # Extracting the contrast image
        contrast = data["data"]["contrast"][:, :]

    # Displaying the RGB image
    plt.figure()
    plt.imshow(rgb)
    plt.title("RGB image")
    plt.show()

    # Displaying the Depth Image
    plt.imshow(
        xyz[:, :, 2],
        vmin=np.nanmin(xyz[:, :, 2]),
        vmax=np.nanmax(xyz[:, :, 2]),
        cmap="jet",
    )
    plt.colorbar()
    plt.title("Depth map")
    plt.show()


if __name__ == "__main__":
    _main()
