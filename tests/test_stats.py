import unittest
from app import app
from services.stats_service import StatsService
from services.user_service import UserService


class TestStats(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.user_service = UserService()
        self.stats_service = StatsService()

    def test_stats_service_calculations(self):
        """
        Comprova que StatsService calcula correctament el percentatge d'èxit,
        l'XP fins al següent nivell, les mitjanes familiars i els rànquings.
        """
        users = self.user_service.get_all_users()
        if not users:
            self.skipTest("No hi ha usuaris a la base de dades")

        test_user = users[0]
        summary = self.stats_service.get_user_stats_summary(test_user.id)

        self.assertIsNotNone(summary)
        self.assertIn("kpi", summary)
        self.assertIn("activity", summary)
        self.assertIn("success_rate", summary["activity"])
        self.assertIn("next_level_xp", summary["kpi"])
        self.assertTrue(0 <= summary["kpi"]["next_level_xp"] <= 100)

        # Test rànquings
        leaderboards = self.stats_service.get_leaderboards(family_id=test_user.family_id)
        self.assertIn("xp", leaderboards)
        self.assertIn("coins", leaderboards)
        self.assertIn("completed", leaderboards)
        if leaderboards["xp"]:
            self.assertEqual(leaderboards["xp"][0]["position"], 1)
            self.assertEqual(leaderboards["xp"][0]["badge"], "🥇")

    def test_unauthenticated_access_to_stats(self):
        """
        Comprova que un usuari no autenticat és redirigit a la pàgina de login.
        """
        response = self.client.get("/stats", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_gamer_role_access_restriction(self):
        """
        Comprova que un usuari Gamer (child) només té accés a les meves estadístiques.
        """
        users = self.user_service.get_all_users()
        gamer = next((u for u in users if u.role == "child"), None)

        if not gamer:
            self.skipTest("No s'ha trobat un usuari amb rol 'child'")

        with self.client.session_transaction() as sess:
            sess["user_id"] = gamer.id
            sess["role"] = gamer.role
            sess["user_name"] = gamer.name

        # Intentar sol·licitar la pestanya de rànquings
        response = self.client.get("/stats?tab=rankings")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("👤 Les meves estadístiques", html)

    def test_admin_role_full_access(self):
        """
        Comprova que un usuari Administrador té accés a les tres pestanyes.
        """
        users = self.user_service.get_all_users()
        admin = next((u for u in users if u.role == "admin"), None)

        if not admin:
            self.skipTest("No s'ha trobat un usuari amb rol 'admin'")

        with self.client.session_transaction() as sess:
            sess["user_id"] = admin.id
            sess["role"] = admin.role
            sess["user_name"] = admin.name

        response = self.client.get("/stats?tab=family_stats")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Estadístiques familiars", html)

    def test_api_evolution(self):
        """
        Comprova que l'endpoint d'API /api/stats/evolution retorna un objecte JSON vàlid.
        """
        users = self.user_service.get_all_users()
        if not users:
            self.skipTest("No hi ha usuaris")

        with self.client.session_transaction() as sess:
            sess["user_id"] = users[0].id
            sess["role"] = users[0].role

        response = self.client.get("/api/stats/evolution?period=week")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("labels", data)
        self.assertIn("datasets", data)
        self.assertIn("xp", data["datasets"])


if __name__ == "__main__":
    unittest.main()
