extends Sprite2D

## Memutar sheet 30 frame derek sebagai loop idle.

@export var fps: float = 12.0

var _time: float = 0.0

func _process(delta: float) -> void:
	_time += delta * fps
	frame = int(_time) % maxi(hframes, 1)
