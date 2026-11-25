extends Control
## Pause menu: Esc toggles pause, Resume/Main Menu/Quit.
## process_mode root harus Always agar tetap bekerja saat tree paused.

@onready var _resume: Button = $Center/Panel/Margin/VBox/BtnResume
@onready var _main_menu: Button = $Center/Panel/Margin/VBox/BtnMainMenu
@onready var _quit: Button = $Center/Panel/Margin/VBox/BtnQuit


func _ready() -> void:
	hide()
	_resume.pressed.connect(_resume_game)
	_main_menu.pressed.connect(_go_main_menu)
	_quit.pressed.connect(_quit_game)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE):
		return
	if get_tree().paused:
		_resume_game()
	else:
		_pause_game()
	get_viewport().set_input_as_handled()


func _pause_game() -> void:
	get_tree().paused = true
	show()
	_resume.grab_focus()


func _resume_game() -> void:
	get_tree().paused = false
	hide()


func _go_main_menu() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/ui/main_menu.tscn")


func _quit_game() -> void:
	get_tree().paused = false
	get_tree().quit()
