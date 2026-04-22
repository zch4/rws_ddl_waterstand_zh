from unittest.mock import patch

import pandas as pd
from django.test import SimpleTestCase

from .data_service import get_uurprofiel_hvh


class UurprofielTests(SimpleTestCase):
    def test_get_uurprofiel_hvh_returns_average_per_hour(self):
        silver_data = pd.DataFrame(
            {
                "meetstation_naam": ["Hoek van Holland", "Hoek van Holland"],
                "uur": [1, 1],
                "waterstand_cm": [20.0, 30.0],
            }
        )

        with patch("waterstand.data_service.laad_silver_data", return_value=silver_data):
            data = get_uurprofiel_hvh()

        self.assertEqual(data["labels"][1], "01:00")
        self.assertEqual(data["waarden"][1], 25.0)
        self.assertEqual(data["eenheid"], "cm t.o.v. NAP")
