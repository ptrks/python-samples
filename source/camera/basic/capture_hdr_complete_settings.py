"""
Capture an HDR frame with fully configured settings for each frame.

In general, taking an HDR image is a lot simpler than this as the default
settings work for most scenes. The purpose of this example is to demonstrate
how to configure all the settings.
"""

import datetime
import zivid


def _main():
    app = zivid.Application()

    print("Connecting to the camera")
    camera = app.connect_camera()

    print("Configuring the camera settings")

    settings = zivid.Settings(
        acquisitions=[
            zivid.Settings.Acquisition(
                aperture=23.42,
                exposure_time=datetime.timedelta(microseconds=10000),
                brightness=1,
                gain=1,
            ),
            zivid.Settings.Acquisition(
                aperture=6.28,
                exposure_time=datetime.timedelta(microseconds=20000),
                brightness=0.5,
                gain=2,
            ),
            zivid.Settings.Acquisition(
                aperture=3.43,
                exposure_time=datetime.timedelta(microseconds=33000),
                brightness=1,
                gain=1,
            ),
        ],
    )
    filters = settings.processing.filters
    filters.noise.removal.enabled = True
    filters.noise.removal.threshold = 10
    filters.smoothing.gaussian.enabled = True
    filters.smoothing.gaussian.sigma = 1.5
    filters.outlier.enabled = True
    filters.outlier.threshold = 5
    filters.experimental.contrast_distortion.correction.enabled = True
    filters.experimental.contrast_distortion.correction.strength = 0.4
    filters.experimental.contrast_distortion.removal.enabled = False
    filters.experimental.contrast_distortion.removal.threshold = 0.6
    balance = settings.processing.color.balance
    balance.red = 1.0
    balance.blue = 1.0
    balance.green = 1.0

    print("Capturing an HDR frame")
    with camera.capture(settings) as hdr_frame:
        print("Saving the HDR frame")
        hdr_frame.save("HDR.zdf")


if __name__ == "__main__":
    _main()
