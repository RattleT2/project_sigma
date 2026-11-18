extends Node2D

# Masukkan semua variasi tekstur (pohon, semak, batu) lewat panel Inspector
@export var prop_textures: Array[Texture2D] = []

# Kecepatan gerak dunia/karavan (piksel per detik)
@export var scroll_speed: float = 120.0

# Rentang jarak acak antar kemunculan objek (dalam piksel)
@export var min_distance: float = 150.0
@export var max_distance: float = 400.0

# Koordinat posisi spawn (sesuaikan dengan ukuran layar/viewport kamu)
@export var spawn_x: float = 450.0    # Di luar batas kanan layar
@export var despawn_x: float = -350.0 # Di luar batas kiri layar
@export var min_y: float = -16.0      # Tinggi permukaan tanah di scene kamu
@export var max_y: float = -16.0      # Samakan untuk objek tanah; bedakan untuk awan (misal -240 s/d -160)

@export var random_flip_h: bool = true # Balik gambar kiri-kanan secara acak agar lebih variatif

var _distance_traveled: float = 0.0
var _next_spawn_distance: float = 0.0

func _ready() -> void:
	# Tentukan jarak acak pertama saat scene mulai
	_next_spawn_distance = randf_range(min_distance, max_distance)

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

func _spawn_random_prop() -> void:
	if prop_textures.is_empty():
		return

	var prop := Sprite2D.new()
	prop.texture = prop_textures.pick_random()
	
	# Posisikan titik tumpu (pivot) di bagian bawah-tengah gambar agar menapak pas di tanah
	prop.centered = true
	prop.offset.y = -prop.texture.get_height() / 2.0
	
	if random_flip_h:
		prop.flip_h = [true, false].pick_random()

	prop.position = Vector2(spawn_x, randf_range(min_y, max_y))
	add_child(prop)
