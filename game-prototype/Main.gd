extends Node2D
## MORPH — Core-Loop-Prototyp
## Inspiriert von MECCHA CHAMELEON, aber: du verwandelst dich in OBJEKTE
## und musst die Tarnung danach von Hand anpassen (Blend-Mechanik).
##
## Ziel: Überlebe den Timer, ohne vom Seeker-Bot enttarnt zu werden.
## Steuerung:
##   Pfeiltasten = Bewegen
##   F           = In nächstgelegenes Objekt verwandeln (oder zurück zum Blob)
##   Q / E       = Farbton/Helligkeit anpassen (Tarnung verbessern)
##   Leertaste   = Pose einfrieren / lösen
##   Enter       = Neustart (nach Sieg/Niederlage)

# ---------------------------------------------------------------------------
# Konstanten / Welt
# ---------------------------------------------------------------------------
const PLAY_RECT := Rect2(40, 40, 1072, 500)
const PLAYER_SPEED := 200.0
const MORPH_RADIUS := 95.0
const ROUND_TIME := 75.0

const SEEKER_SPEED := 90.0
const VIEW_RANGE := 280.0
const VIEW_HALF_ANGLE := 0.60        # ~34° Halböffnung
const SUSPICION_MAX := 100.0

# Objekt-Typen: Farbe, Form ("box"/"circle"), Größe
var TYPES := {
	"Kiste":   {"color": Color(0.55, 0.38, 0.18), "shape": "box",    "size": Vector2(48, 48)},
	"Pflanze": {"color": Color(0.20, 0.55, 0.22), "shape": "circle", "size": Vector2(42, 42)},
	"Fass":    {"color": Color(0.72, 0.45, 0.15), "shape": "box",    "size": Vector2(42, 60)},
	"Lampe":   {"color": Color(0.88, 0.80, 0.32), "shape": "circle", "size": Vector2(28, 28)},
}

# Im Raum platzierte Objekte
var props := [
	{"pos": Vector2(180, 150), "type": "Kiste"},
	{"pos": Vector2(250, 430), "type": "Pflanze"},
	{"pos": Vector2(520, 180), "type": "Fass"},
	{"pos": Vector2(880, 200), "type": "Kiste"},
	{"pos": Vector2(950, 430), "type": "Pflanze"},
	{"pos": Vector2(640, 460), "type": "Lampe"},
	{"pos": Vector2(420, 320), "type": "Kiste"},
	{"pos": Vector2(770, 360), "type": "Fass"},
]

# ---------------------------------------------------------------------------
# Spieler-Zustand
# ---------------------------------------------------------------------------
var player_pos := Vector2(560, 470)
var morphed_type := ""        # "" = weißer Blob
var shade_error := 0.0        # 0 = perfekte Tarnung; ±0.5 = total daneben
var frozen := false
var moving := false

# ---------------------------------------------------------------------------
# Seeker-Zustand
# ---------------------------------------------------------------------------
var seeker_pos := Vector2(560, 120)
var seeker_facing := Vector2(1, 0)
var waypoints := [
	Vector2(160, 150), Vector2(960, 150),
	Vector2(960, 460), Vector2(160, 460), Vector2(560, 300),
]
var wp_index := 0
var suspicion := 0.0
var player_visible := false

# ---------------------------------------------------------------------------
# Spiel-Status
# ---------------------------------------------------------------------------
var time_left := ROUND_TIME
var state := "play"           # "play" | "win" | "lose"
var prev_keys := {}

func _ready() -> void:
	prev_keys = {KEY_F: false, KEY_SPACE: false, KEY_ENTER: false}

func _process(delta: float) -> void:
	if state == "play":
		_handle_input(delta)
		_update_seeker(delta)
		_update_detection(delta)
		time_left -= delta
		if time_left <= 0.0:
			time_left = 0.0
			state = "win"
	else:
		if _just_pressed(KEY_ENTER):
			_reset()
	queue_redraw()

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
func _just_pressed(key: int) -> bool:
	var down := Input.is_physical_key_pressed(key)
	var was: bool = prev_keys.get(key, false)
	prev_keys[key] = down
	return down and not was

func _handle_input(delta: float) -> void:
	# Bewegung (nur wenn nicht eingefroren)
	moving = false
	if not frozen:
		var dir := Vector2.ZERO
		if Input.is_physical_key_pressed(KEY_LEFT):  dir.x -= 1
		if Input.is_physical_key_pressed(KEY_RIGHT): dir.x += 1
		if Input.is_physical_key_pressed(KEY_UP):    dir.y -= 1
		if Input.is_physical_key_pressed(KEY_DOWN):  dir.y += 1
		if dir != Vector2.ZERO:
			player_pos += dir.normalized() * PLAYER_SPEED * delta
			player_pos.x = clamp(player_pos.x, PLAY_RECT.position.x + 20, PLAY_RECT.end.x - 20)
			player_pos.y = clamp(player_pos.y, PLAY_RECT.position.y + 20, PLAY_RECT.end.y - 20)
			moving = true

	# Tarnung anpassen (Helligkeit Richtung 0 = passend)
	if morphed_type != "":
		if Input.is_physical_key_pressed(KEY_Q):
			shade_error = clamp(shade_error - 0.6 * delta, -0.5, 0.5)
		if Input.is_physical_key_pressed(KEY_E):
			shade_error = clamp(shade_error + 0.6 * delta, -0.5, 0.5)

	# Verwandeln / zurück zum Blob
	if _just_pressed(KEY_F):
		_try_morph()

	# Pose einfrieren
	if _just_pressed(KEY_SPACE):
		frozen = not frozen

func _try_morph() -> void:
	# nächstgelegenes Objekt im Radius suchen
	var best := -1
	var best_d := MORPH_RADIUS
	for i in props.size():
		var d := player_pos.distance_to(props[i].pos)
		if d < best_d:
			best_d = d
			best = i
	if best == -1:
		# nichts in Reichweite -> zurück in den weißen Blob
		morphed_type = ""
		shade_error = 0.0
		frozen = false
		return
	morphed_type = props[best].type
	shade_error = randf_range(-0.45, 0.45)   # frisch verwandelt = falscher Ton
	frozen = false

func _blend() -> float:
	# 1.0 = perfekt getarnt, 0.0 = grottig
	return clamp(1.0 - abs(shade_error) / 0.5, 0.0, 1.0)

func _player_color() -> Color:
	if morphed_type == "":
		return Color(0.95, 0.95, 0.95)
	var base: Color = TYPES[morphed_type].color
	var t: float = clamp(abs(shade_error), 0.0, 1.0)
	var tgt := Color.WHITE if shade_error > 0.0 else Color.BLACK
	return base.lerp(tgt, t)

# ---------------------------------------------------------------------------
# Seeker
# ---------------------------------------------------------------------------
func _update_seeker(delta: float) -> void:
	var target: Vector2 = waypoints[wp_index]
	var to_t := target - seeker_pos
	if to_t.length() < 8.0:
		wp_index = (wp_index + 1) % waypoints.size()
	else:
		var step := to_t.normalized()
		seeker_pos += step * SEEKER_SPEED * delta
		seeker_facing = step

func _update_detection(delta: float) -> void:
	# Sichtbarkeit prüfen (Sichtkegel)
	player_visible = false
	var to_p := player_pos - seeker_pos
	var dist := to_p.length()
	if dist <= VIEW_RANGE and dist > 0.001:
		var ang: float = abs(seeker_facing.angle_to(to_p.normalized()))
		if ang <= VIEW_HALF_ANGLE:
			player_visible = true

	if player_visible:
		var risk := 0.0
		if morphed_type == "":
			risk = 65.0                      # weißer Blob = sofort verdächtig
		else:
			if moving:        risk += 48.0   # Bewegung im Blickfeld
			if not frozen:    risk += 10.0   # nicht eingefroren wirkt "lebendig"
			risk += (1.0 - _blend()) * 42.0  # schlechte Tarnung
		if dist < 95.0:
			risk += 25.0                     # Seeker inspiziert aus der Nähe
		suspicion += risk * delta
	else:
		suspicion -= 28.0 * delta            # vergisst langsam wieder

	suspicion = clamp(suspicion, 0.0, SUSPICION_MAX)
	if suspicion >= SUSPICION_MAX:
		state = "lose"

func _reset() -> void:
	player_pos = Vector2(560, 470)
	morphed_type = ""
	shade_error = 0.0
	frozen = false
	seeker_pos = Vector2(560, 120)
	seeker_facing = Vector2(1, 0)
	wp_index = 0
	suspicion = 0.0
	time_left = ROUND_TIME
	state = "play"

# ---------------------------------------------------------------------------
# Rendering (Immediate Mode)
# ---------------------------------------------------------------------------
func _draw() -> void:
	# Boden + Wände
	draw_rect(PLAY_RECT, Color(0.16, 0.17, 0.20), true)
	draw_rect(PLAY_RECT, Color(0.35, 0.36, 0.42), false, 3.0)

	# Sichtkegel des Seekers
	_draw_view_cone()

	# Objekte im Raum
	for p in props:
		_draw_shape(p.pos, p.type, TYPES[p.type].color, false)

	# Spieler
	if morphed_type == "":
		draw_circle(player_pos, 18.0, _player_color())
	else:
		_draw_shape(player_pos, morphed_type, _player_color(), true)

	# Seeker
	draw_circle(seeker_pos, 16.0, Color(0.90, 0.25, 0.25))
	draw_circle(seeker_pos + seeker_facing * 10.0, 5.0, Color.WHITE)

	_draw_hud()

func _draw_shape(pos: Vector2, type: String, color: Color, is_player: bool) -> void:
	var meta: Dictionary = TYPES[type]
	if meta.shape == "box":
		var sz: Vector2 = meta.size
		draw_rect(Rect2(pos - sz / 2.0, sz), color, true)
		draw_rect(Rect2(pos - sz / 2.0, sz), color.darkened(0.3), false, 2.0)
	else:
		draw_circle(pos, meta.size.x / 2.0, color)
		draw_arc(pos, meta.size.x / 2.0, 0, TAU, 24, color.darkened(0.3), 2.0)
	if is_player and frozen:
		# kleiner Marker, dass die Pose gehalten wird
		draw_arc(pos, meta.size.x / 2.0 + 8.0, 0, TAU, 24, Color(0.4, 0.9, 1.0, 0.6), 2.0)

func _draw_view_cone() -> void:
	var pts := PackedVector2Array()
	pts.append(seeker_pos)
	var base := seeker_facing.angle()
	var steps := 14
	for i in steps + 1:
		var a := base - VIEW_HALF_ANGLE + (2.0 * VIEW_HALF_ANGLE) * float(i) / float(steps)
		pts.append(seeker_pos + Vector2(cos(a), sin(a)) * VIEW_RANGE)
	var col := Color(0.95, 0.85, 0.30, 0.10)
	if player_visible:
		col = Color(0.95, 0.35, 0.30, 0.16)
	draw_colored_polygon(pts, col)

func _draw_hud() -> void:
	var font := ThemeDB.fallback_font
	var fs := 18

	# Timer + Status oben
	draw_string(font, Vector2(50, 30), "Zeit: %0.0f s" % time_left,
		HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
	var mt := morphed_type if morphed_type != "" else "Blob (weiß)"
	draw_string(font, Vector2(260, 30), "Form: %s   Blend: %0.0f%%   %s" %
		[mt, _blend() * 100.0, ("EINGEFROREN" if frozen else "")],
		HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.8, 0.9, 1.0))

	# Verdachtsbalken
	var bar := Rect2(820, 16, 280, 20)
	draw_rect(bar, Color(0.1, 0.1, 0.12), true)
	var frac := suspicion / SUSPICION_MAX
	var fill := Color(0.3, 0.85, 0.3).lerp(Color(0.95, 0.2, 0.2), frac)
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * frac, bar.size.y)), fill, true)
	draw_rect(bar, Color(0.5, 0.5, 0.55), false, 2.0)
	draw_string(font, Vector2(820, 12), "Verdacht", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.WHITE)

	# Steuerungs-Hinweis unten
	draw_string(font, Vector2(50, 600),
		"Pfeile = Bewegen   F = Verwandeln   Q/E = Tarnung anpassen   Leertaste = Pose einfrieren",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.75, 0.75, 0.8))
	draw_string(font, Vector2(50, 624),
		"Tipp: In ein Objekt verwandeln, mit Q/E auf 100% Blend bringen, dann einfrieren wenn der Seeker schaut.",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.6, 0.6, 0.65))

	# End-Screens
	if state != "play":
		draw_rect(Rect2(0, 0, 1152, 648), Color(0, 0, 0, 0.55), true)
		var msg := "ÜBERLEBT! 🦎" if state == "win" else "ENTTARNT!"
		var col := Color(0.4, 0.95, 0.5) if state == "win" else Color(0.95, 0.4, 0.4)
		draw_string(font, Vector2(420, 300), msg, HORIZONTAL_ALIGNMENT_LEFT, -1, 48, col)
		draw_string(font, Vector2(440, 360), "Enter = Neue Runde", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color.WHITE)
