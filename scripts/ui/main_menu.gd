extends Control
## Main menu: live forest map + tombol Play/Settings/Quit.

const GAME_SCENE := "res://scenes/game.tscn"

@onready var _bgm: AudioStreamPlayer = $Audio/BGM_Menu
@onready var _sfx: AudioStreamPlayer = $Audio/SFX_Click
@onready var _play: TextureButton = $BottomBar/MenuButtons/BtnPlay
@onready var _settings: TextureButton = $BottomBar/MenuButtons/BtnSettings
@onready var _quit: TextureButton = $BottomBar/MenuButtons/BtnQuit
@onready var _settings_overlay: Control = $SettingsOverlay
@onready var _volume: HSlider = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/VolumeSlider
@onready var _fullscreen: CheckButton = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/FullscreenCheck
@onready var _close: Button = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/Close


func _ready() -> void:
	_setup_live_map()
	_setup_audio()
	_play.pressed.connect(_on_play_pressed)
	_settings.pressed.connect(_on_settings_pressed)
	_quit.pressed.connect(_on_quit_pressed)
	_close.pressed.connect(_on_close_settings)
	_volume.value_changed.connect(_on_volume_changed)
	_fullscreen.toggled.connect(_on_fullscreen_toggled)

	_volume.value = clampf(db_to_linear(AudioServer.get_bus_volume_db(0)) * 100.0, 0.0, 100.0)
	_fullscreen.set_pressed_no_signal(DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN)
	_settings_overlay.hide()
	_play.grab_focus()


func _setup_live_map() -> void:
	var player = get_tree().get_first_node_in_group("player_caravan")
	if player == null:
		return
	_mute_audio(player.get_node_or_null("sound_horse_and_wagon_run_and_boost"))
	_mute_audio(player.get_node_or_null("sound_horse_snort_random_when_idle"))
	player.set("input_enabled", false)
	player.set("external_travel", true)
	player.call("set_traveling", true)


func _setup_audio() -> void:
	var stream := _bgm.stream
	if stream is AudioStreamWAV:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	_bgm.finished.connect(_on_bgm_finished)
	_bgm.play()


func _mute_audio(node: Node) -> void:
	if node is AudioStreamPlayer2D:
		node.volume_db = -80.0


func _play_click() -> void:
	if _sfx.stream != null:
		_sfx.play()


func _on_bgm_finished() -> void:
	_bgm.play()


func _on_play_pressed() -> void:
	_play_click()
	get_tree().change_scene_to_file(GAME_SCENE)


func _on_settings_pressed() -> void:
	_play_click()
	_settings_overlay.show()
	_volume.grab_focus()


func _on_quit_pressed() -> void:
	_play_click()
	get_tree().quit()


func _on_close_settings() -> void:
	_play_click()
	_settings_overlay.hide()


func _on_volume_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(value / 100.0, 0.001)))


func _on_fullscreen_toggled(toggled_on: bool) -> void:
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if toggled_on else DisplayServer.WINDOW_MODE_WINDOWED
	)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE):
		return
	if _settings_overlay.visible:
		_settings_overlay.hide()
		get_viewport().set_input_as_handled()
