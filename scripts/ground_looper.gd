extends Node2D

@export var scroll_speed: float = 120.0 # Harus sama dengan Scroll Speed GroundPropSpawner
@export var tilemap_width: float = 600.0

func _process(delta: float) -> void:
	position.x -= scroll_speed * delta
	# Wrap di sekitar karavan, bukan di titik 0, agar tanah tetap mengikuti kamera.
	var player := get_tree().get_first_node_in_group("player_caravan") as Node2D
	var anchor := player.global_position.x if player != null else 0.0
	while position.x <= anchor - tilemap_width:
		position.x += tilemap_width
	while position.x >= anchor + tilemap_width:
		position.x -= tilemap_width
