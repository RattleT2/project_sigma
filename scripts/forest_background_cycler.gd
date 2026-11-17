extends Node

# Bergantian antara set Forest (Flat + Forest) dan Swamp (langit + swamp)
# dengan crossfade halus.
@export var min_duration: float = 8.0
@export var max_duration: float = 12.0
@export var fade_time: float = 0.8

@onready var forest_set: Node2D = get_node("../ForestSet")
@onready var swamp_set: Node2D = get_node("../SwampSet")
@onready var rock_spawner: Node2D = get_node("../ForestSet/GroundPropSpawner")
@onready var cloud_spawner: Node2D = get_node("../SwampSet/CloudPropSpawner")

var _showing_swamp: bool = false

func _ready() -> void:
	forest_set.visible = true
	swamp_set.visible = false
	swamp_set.modulate.a = 0.0
	_set_spawner(rock_spawner, true)
	_set_spawner(cloud_spawner, false)
	_schedule_next()

func _schedule_next() -> void:
	var tween := create_tween()
	tween.tween_interval(randf_range(min_duration, max_duration))
	tween.tween_callback(_switch)

func _switch() -> void:
	_showing_swamp = not _showing_swamp
	var tween := create_tween()
	if _showing_swamp:
		swamp_set.visible = true
		swamp_set.modulate.a = 0.0
		_set_spawner(cloud_spawner, true)
		tween.tween_property(swamp_set, "modulate:a", 1.0, fade_time)
		tween.tween_callback(_finish_swamp)
	else:
		forest_set.visible = true
		_set_spawner(rock_spawner, true)
		tween.tween_property(swamp_set, "modulate:a", 0.0, fade_time)
		tween.tween_callback(_finish_forest)
	tween.tween_interval(randf_range(min_duration, max_duration))
	tween.tween_callback(_switch)

func _finish_swamp() -> void:
	forest_set.visible = false
	_set_spawner(rock_spawner, false)

func _finish_forest() -> void:
	swamp_set.visible = false
	_set_spawner(cloud_spawner, false)

func _set_spawner(spawner: Node2D, active: bool) -> void:
	spawner.visible = active
	spawner.set_process(active)
	if not active:
		for child in spawner.get_children():
			child.queue_free()
