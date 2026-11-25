extends Node2D

# Masukkan semua variasi tekstur (pohon, semak, batu) lewat panel Inspector
@export var prop_textures: Array[Texture2D] = []

# Kecepatan gerak dunia/karavan (piksel per detik)
@export var scroll_speed: float = 120.0

# Rentang jarak acak antar kemunculan objek (dalam piksel)
@export var min_distance: float = 150.0
@export var max_distance: float = 400.0

# Koordinat posisi spawn (sesuaikan dengan ukuran layar/viewport kamu)
@export var spawn_x: float = 1000.0    # Di luar batas kanan layar
@export var despawn_x: float = -1000.0 # Di luar batas kiri layar
@export var min_y: float = -16.0      # Tinggi permukaan tanah di scene kamu
@export var max_y: float = -16.0      # Samakan untuk objek tanah; bedakan untuk awan (misal -240 s/d -160)

@export var random_flip_h: bool = true # Balik gambar kiri-kanan secara acak agar lebih variatif

# Parent berisi rumah yang tidak boleh ditimpa (mis. RumahSpawner).
@export var avoid_parent_path: NodePath = ^""

# Jumlah prop yang langsung tampil saat scene dimuat (disebar di layar).
@export var initial_props: int = 3

const HOUSE_CLEARANCE := 24.0 # Jarak aman kiri/kanan antara prop dan rumah

var _distance_traveled: float = 0.0
var _next_spawn_distance: float = 0.0
var _avoid_parent: Node = null

func _ready() -> void:
	if not avoid_parent_path.is_empty():
		_avoid_parent = get_node_or_null(avoid_parent_path)
	# Tentukan jarak acak pertama saat scene mulai
	_next_spawn_distance = randf_range(min_distance, max_distance)
	_spawn_initial_props()

func _process(delta: float) -> void:
	var step: float = scroll_speed * delta
	_distance_traveled += step

	# Cek apakah sudah menempuh jarak yang ditentukan
	if _distance_traveled >= _next_spawn_distance:
		_spawn_random_prop()
		_distance_traveled = 0.0
		_next_spawn_distance = randf_range(min_distance, max_distance)

	# Gerakkan semua objek yang sudah muncul ke kiri, lalu hapus jika keluar layar
	for child in get_children():
		if child is Sprite2D:
			child.position.x -= step
			if child.position.x < despawn_x:
				child.queue_free()

func _spawn_initial_props() -> void:
	var slots: Array[float] = [-430.0, -270.0, 250.0, 410.0, 550.0]
	var usable: Array[float] = []
	var max_width: float = _max_prop_width()
	for x in slots:
		if x >= despawn_x + 40.0 and not _overlaps_house(x, max_width):
			usable.append(x)
	usable.shuffle()
	for i in mini(initial_props, usable.size()):
		_spawn_random_prop(usable[i])

func _max_prop_width() -> float:
	var width := 0.0
	for texture in prop_textures:
		width = maxf(width, texture.get_width())
	return width


func _spawn_random_prop(at_x: float = spawn_x) -> void:
	if prop_textures.is_empty():
		return

	var texture: Texture2D = prop_textures.pick_random()
	if _overlaps_house(at_x, texture.get_width()):
		return

	var prop := Sprite2D.new()
	prop.texture = texture
	
	# Posisikan titik tumpu (pivot) di bagian bawah-tengah gambar agar menapak pas di tanah
	prop.centered = true
	prop.offset.y = -prop.texture.get_height() / 2.0
	
	if random_flip_h:
		prop.flip_h = [true, false].pick_random()

	prop.position = Vector2(at_x, randf_range(min_y, max_y))
	add_child(prop)

# Cek tabrakan horizontal dengan rumah; keduanya bergerak dengan kecepatan sama.
func _overlaps_house(at_x: float, prop_width: float) -> bool:
	if _avoid_parent == null:
		return false
	var prop_center: float = global_position.x + at_x
	for child in _avoid_parent.get_children():
		var house := child as Sprite2D
		if house == null or house.texture == null:
			continue
		var house_width: float = house.texture.get_width() * absf(house.global_scale.x)
		var min_gap: float = (prop_width + house_width) * 0.5 + HOUSE_CLEARANCE
		if absf(prop_center - house.global_position.x) < min_gap:
			return true
	return false
