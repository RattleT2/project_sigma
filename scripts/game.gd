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

const WALK_SECONDS := 4.0
const FADE_SECONDS := 0.35
const STOP_FADE_SECONDS := 0.2
const MAX_TURNS := 10

var current_area_id: StringName = &"depot"
var turn := 1

var _travelling := false
var _can_open_map := true

@onready var _host: Node2D = $AreaHost
@onready var _map = $UI/MapMenu
@onready var _fade: ColorRect = $UI/Fade


func _ready() -> void:
	_map.hide()
	_fade.modulate.a = 0.0
	_map.destination_confirmed.connect(_on_destination_confirmed)
	_show_scene(STOP_SCENES[&"depot"])


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M):
		return
	if not _can_open_map:
		return
	if _map.visible:
		_map.hide()
	else:
		_map.refresh(current_area_id, turn, maxi(MAX_TURNS - turn + 1, 0))
		_map.show()
	get_viewport().set_input_as_handled()


func _on_destination_confirmed(area_id: StringName) -> void:
	if _travelling or area_id == current_area_id:
		return
	_travelling = true
	_can_open_map = false
	_map.hide()
	turn += 1

	await _fade_to(1.0, FADE_SECONDS)
	if WALK_SCENES.has(area_id):
		# Fase perjalanan: scene area live dengan RNG aktif.
		_show_scene(WALK_SCENES[area_id])
		await _fade_to(0.0, FADE_SECONDS)
		await get_tree().create_timer(WALK_SECONDS).timeout
		await _fade_to(1.0, STOP_FADE_SECONDS)
		_show_scene(STOP_SCENES[area_id])
		await _fade_to(0.0, STOP_FADE_SECONDS)
	else:
		_show_scene(STOP_SCENES[area_id])
		await _fade_to(0.0, FADE_SECONDS)

	current_area_id = area_id
	_travelling = false
	_can_open_map = true


func _show_scene(scene: PackedScene) -> void:
	for child in _host.get_children():
		child.queue_free()
	_host.add_child(scene.instantiate())


func _fade_to(alpha: float, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "modulate:a", alpha, duration)
	await tween.finished
