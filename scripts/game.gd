extends Node

const STOP_SCENES := {
	&"depot": preload("res://scenes/depot/depot.tscn"),
	&"forest": preload("res://scenes/map/stop/forest_stop.tscn"),
	&"snow": preload("res://scenes/map/stop/snow_stop.tscn"),
	&"desert": preload("res://scenes/map/stop/desert_stop.tscn"),
	&"village": preload("res://scenes/map/stop/village_stop.tscn"),
}
const WALK_SCENES := {
	&"forest": preload("res://scenes/map/forest.tscn"),
	&"snow": preload("res://scenes/map/snow.tscn"),
	&"desert": preload("res://scenes/map/desert.tscn"),
	&"village": preload("res://scenes/map/village.tscn"),
}

const WALK_SECONDS := 10.0
const FOREST_WALK_SECONDS := 15.0
const FADE_SECONDS := 0.35
const STOP_FADE_SECONDS := 0.2
const STOP_VIEW_SECONDS := 2.5
const MAX_TURNS := 10
const DEPARTURE_SPEED := 120.0
const EXIT_MARGIN := 240.0

var current_area_id: StringName = &"depot"
var turn := 1

var _travelling := false

@onready var _host: Node2D = $AreaHost
@onready var _map = $UI/MapMenu
@onready var _fade: ColorRect = $UI/Fade


func _ready() -> void:
	_map.hide()
	_fade.modulate.a = 0.0
	_map.destination_confirmed.connect(_on_destination_confirmed)
	_show_scene(STOP_SCENES[&"depot"], false)
	await get_tree().create_timer(STOP_VIEW_SECONDS).timeout
	_open_map()


func _on_destination_confirmed(area_id: StringName) -> void:
	if _travelling or area_id == current_area_id:
		return
	_travelling = true
	_map.hide()
	turn += 1

	await _drive_off_screen()
	await _fade_to(1.0, FADE_SECONDS)
	var fade_in := FADE_SECONDS
	if WALK_SCENES.has(area_id):
		var walk_area := _show_scene(WALK_SCENES[area_id], true)
		await _fade_to(0.0, FADE_SECONDS)
<<<<<<< HEAD
		await get_tree().create_timer(WALK_SECONDS).timeout
		var walk_player = _find_player(walk_area)
		if walk_player != null:
			walk_player.call("set_traveling", false)
		await _fade_to(1.0, STOP_FADE_SECONDS)
		_show_scene(STOP_SCENES[area_id], false)
		await _fade_to(0.0, STOP_FADE_SECONDS)
	else:
		_show_scene(STOP_SCENES[area_id], false)
		await _fade_to(0.0, FADE_SECONDS)
=======
		var walk_seconds := FOREST_WALK_SECONDS if area_id == &"forest" else WALK_SECONDS
		await get_tree().create_timer(walk_seconds).timeout
		await _fade_to(1.0, STOP_FADE_SECONDS)
		fade_in = STOP_FADE_SECONDS
	_show_scene(STOP_SCENES[area_id])
	await _fade_to(0.0, fade_in)
>>>>>>> origin/develop/map

	current_area_id = area_id
	_travelling = false
	await get_tree().create_timer(STOP_VIEW_SECONDS).timeout
	_open_map()


<<<<<<< HEAD
func _open_map() -> void:
	if _travelling:
		return
	_map.refresh(current_area_id, turn, maxi(MAX_TURNS - turn + 1, 0))
	_map.show()


func _show_scene(scene: PackedScene, traveling: bool) -> Node:
=======
func _drive_off_screen() -> void:
	var scene: Node = _host.get_child(0)
	var caravan: Node2D = null
	for node in scene.find_children("*", "CharacterBody2D", true, false):
		if node.has_method(&"play_run"):
			caravan = node as Node2D
			break
	assert(caravan != null, "Karavan tidak ditemukan di scene aktif.")
	if caravan == null:
		return

	caravan.call(&"play_run")
	var camera := get_viewport().get_camera_2d()
	var target_x: float = camera.get_screen_center_position().x + get_viewport().get_visible_rect().size.x * 0.5 + EXIT_MARGIN
	var duration: float = maxf((target_x - caravan.global_position.x) / DEPARTURE_SPEED, 0.01)
	var tween := create_tween()
	tween.tween_property(caravan, "global_position:x", target_x, duration)
	await tween.finished


func _show_scene(scene: PackedScene) -> void:
>>>>>>> origin/develop/map
	for child in _host.get_children():
		child.queue_free()
	var area := scene.instantiate()
	_host.add_child(area)
	_configure_player(area, traveling)
	return area


func _find_player(area: Node) -> Node:
	if area == null:
		return null
	var grouped := get_tree().get_first_node_in_group("player_caravan")
	if grouped != null and area.is_ancestor_of(grouped):
		return grouped
	for node in area.find_children("*", "", true, false):
		if node.has_method("set_traveling"):
			return node
	return null


func _configure_player(area: Node, traveling: bool) -> void:
	var player = _find_player(area)
	if player == null or not player.has_method("set_traveling"):
		return
	player.set("input_enabled", false)
	player.set("external_travel", true)
	player.call("set_traveling", traveling)
	var area_camera := area.get_node_or_null("Camera2D") as Camera2D
	var player_camera := player.get_node_or_null("Camera2D") as Camera2D
	if area_camera != null and player_camera != null:
		player_camera.enabled = false


func _fade_to(alpha: float, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "modulate:a", alpha, duration)
	await tween.finished
