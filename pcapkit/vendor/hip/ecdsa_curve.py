# -*- coding: utf-8 -*-
"""HIP ECDSA Curve Label"""

from pcapkit.vendor.default import Vendor

__all__ = ['ECDSACurve']


class ECDSACurve(Vendor):
    """ECDSA Curve Label"""

    #: Value limit checker.
    FLAG = 'isinstance(value, int) and 0 <= value <= 65535'
    #: Link to registry.
    LINK = 'https://www.iana.org/assignments/hip-parameters/ecdsa-curve-label.csv'


if __name__ == "__main__":
    ECDSACurve()
