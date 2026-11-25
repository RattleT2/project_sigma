extends Control

## Overlay Forge di main menu. Isi preview/upgrade memakai CostumeForge bersama.

@onready var _forge = %CostumeForge
@onready var _close_button: Button = %CloseButton


func _ready() -> void:
	hide()
	_close_button.pressed.connect(close)


func open() -> void:
	show()
	_forge.call("open")
	_close_button.grab_focus()


func close() -> void:
	hide()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
		close()
		get_viewport().set_input_as_handled()
