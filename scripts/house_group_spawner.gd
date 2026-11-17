extends Node2D

# Spawn 1-3 rumah per grup dengan jarak, lalu tunggu sampai grup keluar layar.
@export var prop_textures: Array[Texture2D] = []
@export var scroll_speed: float = 120.0
@export var spawn_x: float = 700.0
@export var despawn_x: float = -700.0
@export var ground_y: float = 16.0
@export var min_houses: int = 1
@export var max_houses: int = 3
@export var min_spacing: float = 260.0
@export var max_spacing: float = 420.0
@export var fence_texture: Texture2D
@export var fence_gate_texture: Texture2D
@export var fence_chance: float = 0.6

var _delay_left: float = 0.0

func _ready() -> void:
	_delay_left = randf_range(1.0, 3.0)

func _process(delta: float) -> void:
	var step: float = scroll_speed * delta
	for child in get_children():
		if child is Sprite2D:
			child.position.x -= step
			if child.position.x < despawn_x:
				child.queue_free()

	_delay_left -= delta
	if _delay_left <= 0.0:
		var last_x := _spawn_group()
		_delay_left = (last_x - despawn_x) / scroll_speed + randf_range(0.5, 2.0)

func _spawn_group() -> float:
	var x: float = spawn_x
	if prop_textures.is_empty():
		return x
	var pool := prop_textures.duplicate()
	pool.shuffle()
	var count: int = randi_range(min_houses, max_houses)
	for i in count:
		if i > 0:
			x += randf_range(min_spacing, max_spacing)
		var house := Sprite2D.new()
		house.texture = pool[i % pool.size()]
		house.centered = true
		house.offset.y = -house.texture.get_height() / 2.0
		house.position = Vector2(x, ground_y)
		add_child(house)
		if randf() < fence_chance and fence_texture and fence_gate_texture:
			_add_fence(x, house.texture)
	return x

# Pagar kayu + gerbang di depan rumah; ditambah setelah rumah agar tampil di depannya.
func _add_fence(house_x: float, house_texture: Texture2D) -> void:
	var gate_w: float = fence_gate_texture.get_width()
	var fence_w: float = fence_texture.get_width()
	var span: float = house_texture.get_width() + 24.0
	var count: int = int((span - gate_w) / (2.0 * fence_w))
	assert(count >= 0)
	var left: float = house_x - gate_w * 0.5 - count * fence_w
	for i in count:
		_spawn_fence_piece(fence_texture, left + i * fence_w)
	_spawn_fence_piece(fence_gate_texture, house_x - gate_w * 0.5)
	for i in count:
		_spawn_fence_piece(fence_texture, house_x + gate_w * 0.5 + i * fence_w)

func _spawn_fence_piece(texture: Texture2D, left_x: float) -> void:
	var piece := Sprite2D.new()
	piece.texture = texture
	piece.centered = false
	piece.position = Vector2(left_x, ground_y + 2.0 - texture.get_height())
	add_child(piece)
