import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("nba_grade", Path(__file__).resolve().parents[1] / "grade.py")
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)


class GradeTests(unittest.TestCase):
    def test_market_arithmetic(self):
        stats = {"PTS": 14, "REB": 9, "AST": 6, "3PM": 3}
        self.assertEqual(grade.value_for("PR", stats), 23)
        self.assertEqual(grade.value_for("PRA", stats), 29)
        self.assertEqual(grade.value_for("3PM", stats), 3)

    def test_name_normalization(self):
        self.assertEqual(grade.normal("Luka Dončić"), grade.normal("Luka Doncic"))

    def test_completed_event_and_player(self):
        event = {"id": "1", "status": {"type": {"completed": True}},
                 "competitions": [{"competitors": [{"team": {"abbreviation": "ORL"}}, {"team": {"abbreviation": "SAC"}}]}]}
        self.assertEqual(grade.locate_event({"events": [event]}, "ORL", "SAC")["id"], "1")
        summary = {"boxscore": {"players": [{"team": {"abbreviation": "ORL"}, "statistics": [{
            "labels": ["MIN", "FG", "3PT", "REB", "AST", "PTS"],
            "athletes": [{"athlete": {"displayName": "Wendell Carter Jr."},
                          "stats": ["34", "6-14", "1-3", "9", "4", "14"]}]
        }]}]}}
        self.assertEqual(grade.extract_player(summary, "ORL", "Wendell Carter Jr.")["3PM"], 1)
        row = {"id": "test", "date_et": "2026-11-10", "team": "ORL", "opponent": "SAC",
               "player": "Wendell Carter Jr.", "market": "PR", "threshold": 23, "grade_status": "pending"}
        fake = lambda url: {"events": [event]} if "scoreboard" in url else summary
        result = grade.grade_day("2026-11-10", [row], fake)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(row["grade_status"], "hit")
        self.assertEqual(row["observed"], 23)

    def test_nonfinal_does_not_settle(self):
        event = {"id": "1", "status": {"type": {"completed": False}},
                 "competitions": [{"competitors": [{"team": {"abbreviation": "ORL"}}, {"team": {"abbreviation": "SAC"}}]}]}
        row = {"id": "test", "date_et": "2026-11-10", "team": "ORL", "opponent": "SAC",
               "player": "Wendell Carter Jr.", "market": "PR", "threshold": 23, "grade_status": "pending"}
        result = grade.grade_day("2026-11-10", [row], lambda _: {"events": [event]})
        self.assertEqual(result["updated"], 0)
        self.assertEqual(row["grade_status"], "pending")


if __name__ == "__main__":
    unittest.main()
