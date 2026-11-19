extends CharacterBody2D

## Ubah semua animasi idle menjadi run/walk agar karavan tampak berjalan.
func play_run() -> void:
	for node in find_children("*", "AnimatedSprite2D", true, false):
		var sprite := node as AnimatedSprite2D
		if sprite.sprite_frames == null:
			continue
		var current := String(sprite.animation)
		if not current.ends_with("_idle"):
			continue
		var target := current.replace("_idle", "_run")
		if not sprite.sprite_frames.has_animation(target):
			target = _walk_animation(sprite, current.trim_suffix("_idle"))
		if target != "" and sprite.sprite_frames.has_animation(target):
			sprite.play(target)


func _walk_animation(sprite: AnimatedSprite2D, prefix: String) -> String:
	for animation in sprite.sprite_frames.get_animation_names():
		var anim_name := String(animation)
		if anim_name.begins_with(prefix) and "walk" in anim_name and "boost" not in anim_name:
			return anim_name
	return ""
