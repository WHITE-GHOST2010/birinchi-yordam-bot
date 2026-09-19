with open("app/style.css", "r", encoding="utf-8") as f:
    css = f.read()

# 1. nav-btn
old_nav = """.nav-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    border: none;
    background: none;
    color: var(--hint-color);
    font-size: 10px;
    font-weight: 500;
    width: 70px;
    cursor: pointer;
    transition: color 0.2s;
}"""
new_nav = """.nav-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    border: none;
    background: none;
    color: var(--hint-color);
    font-size: 10px;
    font-weight: 500;
    flex: 1;
    min-width: 0;
    cursor: pointer;
    transition: color 0.2s;
}"""
css = css.replace(old_nav, new_nav)

# 2. first-aid-grid
old_grid = """.first-aid-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}"""
new_grid = """.first-aid-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
    gap: 12px;
}"""
css = css.replace(old_grid, new_grid)

# 3. wheel-outer-ring
old_ring = """.wheel-outer-ring {
    position: relative;
    width: 304px;
    height: 304px;
    border-radius: 50%;
    padding: 2px;"""
new_ring = """.wheel-outer-ring {
    position: relative;
    width: min(100%, 304px);
    aspect-ratio: 1 / 1;
    height: auto;
    border-radius: 50%;
    padding: 2px;"""
css = css.replace(old_ring, new_ring)

# 4. wheel-canvas-wrap
old_canvas = """.wheel-canvas-wrap {
    width: 290px;
    height: 290px;
    border-radius: 50%;
    overflow: hidden;
    position: relative;
    background: #042f2e;"""
new_canvas = """.wheel-canvas-wrap {
    width: calc(100% - 14px);
    height: auto;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
    overflow: hidden;
    position: relative;
    background: #042f2e;"""
css = css.replace(old_canvas, new_canvas)

# 5. body-map-svg-wrapper 1
old_svg1 = """.body-map-svg-wrapper {
    width: 100%;
    max-width: 300px;
    height: 480px;
}"""
new_svg1 = """.body-map-svg-wrapper {
    width: 100%;
    max-width: 300px;
    height: auto;
    aspect-ratio: 300 / 480;
}"""
css = css.replace(old_svg1, new_svg1)

# 6. body-map-svg-wrapper 2
old_svg2 = """.body-map-svg-wrapper {
    width: 100%;
    max-width: 320px;
    height: 460px;
    position: relative;
    z-index: 2;
}"""
new_svg2 = """.body-map-svg-wrapper {
    width: 100%;
    max-width: 320px;
    height: auto;
    aspect-ratio: 320 / 460;
    max-height: 55vh;
    position: relative;
    z-index: 2;
}"""
css = css.replace(old_svg2, new_svg2)

# 7. Media query
media_query = """

/* --- RESPONSIVE ADJUSTMENTS FOR SMALL SCREENS --- */
@media (max-width: 360px) {
    .section-title h2 { font-size: 18px; }
    .calc-card { padding: 12px; }
    .wheel-modal-header h2 { font-size: 20px; }
    .body-map-card { padding: 12px 8px; min-height: 380px; }
    .quiz-options .quiz-option-btn { padding: 12px; }
    .quiz-start-card { padding: 20px 12px; }
    .quiz-start-card h3 { font-size: 18px; }
    .wheel-promo-card { flex-direction: column; text-align: center; gap: 10px; }
    .wheel-promo-btn { width: 100%; justify-content: center; }
}
"""
if "RESPONSIVE ADJUSTMENTS FOR SMALL SCREENS" not in css:
    css += media_query

with open("app/style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("style.css updated!")
