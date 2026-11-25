extends Control
## Main menu: live forest map + tombol Play/Settings/Quit.

const GAME_SCENE := "res://scenes/game.tscn"

@onready var _bgm: AudioStreamPlayer = $Audio/BGM_Menu
@onready var _sfx: AudioStreamPlayer = $Audio/SFX_Click
@onready var _hover_sfx: AudioStreamPlayer = $Audio/SFX_Hover
@onready var _play: TextureButton = $BottomBar/MenuButtons/BtnPlay
@onready var _settings: TextureButton = $BottomBar/MenuButtons/BtnSettings
@onready var _quit: TextureButton = $BottomBar/MenuButtons/BtnQuit
@onready var _settings_overlay: Control = $SettingsOverlay
@onready var _volume: HSlider = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/VolumeSlider
@onready var _fullscreen: CheckButton = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/FullscreenCheck
@onready var _close: Button = $SettingsOverlay/SettingsCenter/SettingsPanel/Margin/VBox/Close
@onready var _menu_coins: Label = %MenuCoins
@onready var _menu_bar: Control = $MenuBar
@onready var _forge_button: TextureButton = %ForgeButton
@onready var _upgrade_panel: Control = $UpgradePanel
@onready var _continue_overlay: Control = %ContinueOverlay
@onready var _continue_info: Label = %ContinueInfo
@onready var _continue_button: Button = %BtnContinue
@onready var _new_game_button: Button = %BtnNewGame
@onready var _cancel_button: Button = %BtnCancel


func _ready() -> void:
	_setup_live_map()
	_setup_audio()
	_play.pressed.connect(_on_play_pressed)
	_settings.pressed.connect(_on_settings_pressed)
	_quit.pressed.connect(_on_quit_pressed)
	_close.pressed.connect(_on_close_settings)
	_volume.value_changed.connect(_on_volume_changed)
	_fullscreen.toggled.connect(_on_fullscreen_toggled)
	_forge_button.pressed.connect(_on_forge_pressed)
	_continue_button.pressed.connect(_on_continue_game)
	_new_game_button.pressed.connect(_on_new_game)
	_cancel_button.pressed.connect(_on_cancel_continue)
	for button in find_children("*", "BaseButton", true, false):
		(button as BaseButton).mouse_entered.connect(_play_hover)

	_volume.value = clampf(db_to_linear(AudioServer.get_bus_volume_db(0)) * 100.0, 0.0, 100.0)
	_fullscreen.set_pressed_no_signal(DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN)
	_settings_overlay.hide()
	_continue_overlay.hide()
	_play.grab_focus()
	RunState.changed.connect(_refresh_meta)
	RunState.changed.connect(_sync_live_costume)
	_refresh_meta()


func _setup_live_map() -> void:
	var player = get_tree().get_first_node_in_group("player_caravan")
	if player == null:
		return
	_mute_audio(player.get_node_or_null("sound_horse_and_wagon_run_and_boost"))
	_mute_audio(player.get_node_or_null("sound_horse_snort_random_when_idle"))
	player.call("set_customization", RunState.cart_level, RunState.accessories)
	player.set("input_enabled", false)
	player.set("external_travel", true)
	var world_scroll := player.get_parent().get_node_or_null("WorldScroll")
	if world_scroll != null:
		world_scroll.call("set_forced_speed", float(player.get("walk_speed")))
	player.call("set_traveling", true)


func _sync_live_costume() -> void:
	var player = get_tree().get_first_node_in_group("player_caravan")
	if player != null and player.has_method("set_customization"):
		player.call("set_customization", RunState.cart_level, RunState.accessories)


func _setup_audio() -> void:
	if _bgm.stream is AudioStreamWAV:
		var wav := _bgm.stream as AudioStreamWAV
		# Loop tanpa titik loop = diputar 1 frame kosong terus, jadi isi loop_end dulu.
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate) - 1
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	_bgm.finished.connect(_on_bgm_finished)
	_bgm.play()


func _mute_audio(node: Node) -> void:
	if node is AudioStreamPlayer2D:
		node.volume_db = -80.0


func _play_click() -> void:
	if _sfx.stream != null:
		_sfx.play()


func _play_hover() -> void:
	if _hover_sfx.stream != null:
		_hover_sfx.play()


func _on_bgm_finished() -> void:
	_bgm.play()


func _on_play_pressed() -> void:
	_play_click()
	if RunState.has_run():
		_refresh_meta()
		_continue_overlay.show()
		_continue_button.grab_focus()
	else:
		_start_new_run()


func _start_new_run() -> void:
	RunState.new_run()
	get_tree().change_scene_to_file(GAME_SCENE)


func _on_continue_game() -> void:
	_play_click()
	get_tree().change_scene_to_file(GAME_SCENE)


func _on_new_game() -> void:
	_play_click()
	_start_new_run()


func _on_cancel_continue() -> void:
	_play_click()
	_continue_overlay.hide()
	_play.grab_focus()


func _on_forge_pressed() -> void:
	_play_click()
	_upgrade_panel.call("open")


func _refresh_meta() -> void:
	if not is_node_ready():
		return
	_menu_coins.text = "%d koin menu" % RunState.menu_coins
	if RunState.has_run():
		_continue_info.text = "Putaran %d - Turn %d/%d - %d koin in-game" % [
			RunState.round_number(), mini(RunState.turn(), RunState.turns_total()),
			RunState.turns_total(), RunState.coin_balance()
		]
	else:
		_continue_info.text = "Belum ada perjalanan tersimpan."


func _on_settings_pressed() -> void:
	_play_click()
	_menu_bar.hide()
	_settings_overlay.show()
	_volume.grab_focus()


func _on_quit_pressed() -> void:
	_play_click()
	get_tree().quit()


func _on_close_settings() -> void:
	_play_click()
	_settings_overlay.hide()
	_menu_bar.show()


func _on_volume_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(value / 100.0, 0.001)))


func _on_fullscreen_toggled(toggled_on: bool) -> void:
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if toggled_on else DisplayServer.WINDOW_MODE_WINDOWED
	)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE):
		return
	if _upgrade_panel.visible:
		_upgrade_panel.call("close")
		get_viewport().set_input_as_handled()
	elif _continue_overlay.visible:
		_continue_overlay.hide()
		_play.grab_focus()
		get_viewport().set_input_as_handled()
	elif _settings_overlay.visible:
		_settings_overlay.hide()
		_menu_bar.show()
		get_viewport().set_input_as_handled()
