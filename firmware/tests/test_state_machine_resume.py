"""Source-level regression checks for StateMachine heater restoration."""

from pathlib import Path
import unittest


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "state_machine.cpp"


def extract_function(source: str, signature: str) -> str:
    """Return one C++ function body using balanced-brace scanning."""
    signature_start = source.index(signature)
    body_start = source.index("{", signature_start + len(signature))
    depth = 0

    for position in range(body_start, len(source)):
        character = source[position]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[body_start : position + 1]

    raise ValueError(f"Unbalanced function body for {signature}")


class StateMachineResumeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE_PATH.read_text(encoding="utf-8")

    def test_resume_restores_active_material_profile_temperature(self) -> None:
        body = extract_function(self.source, "void StateMachine::resume()")

        self.assertIn(
            "const TemperatureProfile profile = getActiveTemperatureProfile();",
            body,
        )
        self.assertIn("setTargetTemperature(profile.spliceTargetC);", body)
        self.assertNotIn("WELD_TEMP_", body)

    def test_resume_matches_heating_profile_source(self) -> None:
        resume_body = extract_function(self.source, "void StateMachine::resume()")
        heating_body = extract_function(self.source, "void StateMachine::handleHeating()")

        expected_profile_lookup = "getActiveTemperatureProfile()"
        expected_target = "setTargetTemperature(profile.spliceTargetC);"
        self.assertIn(expected_profile_lookup, resume_body)
        self.assertIn(expected_profile_lookup, heating_body)
        self.assertIn(expected_target, resume_body)
        self.assertIn(expected_target, heating_body)


if __name__ == "__main__":
    unittest.main()
