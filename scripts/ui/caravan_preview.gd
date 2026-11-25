extends SubViewportContainer

## Preview karavan di Forge. Player memakai preview_mode agar tidak ikut game.

@onready var _player = $SubViewport/Player
@onready var _camera: Camera2D = $SubViewport/Camera2D


func _ready() -> void:
	var player_camera := _player.get_node_or_null("Camera2D") as Camera2D
	if player_camera != null:
		player_camera.enabled = false
	_player.set("input_enabled", false)
	_player.set("external_travel", true)
	_camera.make_current()


func show_customization(cart_level: int, accessories: Dictionary) -> void:
	if _player.has_method("set_customization"):
		_player.call("set_customization", cart_level, accessories)
