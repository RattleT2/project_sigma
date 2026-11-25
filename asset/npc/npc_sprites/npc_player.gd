extends Node2D
# Pemutar NPC (Godot 4.x). Salin folder npc_sprites ke res://
# Contoh: $NPC.npc_name = "pandai_besi"; $NPC.play_anim("menempa")

const FRAME := Vector2i(56, 56)
const ANCHOR := Vector2(28, 52)      # titik kaki di dalam frame
@export var npc_name := "petani_pria"
@export var default_anim := "diam"
@export var folder := "res://npc_sprites/"

var _spr: AnimatedSprite2D

func _ready() -> void:
	_spr = AnimatedSprite2D.new()
	_spr.centered = false
	_spr.position = -ANCHOR
	_spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_spr)
	_spr.sprite_frames = _build_frames()
	play_anim(default_anim)

func _build_frames() -> SpriteFrames:
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	var dir := DirAccess.open(folder + npc_name)
	for f in dir.get_files():
		if not f.ends_with(".png"):
			continue
		# <npc>_<anim>_<n>f.png
		var stem := f.get_basename()
		var parts := stem.trim_prefix(npc_name + "_").rsplit("_", true, 1)
		var anim := parts[0]
		var n := int(parts[1].trim_suffix("f"))
		var tex: Texture2D = load(folder + npc_name + "/" + f)
		sf.add_animation(anim)
		sf.set_animation_speed(anim, 30.0)
		sf.set_animation_loop(anim, true)
		for i in n:
			var at := AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(i * FRAME.x, 0, FRAME.x, FRAME.y)
			sf.add_frame(anim, at)
	return sf

func play_anim(anim: String) -> void:
	if _spr.sprite_frames.has_animation(anim):
		_spr.play(anim)

func face(right: bool) -> void:
	_spr.flip_h = not right
	_spr.position.x = -ANCHOR.x if right else -(FRAME.x - ANCHOR.x)
