extends Node2D
# Contoh perakitan caravan (Godot 4.x). Salin folder caravan_sprites ke res://
# Tempel skrip ini ke Node2D kosong. Semua sprite memakai Centered = false.

const BASE := "res://caravan_sprites/"
const FPS := 8.0

# ---- ganti pilihan di sini --------------------------------------------------
var kuda := "kuda/kuda_1_bay/kuda_1_bay_jalan_12f.png"   # atau kuda_2_putih_abu/kuda_2_putih_abu_jalan_12f.png
var harness := "kuda/harness_coklat/harness_coklat_jalan_12f.png"   # hitam / merah
var pengemudi := "pengemudi/pengemudi_1_pionir_duduk_8f.png"
var badan := "gerobak_A_covered_wagon/A_badan.png"
var kanopi := "gerobak_A_covered_wagon/A_kanopi_krem.png"
var roda := "roda/roda_kayu_8f.png"
var aksesoris := [
	"aksesoris/akses_tong_air.png",
	"aksesoris/akses_tali_gulung.png",
	"aksesoris/akses_sekop_beliung.png",
	"aksesoris/akses_lentera.png",
	"aksesoris/akses_panci_ember.png",
	"aksesoris/akses_karung_atap.png",
]
# -----------------------------------------------------------------------------

var _anim: Array[Sprite2D] = []
var _horse: Array[Sprite2D] = []
var _wheels: Array[Sprite2D] = []
var _gerobak: Node2D
var _t := 0.0

func _make(parent: Node, path: String, pos: Vector2, hframes: int = 1) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(BASE + path)
	s.centered = false
	s.position = pos
	s.hframes = hframes
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	parent.add_child(s)
	if hframes == 8:
		_anim.append(s)
	return s

func _ready() -> void:
	_gerobak = Node2D.new()
	add_child(_gerobak)
	_make(_gerobak, badan, Vector2.ZERO)
	_make(_gerobak, kanopi, Vector2.ZERO)
	for a in aksesoris:
		_make(_gerobak, a, Vector2.ZERO)
	_make(_gerobak, pengemudi, Vector2(96, 32), 8)
	_wheels.append(_make(self, roda, Vector2(7, 67), 1))
	_wheels[-1].hframes = 8     # roda belakang
	_wheels.append(_make(self, roda, Vector2(69, 67), 8))    # roda depan
	_horse.append(_make(self, kuda, Vector2(120, 33), 12))
	_horse.append(_make(self, harness, Vector2(120, 33), 12))

func _process(delta: float) -> void:
	_t += delta
	var f := int(_t * FPS) % 8
	for s in _anim:
		s.frame = f
	for s in _wheels:                     # roda: 8 frame @ 24 FPS
		s.frame = int(_t * 24.0) % 8
	for s in _horse:                      # kuda: 12 frame @ 12 FPS
		s.frame = int(_t * 12.0) % 12
	var bounce := [0, 0, -1, -1, 0, 0, -1, -1]
	_gerobak.position.y = bounce[f]
