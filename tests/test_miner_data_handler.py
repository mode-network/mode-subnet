import unittest
import os
from datetime import datetime, timedelta
from simulation.validator.miner_data_handler import MinerDataHandler

from tests.utils import generate_values


class TestMinerDataHandler(unittest.TestCase):
    def setUp(self):
        """Set up a temporary file for testing."""
        self.handler = MinerDataHandler()

    def test_get_values_within_range(self):
        """
        Test retrieving values within the valid time range.
        2024-11-20T00:00:00       2024-11-20T23:55:00
                 |-------------------------|                       (Prediction range)

                                                2024-11-22T00:00:00
                                                        |-|        (Current Time)
        """
        miner_id = "miner_123"
        start_time = "2024-11-20T00:00:00"
        current_time = "2024-11-22T00:00:00"

        values = generate_values(datetime.fromisoformat(start_time))
        self.handler.set_values(miner_id, start_time, values)

        result = self.handler.get_values(miner_id, current_time)

        self.assertEqual(288, len(result))  # Half of the 288 intervals
        self.assertEqual({"time": "2024-11-20T00:00:00", "price": 90000}, result[0])
        self.assertEqual({"time": "2024-11-20T23:55:00", "price": 233500}, result[287])

    def test_get_values_exceeding_range(self):
        """
        Test retrieving values when current_time exceeds the range.
        2024-11-20T00:00:00       2024-11-20T23:55:00
                 |-------------------------|                       (Prediction range)

                                                2024-11-30T00:00:00
                                                        |-|        (Current Time - more than 5 days passed)
        """
        miner_id = "miner_123"
        start_time = "2024-11-20T00:00:00"
        current_time = "2024-11-30T00:00:00"

        values = generate_values(datetime.fromisoformat(start_time))
        self.handler.set_values(miner_id, start_time, values)

        result = self.handler.get_values(miner_id, current_time)
        self.assertEqual(result, [])

    def test_get_values_ongoing_range(self):
        """
        Test retrieving values when current_time overlaps with the range.
        2024-11-20T00:00:00       2024-11-20T23:55:00
                 |-------------------------|         (Prediction range)

                    2024-11-20T12:00:00
                            |-|                      (Current Time)
        """
        miner_id = "miner_123"
        start_time = "2024-11-20T00:00:00"
        current_time = "2024-11-20T12:00:00"

        values = generate_values(datetime.fromisoformat(start_time))
        self.handler.set_values(miner_id, start_time, values)

        result = self.handler.get_values(miner_id, current_time)
        self.assertEqual(result, [])

    def test_multiple_records_for_same_miner(self):
        """
        Test handling multiple records for the same miner.
        Should take "Prediction range 2" as the latest one

        2024-11-20T00:00:00       2024-11-20T23:55:00
                 |-------------------------|                             (Prediction range 1)

                      2024-11-20T12:00:00       2024-11-21T11:55:00
                               |-------------------------|               (Prediction range 2)

                                                      2024-11-21T15:00:00
                                                              |-|        (Current Time)
        """
        miner_id = "miner_123"
        start_time_1 = "2024-11-20T00:00:00"
        start_time_2 = "2024-11-20T12:00:00"
        current_time = "2024-11-21T15:00:00"

        values = generate_values(datetime.fromisoformat(start_time_1))
        self.handler.set_values(miner_id, start_time_1, values)

        values = generate_values(datetime.fromisoformat(start_time_2))
        self.handler.set_values(miner_id, start_time_2, values)

        result = self.handler.get_values(miner_id, current_time)

        self.assertEqual(288, len(result))  # Half of the 288 intervals
        self.assertEqual({"time": "2024-11-20T12:00:00", "price": 90000}, result[0])
        self.assertEqual({"time": "2024-11-21T11:55:00", "price": 233500}, result[287])

    def test_multiple_records_for_same_miner_with_overlapping(self):
        """
        Test handling multiple records for the same miner with overlapping records.
        Should take "Prediction range 1" as the latest one

        2024-11-20T00:00:00       2024-11-20T23:55:00
                 |-------------------------|                             (Prediction range 1)

                      2024-11-20T12:00:00       2024-11-21T11:55:00
                               |-------------------------|               (Prediction range 2)

                                        2024-11-21T03:00:00
                                                |-|                      (Current Time)
        """
        miner_id = "miner_123"
        start_time_1 = "2024-11-20T00:00:00"
        start_time_2 = "2024-11-20T12:00:00"
        current_time = "2024-11-21T03:00:00"

        values = generate_values(datetime.fromisoformat(start_time_1))
        self.handler.set_values(miner_id, start_time_1, values)

        values = generate_values(datetime.fromisoformat(start_time_2))
        self.handler.set_values(miner_id, start_time_2, values)

        result = self.handler.get_values(miner_id, current_time)

        self.assertEqual(288, len(result))  # Half of the 288 intervals
        self.assertEqual({"time": "2024-11-20T00:00:00", "price": 90000}, result[0])
        self.assertEqual({"time": "2024-11-20T23:55:00", "price": 233500}, result[287])

    def test_no_data_for_miner(self):
        """Test retrieving values for a miner that doesn't exist."""
        miner_id = "nonexistent_miner"
        current_time = "2024-11-20T12:00:00"

        result = self.handler.get_values(miner_id, current_time)
        self.assertEqual(result, [])
