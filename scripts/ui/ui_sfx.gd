extends Node
## SFX klik/hover untuk semua BaseButton di scene ini; stream sama dengan main menu.

@onready var _click: AudioStreamPlayer = $SFX_Click
@onready var _hover: AudioStreamPlayer = $SFX_Hover


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for button in get_parent().find_children("*", "BaseButton", true, false):
		_hook(button)


func _hook(button: BaseButton) -> void:
	if not button.pressed.is_connected(_play_click):
		button.pressed.connect(_play_click)
	if not button.mouse_entered.is_connected(_play_hover):
		button.mouse_entered.connect(_play_hover)


func _play_click() -> void:
	if _click.stream != null:
		_click.play()


func _play_hover() -> void:
	if _hover.stream != null:
		_hover.play()
