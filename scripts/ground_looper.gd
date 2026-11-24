extends Node2D

@export var scroll_speed: float = 120.0 # Harus sama dengan Scroll Speed GroundPropSpawner
@export var tilemap_width: float = 600.0

func _process(delta: float) -> void:
	position.x -= scroll_speed * delta
	while position.x <= -tilemap_width:
		position.x += tilemap_width
	while position.x >= tilemap_width:
		position.x -= tilemap_width
