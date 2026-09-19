import re

with open("app/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Insert Daily Bonus Promo Card
wheel_card_end = """                </div>
                
                <!-- Fast Aid Grid -->"""
                
daily_bonus_card = """                </div>
                
                <!-- Daily Bonus Promo Card -->
                <div class="wheel-promo-card daily-bonus-promo" id="btn-open-daily-bonus" style="margin-top: 15px; cursor: pointer;">
                    <div class="wheel-promo-left">
                        <div class="wheel-promo-mini" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                            🎁
                        </div>
                    </div>
                    <div class="wheel-promo-info">
                        <h3>Kunlik bonus</h3>
                        <p>Har kuni kirib, ball oling!</p>
                    </div>
                    <button class="wheel-promo-btn" style="background: transparent; color: rgba(255,255,255,0.5);">
                        <i class="fa-solid fa-chevron-right"></i>
                    </button>
                </div>
                
                <!-- Fast Aid Grid -->"""
text = text.replace(wheel_card_end, daily_bonus_card)

# Insert Daily Bonus Modal
modal_insertion_point = """    <!-- Script ulanishi -->
    <script src="app.js?v=__JS_VERSION__"></script>"""

daily_bonus_modal = """    <!-- DAILY BONUS MODAL -->
    <div id="daily-bonus-modal" class="modal hidden">
        <div class="modal-content" style="background: #111827; max-width: 400px; padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); overflow: visible;">
            <div class="modal-header" style="border: none; padding: 0; margin-bottom: 20px;">
                <span class="close-btn" id="daily-bonus-close" style="position: absolute; top: 15px; right: 15px; background: rgba(255,255,255,0.1); border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; z-index: 10;"><i class="fa-solid fa-xmark"></i></span>
            </div>
            <div class="modal-body" style="text-align: center; padding: 0;">
                <div style="font-size: 3rem; margin-top: -50px; text-shadow: 0 10px 20px rgba(0,0,0,0.5);">🎁</div>
                <h2 style="font-size: 1.5rem; font-weight: 700; color: #fff; margin: 10px 0 5px;">Kunlik bonus</h2>
                <p style="color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 20px;">Botga har kuni kirib boring va bonus oling!<br>7 kunlik seriya uchun maxsus mukofot sizni kutmoqda.</p>
                
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <i class="fa-solid fa-star" style="color: #f59e0b; font-size: 1.2rem;"></i>
                        <span style="color: rgba(255,255,255,0.8); font-weight: 500;">Sizning hozirgi ballaringiz</span>
                    </div>
                    <span id="daily-bonus-current-score" style="color: #f59e0b; font-size: 1.3rem; font-weight: 700;">0</span>
                </div>
                
                <div style="text-align: left; margin-bottom: 15px;">
                    <h3 style="font-size: 1rem; color: #fff; font-weight: 600;">Kunlik bonuslar jadvali (7 kunlik seriya)</h3>
                </div>
                
                <div class="daily-bonus-grid" id="daily-bonus-grid">
                    <!-- Cards injected by JS -->
                </div>
                
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 12px; padding: 15px; display: flex; align-items: flex-start; gap: 12px; text-align: left; margin-bottom: 20px;">
                    <i class="fa-solid fa-circle-info" style="color: #3b82f6; margin-top: 3px;"></i>
                    <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem; line-height: 1.4; margin: 0;">Seriyani uzib qo'ymang! Har kuni kirganingizda bonus olish imkoniyatingiz bor.</p>
                </div>
                
                <button id="btn-claim-daily-bonus" class="wheel-center-btn" style="width: 100%; border-radius: 12px; padding: 16px; margin: 0;">
                    <span class="wheel-center-text" style="font-size: 1rem;">🎁 Bonusni olish</span>
                </button>
            </div>
        </div>
    </div>

    <!-- Script ulanishi -->
    <script src="app.js?v=__JS_VERSION__"></script>"""
text = text.replace(modal_insertion_point, daily_bonus_modal)

with open("app/index.html", "w", encoding="utf-8") as f:
    f.write(text)
