"""
Balance color for RGB image.
"""

import datetime
from dataclasses import dataclass
import math
import numpy as np
import matplotlib.pyplot as plt
import zivid


@dataclass(frozen=True)
class StopIncrement:
    """
    Set of aperture stop increments. For readability

    """

    full = 1 / 1
    half = 1 / 2
    third = 1 / 3
    quarter = 1 / 4


@dataclass
class MeanColor:
    """
    RGB  channel mean colors

    Attributes:
        red (np.array): Red channel mean value
        green (np.array): Green channel mean value
        blue (np.array): Blue channel mean value

    """

    red: np.array
    green: np.array
    blue: np.array


def _get_next_aperture_setting(current_aperture: float, stop: float) -> float:
    # new_aperture = current_aperture * 2 ^ (0.5 * stop)
    return current_aperture * math.pow(2, 0.5 * stop)


def _convert_frame2d_to_numpy_float_rgb(frame: zivid.Frame2D):
    image = frame.image_rgba().to_array()
    return np.dstack([image["r"], image["g"], image["b"]])


def _display_rgb(rgb, title):
    """Display RGB image.

    Args:
        rgb: RGB image
        title: Image title

    Returns None

    """
    plt.figure()
    plt.imshow(rgb)
    plt.title(title)
    plt.show(block=False)


def _get_center_mask(rgb, pixels):
    """Get central square RGB values.

    Args:
        rgb: RGB image
        pixels: Number of central pixels (^2) for computation

    Returns:
        Masked RGB

    """
    height = np.shape(rgb)[0]
    width = np.shape(rgb)[1]
    pixel_hight_start_index = int((height - pixels) / 2)
    pixel_hight_end_index = int((height + pixels) / 2)
    pixel_width_start_index = int((width - pixels) / 2)
    pixel_width_end_index = int((width + pixels) / 2)
    return rgb[
        pixel_hight_start_index:pixel_hight_end_index,
        pixel_width_start_index:pixel_width_end_index,
        :,
    ]


def _compute_mean_rgb(rgb):
    """Compute mean RGB values.

    Args:
        rgb: RGB image

    Returns:
        mean_color: RGB channel mean values

    """
    mean_rgb = np.mean(np.mean(rgb, axis=0), axis=0)
    return MeanColor(red=mean_rgb[0], green=mean_rgb[1], blue=mean_rgb[2])


def _get_tuned_settings(camera: zivid.Camera) -> zivid.Settings2D:
    """Get settings such that max mean(RGB) is < 240. In other words, no saturation on average.

    Args:
        camera: Zivid camera

    Returns:
        settings_2d: 2D capture settings without saturation on average

    """
    settings_2d = zivid.Settings2D(
        acquisitions=[
            zivid.Settings2D.Acquisition(
                aperture=5.66,
                exposure_time=datetime.timedelta(microseconds=80000),
                brightness=0.0,
                gain=2.0,
            )
        ],
    )
    rgb = _convert_frame2d_to_numpy_float_rgb(camera.capture(settings_2d))
    rgb_masked = _get_center_mask(rgb, 100)
    mean_rgb = np.mean(np.mean(rgb_masked, axis=0), axis=0)
    print(f"RGB mean: {mean_rgb}, Aperture: {settings_2d.acquisitions[0].aperture}")
    while mean_rgb.max() > 240:
        settings_2d.acquisitions[0].aperture = _get_next_aperture_setting(
            settings_2d.acquisitions[0].aperture, StopIncrement.quarter
        )
        rgb = _convert_frame2d_to_numpy_float_rgb(camera.capture(settings_2d))
        rgb_masked = _get_center_mask(rgb, 100)
        mean_rgb = np.mean(np.mean(rgb_masked, axis=0), axis=0)
        print(f"RGB mean: {mean_rgb}, Aperture: {settings_2d.acquisitions[0].aperture}")
    return settings_2d


def _color_balance_calibration(camera, settings_2d):
    """Balance color for RGB image by taking images of white surface (piece of paper, wall, etc.) in a loop.

    Args:
        camera: Zivid camera
        settings_2d: 2D capture settings

    Returns:
        corrected_red_balance: Corrected red balance
        corrected_blue_balance: Corrected blue balance

    """
    print("Starting color balance calibration")
    corrected_red_balance = 1.0
    corrected_blue_balance = 1.0
    first_iteration = True
    while True:
        settings_2d.processing.color.balance.red = corrected_red_balance
        settings_2d.processing.color.balance.blue = corrected_blue_balance
        rgb = _convert_frame2d_to_numpy_float_rgb(camera.capture(settings_2d))
        if first_iteration:
            _display_rgb(rgb, "RGB image before color balance")
            first_iteration = False
        mean_color = _compute_mean_rgb(_get_center_mask(rgb, 100))
        print(
            (
                "Mean color values: R = "
                f"{int(mean_color.red)} "
                "G = "
                f"{int(mean_color.green)} "
                "B = "
                f"{int(mean_color.blue)} "
            )
        )
        if int(mean_color.green) == int(mean_color.red) and int(
            mean_color.green
        ) == int(mean_color.blue):
            break
        corrected_red_balance = (
            settings_2d.processing.color.balance.red * mean_color.green / mean_color.red
        )
        corrected_blue_balance = (
            settings_2d.processing.color.balance.blue
            * mean_color.green
            / mean_color.blue
        )
    _display_rgb(rgb, "RGB image after color balance")

    return (corrected_red_balance, corrected_blue_balance)


def _main():

    app = zivid.Application()

    camera = app.connect_camera()

    settings_2d = _get_tuned_settings(camera)

    rgb = _convert_frame2d_to_numpy_float_rgb(camera.capture(settings_2d))
    _display_rgb(rgb, "RGB image before color balance")

    [red_balance, blue_balance] = _color_balance_calibration(camera, settings_2d)

    settings_2d.processing.color.balance.red = red_balance
    settings_2d.processing.color.balance.blue = blue_balance
    print(f"Updating color balance settings to {settings_2d.processing.color.balance}")
    rgb_balanced = _convert_frame2d_to_numpy_float_rgb(camera.capture(settings_2d))

    _display_rgb(rgb_balanced, "RGB image after color balance")
    input("Press Enter to close...")


if __name__ == "__main__":
    _main()
