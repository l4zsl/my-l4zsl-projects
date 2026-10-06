import json
import random
import time
import tkinter as tk
from pathlib import Path

W, H = 900, 800
HP = 100
P_SIZE = 20
R_SIZE = 10
STEP = 1
UPD = 8
SPRINT_UPD = 4
RAIN_STEP = 1
RAIN_MIN = 3
RAIN_MAX = 5
RAIN_PRINT = 750
RAIN_TIME = 10_000
LINE_H = 20
LINE_GAP = 300
LINE_STEP = 1
SIDE_STEP = 1
LINE_UPD = 6
LINE_SPAWN = 750
WALL_COLOR = "#707070"
HPX, HPY = 10, H - 50
HIGH_SCORE_FILE = Path(__file__).with_name("highscore.json")

WALLS = ((0, H - 100, W, H),)

window = tk.Tk()
window.title("Game")
window.geometry(f"{W}x{H}")

canvas = tk.Canvas(window, width=W, height=H, bg="#afafaf")
canvas.pack()

player = canvas.create_oval(
    W // 2 - P_SIZE // 2,
    H // 2 - P_SIZE // 2,
    W // 2 + P_SIZE // 2,
    H // 2 + P_SIZE // 2,
    fill="#424242",
    outline="#000000",
    width=3,
)

for wall in WALLS:
    canvas.create_rectangle(wall, fill=WALL_COLOR, outline="#505050", width=3, tags=("bottom_cover",))

hp = HP
hp_display = canvas.create_text(
    HPX,
    H - 85,
    anchor="nw",
    text=f"HP: {hp}",
    fill="#202020",
    font=("Arial", 14, "bold"),
    tags=("hud",),
)

timer_display = canvas.create_text(
    W - HPX,
    H - 65,
    anchor="ne",
    text="Time: 0s  Best: 0s",
    fill="#202020",
    font=("Arial", 14, "bold"),
    tags=("hud",),
)
canvas.create_rectangle(HPX, HPY, HPX + 203, HPY + 13, fill="#505050", outline="", tags=("hud",))
hp_bar = canvas.create_rectangle(HPX + 1, HPY + 1, HPX + 1 + 2 * hp, HPY + 11, fill="yellow", outline="", tags=("hud",))

pressed_keys: set[str] = set()
rain_hits: set[int] = set()
line_hits: set[str] = set()
line_rows: dict[str, tuple[list[int], list[int], int, int, int]] = {}
rain_on = False
lines_on = False
game_on = False
game_id = 0
play_again_button: tk.Button | None = None


def load_high_score() -> int:
    try:
        with HIGH_SCORE_FILE.open(encoding="utf-8") as f:
            score = json.load(f).get("high_score_seconds", 0)
        return max(0, int(score))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0


def save_high_score() -> None:
    with HIGH_SCORE_FILE.open("w", encoding="utf-8") as f:
        json.dump({"high_score_seconds": high_score_seconds}, f, indent=2)


high_score_seconds = load_high_score()


def run_ok(id_):
    return game_on and id_ == game_id


def record_high_score(id_):
    global high_score_seconds
    if not run_ok(id_):
        return
    sec = int(time.monotonic() - game_started_at)
    if sec > high_score_seconds:
        high_score_seconds = sec
        try:
            save_high_score()
        except OSError:
            pass


def update_timer(id_):
    if not run_ok(id_):
        return
    record_high_score(id_)
    sec = int(time.monotonic() - game_started_at)
    canvas.itemconfigure(timer_display, text=f"Time: {sec}s  Best: {high_score_seconds}s")
    window.after(250, update_timer, id_)


def key_down(e):
    pressed_keys.add(e.keysym.lower())


def key_up(e):
    pressed_keys.discard(e.keysym.lower())


def make_rain(id_):
    if not run_ok(id_) or not rain_on:
        return
    for _ in range(random.randint(10, 20)):
        side = random.choice(("top", "bottom", "left", "right"))
        if side == "top":
            x, y, dx, dy = random.randint(R_SIZE, W - R_SIZE), 0, 0, RAIN_STEP
        elif side == "bottom":
            x, y, dx, dy = random.randint(R_SIZE, W - R_SIZE), H + R_SIZE, 0, -RAIN_STEP
        elif side == "left":
            x, y, dx, dy = -R_SIZE, random.randint(R_SIZE, H - R_SIZE), RAIN_STEP, 0
        else:
            x, y, dx, dy = W + R_SIZE, random.randint(R_SIZE, H - R_SIZE), -RAIN_STEP, 0

        item = canvas.create_oval(
            x - R_SIZE,
            y - R_SIZE,
            x + R_SIZE,
            y + R_SIZE,
            fill="red",
            outline="",
            tags=("rain",),
        )
        wait = random.randint(RAIN_MIN, RAIN_MAX)
        window.after(wait, move_rain, item, dx, dy, wait, id_)

    canvas.tag_raise("bottom_cover")
    canvas.tag_raise("hud")
    if run_ok(id_) and rain_on:
        window.after(RAIN_PRINT, make_rain, id_)


def move_rain(item, dx, dy, wait, id_):
    if not run_ok(id_) or not canvas.type(item):
        return

    canvas.move(item, dx, dy)
    box = canvas.bbox(item)
    if box is None or box[0] > W or box[1] > H or box[2] < 0 or box[3] < 0:
        canvas.delete(item)
        return

    window.after(wait, move_rain, item, dx, dy, wait, id_)


def stop_rain(id_):
    global rain_on
    if not run_ok(id_):
        return
    rain_on = False
    window.after(50, start_lines_after_rain, id_)


def start_lines_after_rain(id_):
    global lines_on
    if not run_ok(id_):
        return
    if canvas.find_withtag("rain"):
        window.after(50, start_lines_after_rain, id_)
        return

    lines_on = True
    window.after(RAIN_TIME, stop_lines, id_)
    window.after(LINE_SPAWN, make_lines, id_)


def make_lines(id_):
    if not run_ok(id_) or not lines_on:
        return

    gaps = [random.randint(P_SIZE, W - LINE_GAP - P_SIZE)]
    top = -LINE_H
    tag = ""
    parts = []
    start = 0
    for gap in gaps:
        if gap > start:
            item = canvas.create_rectangle(
                start,
                top,
                gap,
                0,
                fill="#505050",
                outline="",
                tags=("lines", tag) if tag else ("lines",),
            )
            parts.append(item)
            if not tag:
                tag = f"line_row_{item}"
                canvas.addtag_withtag(tag, item)
        start = gap + LINE_GAP

    if start < W:
        item = canvas.create_rectangle(
            start,
            top,
            W,
            0,
            fill="#505050",
            outline="",
            tags=("lines", tag) if tag else ("lines",),
        )
        parts.append(item)
        if not tag:
            tag = f"line_row_{item}"
            canvas.addtag_withtag(tag, item)

    line_rows[tag] = (gaps, parts, top, 0, random.choice((-1, 1)))
    window.after(LINE_UPD, move_line_row, tag, LINE_UPD, id_)
    canvas.tag_raise("bottom_cover")
    canvas.tag_raise("hud")
    if run_ok(id_) and lines_on:
        window.after(LINE_SPAWN, make_lines, id_)


def move_line_row(tag, wait, id_):
    if not run_ok(id_) or not canvas.find_withtag(tag):
        line_rows.pop(tag, None)
        return

    gaps, parts, top, offset, dir_ = line_rows[tag]
    min_off = P_SIZE - gaps[0]
    max_off = W - P_SIZE - LINE_GAP - gaps[-1]
    next_off = offset + dir_ * SIDE_STEP
    if next_off < min_off or next_off > max_off:
        dir_ = -dir_
        next_off = offset + dir_ * SIDE_STEP

    top += LINE_STEP
    if top > H:
        canvas.delete(tag)
        line_rows.pop(tag, None)
        return

    start = 0
    for part, gap in zip(parts, gaps):
        left = gap + next_off
        canvas.coords(part, start, top, left, top + LINE_H)
        start = left + LINE_GAP
    canvas.coords(parts[-1], start, top, W, top + LINE_H)
    line_rows[tag] = (gaps, parts, top, next_off, dir_)
    window.after(wait, move_line_row, tag, wait, id_)


def stop_lines(id_):
    global lines_on
    if not run_ok(id_):
        return
    lines_on = False
    window.after(50, start_rain_after_lines, id_)


def start_rain_after_lines(id_):
    global rain_on
    if not run_ok(id_):
        return
    if canvas.find_withtag("lines"):
        window.after(50, start_rain_after_lines, id_)
        return

    rain_on = True
    window.after(RAIN_TIME, stop_rain, id_)
    window.after(RAIN_PRINT, make_rain, id_)


def move_player(id_):
    global hp, rain_hits, line_hits
    if not run_ok(id_):
        return

    dx = dy = 0
    if "left" in pressed_keys or "a" in pressed_keys:
        dx = -STEP
    elif "right" in pressed_keys or "d" in pressed_keys:
        dx = STEP
    if "up" in pressed_keys or "w" in pressed_keys:
        dy = -STEP
    elif "down" in pressed_keys or "s" in pressed_keys:
        dy = STEP

    left, top, right, bottom = canvas.coords(player)
    nx1, ny1, nx2, ny2 = left + dx, top + dy, right + dx, bottom + dy
    if nx1 < 0 or nx2 > W:
        dx = 0
    if ny1 < 0 or ny2 > H:
        dy = 0

    for wall_left, wall_top, wall_right, wall_bottom in WALLS:
        if left + dx < wall_right and right + dx > wall_left and top < wall_bottom and bottom > wall_top:
            dx = 0
            break
    for wall_left, wall_top, wall_right, wall_bottom in WALLS:
        if left + dx < wall_right and right + dx > wall_left and top + dy < wall_bottom and bottom + dy > wall_top:
            dy = 0
            break

    canvas.move(player, dx, dy)
    left, top, right, bottom = canvas.coords(player)
    over = set(canvas.find_overlapping(left, top, right, bottom))
    touch_rain = over.intersection(canvas.find_withtag("rain"))
    new_rain = touch_rain - rain_hits
    touch_lines = over.intersection(canvas.find_withtag("lines"))
    touch_line_rows = {tag for item in touch_lines for tag in canvas.gettags(item) if tag.startswith("line_row_")}
    new_lines = touch_line_rows - line_hits
    dmg = len(new_rain) + len(new_lines)
    if dmg:
        hp = max(0, hp - 20 * dmg)
        canvas.itemconfigure(hp_display, text=f"HP: {hp}")
        canvas.coords(hp_bar, HPX + 1, HPY + 1, HPX + 1 + 2 * hp, HPY + 11)
        for rain_item in new_rain:
            canvas.delete(rain_item)
        for row in new_lines:
            canvas.delete(row)
            line_rows.pop(row, None)

    rain_hits = touch_rain
    line_hits = touch_line_rows
    if hp == 0:
        show_game_over(id_)
        return

    wait = SPRINT_UPD if "shift_l" in pressed_keys or "shift_r" in pressed_keys else UPD
    window.after(wait, move_player, id_)


def show_game_over(id_):
    global game_on, rain_on, lines_on, play_again_button
    if not run_ok(id_):
        return

    record_high_score(id_)
    canvas.itemconfigure(timer_display, text=f"Time: {int(time.monotonic() - game_started_at)}s  Best: {high_score_seconds}s")
    game_on = False
    rain_on = False
    lines_on = False
    canvas.create_text(W // 2, H // 2 - 35, text="GAME OVER", font=("Arial", 32, "bold"), fill="#b00020", tags=("game_over",))
    play_again_button = tk.Button(canvas, text="Play Again", command=start_game)
    canvas.create_window(W // 2, H // 2 + 25, window=play_again_button, tags=("game_over",))
    canvas.tag_raise("game_over")
    canvas.tag_raise("hud")


def start_game():
    global hp, rain_hits, line_hits, rain_on, lines_on, game_on, game_id, play_again_button, game_started_at

    if play_again_button is not None:
        play_again_button.destroy()
        play_again_button = None
    canvas.delete("game_over")
    canvas.delete("rain")
    canvas.delete("lines")
    line_rows.clear()
    game_id += 1
    id_ = game_id
    game_on = True
    game_started_at = time.monotonic()
    hp = 100
    rain_on = True
    lines_on = False
    rain_hits.clear()
    line_hits.clear()
    pressed_keys.clear()
    canvas.coords(player, W // 2 - P_SIZE // 2, H // 2 - P_SIZE // 2, W // 2 + P_SIZE // 2, H // 2 + P_SIZE // 2)
    canvas.itemconfigure(hp_display, text=f"HP: {hp}")
    canvas.itemconfigure(timer_display, text=f"Time: 0s  Best: {high_score_seconds}s")
    canvas.coords(hp_bar, HPX + 1, HPY + 1, HPX + 1 + 2 * hp, HPY + 11)
    window.after(RAIN_TIME, stop_rain, id_)
    window.after(RAIN_PRINT, make_rain, id_)
    window.after(250, update_timer, id_)
    move_player(id_)


def close_game():
    if game_on:
        record_high_score(game_id)
    window.destroy()


window.bind("<KeyPress>", key_down)
window.bind("<KeyRelease>", key_up)
window.protocol("WM_DELETE_WINDOW", close_game)
canvas.focus_set()

start_game()
window.mainloop()
