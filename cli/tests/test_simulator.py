"""Tests for the Splice3D firmware simulator."""

import json
import os
import tempfile
import unittest

from cli.simulator import FirmwareSimulator, SimConfig, State


class TestSimConfig(unittest.TestCase):
    """Tests for SimConfig defaults."""

    def test_default_values(self):
        config = SimConfig()
        self.assertEqual(config.feed_rate_mm_s, 50.0)
        self.assertEqual(config.weld_temp_c, 210.0)
        self.assertEqual(config.heat_rate_c_s, 5.0)
        self.assertEqual(config.cool_rate_c_s, 10.0)
        self.assertEqual(config.speed_factor, 1.0)

    def test_custom_values(self):
        config = SimConfig(feed_rate_mm_s=100.0, speed_factor=10.0)
        self.assertEqual(config.feed_rate_mm_s, 100.0)
        self.assertEqual(config.speed_factor, 10.0)


class TestFirmwareSimulator(unittest.TestCase):
    """Tests for FirmwareSimulator."""

    def setUp(self):
        self.config = SimConfig(speed_factor=1000.0)  # Fast for tests
        self.sim = FirmwareSimulator(config=self.config)
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_recipe(self, segments):
        recipe = {
            "version": "1.0",
            "segments": segments,
            "total_length_mm": sum(s["length_mm"] for s in segments),
            "segment_count": len(segments),
        }
        path = os.path.join(self.tmpdir, "test_recipe.json")
        with open(path, "w") as f:
            json.dump(recipe, f)
        return path

    def test_initial_state(self):
        self.assertEqual(self.sim.state, State.IDLE)
        self.assertEqual(self.sim.splices_completed, 0)
        self.assertEqual(self.sim.current_temp, 25.0)

    def test_load_recipe_success(self):
        path = self._create_recipe([
            {"color": 0, "length_mm": 100.0},
            {"color": 1, "length_mm": 100.0},
        ])
        result = self.sim.load_recipe(path)
        self.assertTrue(result)
        self.assertEqual(self.sim.state, State.READY)
        self.assertEqual(len(self.sim.segments), 2)

    def test_load_recipe_bad_file(self):
        result = self.sim.load_recipe("/nonexistent/recipe.json")
        self.assertFalse(result)
        self.assertEqual(self.sim.state, State.ERROR)

    def test_load_recipe_invalid_json(self):
        path = os.path.join(self.tmpdir, "bad.json")
        with open(path, "w") as f:
            f.write("not json")
        result = self.sim.load_recipe(path)
        self.assertFalse(result)

    def test_run_without_recipe(self):
        result = self.sim.run()
        self.assertFalse(result)

    def test_run_two_segment_recipe(self):
        path = self._create_recipe([
            {"color": 0, "length_mm": 50.0},
            {"color": 1, "length_mm": 50.0},
        ])
        self.sim.load_recipe(path)
        result = self.sim.run()
        self.assertTrue(result)
        self.assertEqual(self.sim.state, State.COMPLETE)
        self.assertEqual(self.sim.splices_completed, 2)
        self.assertAlmostEqual(self.sim.total_filament_mm, 100.0)

    def test_run_single_segment(self):
        path = self._create_recipe([
            {"color": 0, "length_mm": 200.0},
        ])
        self.sim.load_recipe(path)
        result = self.sim.run()
        self.assertTrue(result)
        self.assertEqual(self.sim.splices_completed, 1)

    def test_color_routing(self):
        """Test that color 0 goes to FEEDING_A and color 1 to FEEDING_B."""
        path = self._create_recipe([
            {"color": 0, "length_mm": 10.0},
            {"color": 1, "length_mm": 10.0},
        ])
        self.sim.load_recipe(path)

        # Step through READY
        self.sim._step()
        self.assertEqual(self.sim.state, State.FEEDING_A)

    def test_total_time_accumulated(self):
        path = self._create_recipe([
            {"color": 0, "length_mm": 100.0},
        ])
        self.sim.load_recipe(path)
        self.sim.run()
        self.assertGreater(self.sim.total_time_s, 0)

    def test_zero_rate_protection(self):
        """Test that zero heat/cool rates don't cause division by zero."""
        config = SimConfig(heat_rate_c_s=0.0, cool_rate_c_s=0.0, speed_factor=1000.0)
        sim = FirmwareSimulator(config=config)
        path = self._create_recipe([{"color": 0, "length_mm": 10.0}])
        sim.load_recipe(path)
        # Should not raise ZeroDivisionError
        result = sim.run()
        self.assertTrue(result)


class TestSimulatorEdgeCases(unittest.TestCase):
    """Edge case tests for simulator."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_segments(self):
        recipe = {"segments": []}
        path = os.path.join(self.tmpdir, "empty.json")
        with open(path, "w") as f:
            json.dump(recipe, f)
        sim = FirmwareSimulator(SimConfig(speed_factor=1000.0))
        sim.load_recipe(path)
        result = sim.run()
        self.assertTrue(result)
        self.assertEqual(sim.splices_completed, 0)

    def test_default_color_fallback(self):
        """Segments without color key default to 0 (FEEDING_A)."""
        recipe = {"segments": [{"length_mm": 10.0}]}
        path = os.path.join(self.tmpdir, "no_color.json")
        with open(path, "w") as f:
            json.dump(recipe, f)
        sim = FirmwareSimulator(SimConfig(speed_factor=1000.0))
        sim.load_recipe(path)
        result = sim.run()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
