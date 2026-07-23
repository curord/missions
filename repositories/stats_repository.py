from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import database


class StatsRepository:
    """
    Repositori encarregat d'executar consultes SQL d'agregació optimitzades
    per al Centre d'Estadístiques, evitant problemes N+1.
    """

    def get_user_activity_counts(self, user_id: int) -> Dict[str, int]:
        """
        Retorna el recompte de missions per estat d'un usuari.
        """
        rows = database.query(
            """
            SELECT status, COUNT(*) AS count
            FROM mission_assignments
            WHERE user_id = ?
            GROUP BY status
            """,
            (user_id,)
        )
        counts = {
            "completed": 0,
            "pending": 0,
            "waiting_validation": 0,
            "rejected": 0,
            "cancelled": 0,
            "in_progress": 0
        }
        for r in rows:
            st = r["status"]
            if st in counts:
                counts[st] = r["count"]
            else:
                counts[st] = r["count"]
        # 'pending' a la UI inclou 'pending' i 'in_progress'
        counts["pending_total"] = counts.get("pending", 0) + counts.get("in_progress", 0)
        return counts

    def get_user_rewards_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Retorna el resum de recompenses sol·licitades per un usuari.
        """
        row = database.query_one(
            """
            SELECT 
                COUNT(*) AS total_bought,
                SUM(CASE WHEN rh.delivered = 0 THEN 1 ELSE 0 END) AS pending_delivery,
                SUM(CASE WHEN rh.delivered = 1 THEN 1 ELSE 0 END) AS delivered_count,
                COALESCE(SUM(r.points_required), 0) AS total_coins_spent
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            WHERE rh.user_id = ?
            """,
            (user_id,)
        )
        if not row:
            return {
                "total_bought": 0,
                "pending_delivery": 0,
                "delivered_count": 0,
                "total_coins_spent": 0
            }
        return {
            "total_bought": row["total_bought"] or 0,
            "pending_delivery": row["pending_delivery"] or 0,
            "delivered_count": row["delivered_count"] or 0,
            "total_coins_spent": row["total_coins_spent"] or 0
        }

    def get_user_daily_activity(self, user_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """
        Retorna l'activitat diària dels darrers N dies d'un usuari per al calendari estil GitHub.
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = database.query(
            """
            SELECT 
                DATE(completed_at) AS date_str,
                COUNT(*) AS completed_count
            FROM mission_assignments
            WHERE user_id = ? 
              AND status = 'completed'
              AND completed_at IS NOT NULL
              AND DATE(completed_at) >= ?
            GROUP BY DATE(completed_at)
            ORDER BY date_str ASC
            """,
            (user_id, start_date)
        )
        return rows

    def get_family_daily_activity(self, family_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """
        Retorna l'activitat diària acumulada de tota la família per al calendari estil GitHub.
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = database.query(
            """
            SELECT 
                DATE(ma.completed_at) AS date_str,
                COUNT(*) AS completed_count
            FROM mission_assignments ma
            JOIN users u ON u.id = ma.user_id
            WHERE u.family_id = ? 
              AND ma.status = 'completed'
              AND ma.completed_at IS NOT NULL
              AND DATE(ma.completed_at) >= ?
            GROUP BY DATE(ma.completed_at)
            ORDER BY date_str ASC
            """,
            (family_id, start_date)
        )
        return rows

    def get_family_summary(self, family_id: int) -> Dict[str, Any]:
        """
        Retorna l'agregat global de tota la família en una sola consulta.
        """
        row_missions = database.query_one(
            """
            SELECT 
                COUNT(*) AS total_assignments,
                SUM(CASE WHEN ma.status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
                SUM(CASE WHEN ma.status IN ('pending', 'in_progress') THEN 1 ELSE 0 END) AS pending_count,
                SUM(CASE WHEN ma.status = 'waiting_validation' THEN 1 ELSE 0 END) AS waiting_count,
                SUM(CASE WHEN ma.status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count,
                SUM(CASE WHEN ma.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
            FROM mission_assignments ma
            JOIN users u ON u.id = ma.user_id
            WHERE u.family_id = ?
            """,
            (family_id,)
        )

        row_users = database.query_one(
            """
            SELECT 
                COUNT(*) AS total_members,
                COALESCE(SUM(points), 0) AS total_xp
            FROM users
            WHERE family_id = ?
            """,
            (family_id,)
        )

        row_rewards = database.query_one(
            """
            SELECT 
                COUNT(*) AS total_rewards_bought,
                SUM(CASE WHEN rh.delivered = 1 THEN 1 ELSE 0 END) AS rewards_delivered,
                SUM(CASE WHEN rh.delivered = 0 THEN 1 ELSE 0 END) AS rewards_pending,
                COALESCE(SUM(r.points_required), 0) AS total_family_spent
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            JOIN users u ON u.id = rh.user_id
            WHERE u.family_id = ?
            """,
            (family_id,)
        )

        return {
            "total_members": row_users["total_members"] if row_users else 0,
            "total_xp": row_users["total_xp"] if row_users else 0,
            "total_assignments": row_missions["total_assignments"] or 0,
            "completed_count": row_missions["completed_count"] or 0,
            "pending_count": row_missions["pending_count"] or 0,
            "waiting_count": row_missions["waiting_count"] or 0,
            "rejected_count": row_missions["rejected_count"] or 0,
            "cancelled_count": row_missions["cancelled_count"] or 0,
            "rewards_bought": row_rewards["total_rewards_bought"] or 0,
            "rewards_delivered": row_rewards["rewards_delivered"] or 0,
            "rewards_pending": row_rewards["rewards_pending"] or 0,
            "total_family_spent": row_rewards["total_family_spent"] or 0
        }

    def get_family_rewards_stats(self, family_id: int) -> Dict[str, Any]:
        """
        Retorna qui compra més i quines recompenses són les més utilitzades a la família.
        """
        top_buyers = database.query(
            """
            SELECT 
                u.id AS user_id,
                u.name,
                u.avatar,
                COUNT(rh.id) AS count,
                COALESCE(SUM(r.points_required), 0) AS spent
            FROM reward_history rh
            JOIN users u ON u.id = rh.user_id
            JOIN rewards r ON r.id = rh.reward_id
            WHERE u.family_id = ?
            GROUP BY u.id, u.name, u.avatar
            ORDER BY count DESC, spent DESC
            LIMIT 5
            """,
            (family_id,)
        )

        top_rewards = database.query(
            """
            SELECT 
                r.id AS reward_id,
                r.name,
                COALESCE(r.icon, '🎁') AS icon,
                COUNT(rh.id) AS times_redeemed,
                r.points_required AS cost
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            JOIN users u ON u.id = rh.user_id
            WHERE u.family_id = ?
            GROUP BY r.id, r.name, r.icon, r.points_required
            ORDER BY times_redeemed DESC
            LIMIT 5
            """,
            (family_id,)
        )

        return {
            "top_buyers": top_buyers,
            "top_rewards": top_rewards
        }

    def get_evolution_points_by_period(self, user_id: int, period: str = "total") -> List[Dict[str, Any]]:
        """
        Recupera el desplegament d'XP, punts, missions aprovades i rebutjades agrupades per data segons el període.
        """
        where_clause = "WHERE ma.user_id = ?"
        params: list = [user_id]

        now = datetime.now()
        if period == "week":
            start = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            where_clause += " AND ma.completed_at >= ?"
            params.append(start)
        elif period == "month":
            start = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            where_clause += " AND ma.completed_at >= ?"
            params.append(start)
        elif period == "year":
            start = (now - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
            where_clause += " AND ma.completed_at >= ?"
            params.append(start)

        sql = f"""
            SELECT 
                DATE(COALESCE(ma.validated_at, ma.completed_at)) AS date_key,
                SUM(CASE WHEN ma.status = 'completed' THEN COALESCE(ma.completed_points, 10) ELSE 0 END) AS xp_gained,
                SUM(CASE WHEN ma.status = 'completed' THEN COALESCE(ma.coins, 1) ELSE 0 END) AS coins_gained,
                SUM(CASE WHEN ma.status = 'completed' THEN 1 ELSE 0 END) AS approved_count,
                SUM(CASE WHEN ma.status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count
            FROM mission_assignments ma
            {where_clause}
              AND (ma.completed_at IS NOT NULL OR ma.validated_at IS NOT NULL)
            GROUP BY date_key
            ORDER BY date_key ASC
        """
        return database.query(sql, tuple(params))
