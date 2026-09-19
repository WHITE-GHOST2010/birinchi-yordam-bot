def get_daily_bonus_info(user_id: int) -> dict:
    """
    Returns information about the user's daily bonus status:
    - streak: Current active streak
    - is_claimed_today: True if they already claimed today's bonus
    """
    from datetime import datetime, timezone, timedelta
    uz_tz = timezone(timedelta(hours=5))
    today_dt = datetime.now(uz_tz).date()
    today_str = today_dt.isoformat()
    yesterday_str = (today_dt - timedelta(days=1)).isoformat()

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT daily_streak, last_checkin_date FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {"streak": 1, "is_claimed_today": False}

    streak, last_date = row
    if streak is None:
        streak = 0

    is_claimed_today = (last_date == today_str)

    if last_date == yesterday_str or last_date == today_str:
        # Streak is active
        current_streak = streak if last_date == today_str else streak + 1
        if current_streak > 7:
            current_streak = 1
    else:
        # Streak broken or never started
        current_streak = 1
        if last_date == today_str: # Just in case
             current_streak = streak

    return {
        "streak": current_streak,
        "is_claimed_today": is_claimed_today
    }
