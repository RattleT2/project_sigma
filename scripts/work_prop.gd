extends Node2D
## Tempel ke root scene WorkProp_NPC_*.
## Scene perlu punya Marker2D:
## - WorkSpot_for_npc_standing_facing_right
## - WorkSpot_for_npc_standing_facing_left
## AudioStreamPlayer2D opsional, boleh bernama apa saja.

var _spot_right: Marker2D
var _spot_left: Marker2D
var _work_audio: AudioStreamPlayer2D


func _ready() -> void:
	_spot_right = find_child("WorkSpot_for_npc_standing_facing_right", true, false) as Marker2D
	_spot_left = find_child("WorkSpot_for_npc_standing_facing_left", true, false) as Marker2D
	for child in get_children():
		if child is AudioStreamPlayer2D:
			_work_audio = child
			break


func get_nearest_spot(npc_global_pos: Vector2) -> Marker2D:
	if _spot_right == null:
		return _spot_left
	if _spot_left == null:
		return _spot_right
	var distance_right := npc_global_pos.distance_squared_to(_spot_right.global_position)
	var distance_left := npc_global_pos.distance_squared_to(_spot_left.global_position)
	return _spot_right if distance_right <= distance_left else _spot_left


func get_random_spot() -> Marker2D:
	if _spot_right == null:
		return _spot_left
	if _spot_left == null:
		return _spot_right
	return _spot_right if randi() % 2 == 0 else _spot_left


func play_work_sound() -> void:
	if _work_audio != null and _work_audio.stream != null:
		_work_audio.play()
