def generate_or_get_spin_prize(user_id: int):
    """
    Spins the wheel on the server side.
    Returns the prize points (0 for super prize) if eligible, or None if cooldown is active.
    """
    import random
    from datetime import datetime, timezone, timedelta
    uz_tz = timezone(timedelta(hours=5))
    now = datetime.now(uz_tz)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_spin_date, pending_spin_prize FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    last_spin = row[0]
    pending_prize = row[1]

    # Check cooldown
    if last_spin:
        try:
            last_spin_dt = datetime.fromisoformat(last_spin)
            if last_spin_dt.tzinfo is None:
                last_spin_dt = last_spin_dt.replace(tzinfo=uz_tz)
            
            diff = now - last_spin_dt
            if diff.total_seconds() < 24 * 3600:
                conn.close()
                return None  # Cooldown active
        except ValueError:
            if last_spin == now.date().isoformat():
                conn.close()
                return None

    # If we already generated a prize but they haven't claimed it yet
    if pending_prize is not None:
        conn.close()
        return pending_prize

    # Generate new prize
    # Segments based on app.js: 1, 3, 5, 10, 20, 50, Super (0)
    r = random.random()
    if r < 0.40: prize = 1
    elif r < 0.70: prize = 3
    elif r < 0.85: prize = 5
    elif r < 0.95: prize = 10
    elif r < 0.98: prize = 20
    elif r < 0.99: prize = 50
    else: prize = 0

    c.execute("UPDATE users SET pending_spin_prize = ? WHERE user_id = ?", (prize, user_id))
    conn.commit()
    conn.close()
    return prize
