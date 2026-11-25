extends Node2D

## NPC ambient di pinggir jalan saat karavan berjalan.
## Node ini ikut posisi karavan lewat WorldScroll; anak-anaknya bergerak ke kiri.

@export var npc_scenes: Array[PackedScene] = []
@export var scroll_speed := 120.0
@export var spawn_x := 700.0
@export var despawn_x := -700.0
@export var min_distance := 900.0
@export var max_distance := 1500.0
@export var ground_y := 16.0
## Koreksi naik/turun agar kaki NPC menapak tepat di garis tanah (negatif = naik).
@export var ground_offset := -3.0
@export var initial_npc := 1

var _distance := 0.0
var _next_spawn := 0.0


func _ready() -> void:
	_next_spawn = randf_range(min_distance, max_distance)
	for i in initial_npc:
		_spawn(randf_range(-200.0, 500.0))


func _process(delta: float) -> void:
	var step := scroll_speed * delta
	_distance += step
	if _distance >= _next_spawn:
		_spawn(spawn_x)
		_distance = 0.0
		_next_spawn = randf_range(min_distance, max_distance)
	for child in get_children():
		if child is Node2D:
			child.position.x -= step
			if child.position.x < despawn_x:
				child.queue_free()


func _spawn(at_x: float) -> void:
	if npc_scenes.is_empty():
		return
	var packed: PackedScene = npc_scenes.pick_random()
	var npc := packed.instantiate()
	# NPC tidak perlu fisika sendiri; dia hanya ikut scroll dan melambai saat dilewati.
	npc.set("apply_gravity", false)
	npc.set("idle_duration_min", 9999.0)
	npc.set("idle_duration_max", 9999.0)
	add_child(npc)
	npc.set_physics_process(false)
	npc.position = Vector2(at_x, ground_y + ground_offset)
