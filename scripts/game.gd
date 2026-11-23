extends Node

const MAIN_MENU := "res://scenes/ui/main_menu.tscn"
const STOP_SCENES := {
	&"depot": preload("res://scenes/depot/depot.tscn"),
	&"forest": preload("res://scenes/map/stop/forest_stop.tscn"),
	&"snow": preload("res://scenes/map/stop/snow_stop.tscn"),
	&"desert": preload("res://scenes/map/stop/desert_stop.tscn"),
	&"village": preload("res://scenes/map/stop/village_stop.tscn"),
}
const WALK_SCENES := {
	&"forest": preload("res://scenes/map/forest.tscn"),
	&"snow": preload("res://scenes/map/snow.tscn"),
	&"desert": preload("res://scenes/map/desert.tscn"),
	&"village": preload("res://scenes/map/village.tscn"),
}

const FADE_SECONDS := 0.35
const STOP_FADE_SECONDS := 0.2
const EXIT_MARGIN := 240.0
const BASE_BOOST_SPEED := 220.0

var departure_speed := 420.0
var _travelling := false

@onready var _host: Node2D = $AreaHost
@onready var _map = $UI/MapMenu
@onready var _hud = $UI/HUD
@onready var _fade: ColorRect = $UI/Fade


func _ready() -> void:
	_map.hide()
	_fade.modulate.a = 0.0
	if not RunState.has_run():
		RunState.new_run()
	_map.destination_confirmed.connect(_on_destination_confirmed)
	_map.close_requested.connect(_close_map)
	_hud.map_requested.connect(_open_map)
	RunState.changed.connect(_sync_player_customization)
	_show_scene(_current_stop_scene(), false)
	_hud.refresh()

	var result := RunState.pending_result()
	if result != "":
		_hud.set_busy(true)
		_handle_pending_result()
	elif RunState.is_awaiting_delivery():
		_hud.set_busy(true)
		_handle_pending_delivery()
	elif RunState.is_at_depot():
		_hud.open_shop()
	else:
		_hud.show_toast("Buka peta untuk memilih tujuan berikutnya.")


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M):
		return
	if _travelling or RunState.pending_result() != "" or RunState.is_awaiting_delivery():
		return
	if _map.visible:
		_close_map()
	else:
		_open_map()
	get_viewport().set_input_as_handled()


func _open_map() -> void:
	if _travelling or RunState.pending_result() != "" or RunState.is_awaiting_delivery():
		return
	if not RunState.has_run():
		return
	_hud.close_panels()
	_map.refresh()
	_map.show()
	_hud.hide()


func _close_map() -> void:
	_map.hide()
	_hud.show()
	_hud.refresh()


func _on_destination_confirmed(area_id: StringName) -> void:
	if _travelling:
		return
	var area := String(area_id)
	var check: Dictionary = RunState.can_travel(area)
	if not bool(check.get("ok", false)):
		_close_map()
		_hud.show_toast(String(check.get("reason", "Tidak bisa berangkat.")))
		return
	_close_map()
	if area == "depot":
		await _return_to_depot()
	else:
		await _travel_to_region(area)


func _travel_to_region(area: String) -> void:
	_travelling = true
	_hud.set_busy(true)
	await _fade_to(1.0, FADE_SECONDS)
	var walk_area := _show_scene(WALK_SCENES[StringName(area)], false)
	await _fade_to(0.0, FADE_SECONDS)

	var player = _find_player(walk_area)
	if player == null:
		_hud.set_busy(false)
		_travelling = false
		return

	var speed_scale := RunState.drive_speed_scale()
	player.set("input_enabled", true)
	player.set("external_travel", false)
	player.set("walk_speed", GameData.BASE_DRIVE_SPEED * speed_scale)
	player.set("boost_speed", BASE_BOOST_SPEED * speed_scale)
	player.call("stop_move")
	var area_camera := walk_area.get_node_or_null("Camera2D") as Camera2D
	var player_camera := player.get_node_or_null("Camera2D") as Camera2D
	if area_camera != null:
		area_camera.enabled = false
	if player_camera != null:
		player_camera.enabled = true
		player_camera.zoom = Vector2(2.4, 2.4)
		player_camera.make_current()

	var start_x: float = player.global_position.x
	var distance := maxf(RunState.drive_distance(area), 1.0)
	var target_x := start_x + distance
	var bandit_event: Dictionary = {}
	var bandit_at := randf_range(0.45, 0.7)
	_hud.show_travel_progress(area)
	_hud.show_toast("Panah kanan / D untuk jalan, Space untuk boost.")

	while player.global_position.x < target_x:
		await get_tree().process_frame
		if get_tree().paused:
			continue
		var progress := clampf((player.global_position.x - start_x) / distance, 0.0, 1.0)
		_hud.set_travel_progress(progress)
		if bandit_event.is_empty() and progress >= bandit_at:
			bandit_event = RunState.roll_bandit(area)
			if not bandit_event.is_empty():
				if bool(bandit_event.get("blocked", false)):
					_hud.show_toast("Penjaga mengusir bandit.")
				else:
					player.set("input_enabled", false)
					player.call("stop_move")
					var pay: bool = await _hud.ask_bandit(bandit_event)
					RunState.resolve_bandit(bandit_event, pay)
					player.set("input_enabled", true)

	_hud.hide_travel_progress()
	player.set("input_enabled", false)
	player.set("external_travel", true)
	player.call("stop_move")
	player.call("set_traveling", false)

	await _fade_to(1.0, STOP_FADE_SECONDS)
	RunState.arrive_at_region(area)
	_show_scene(STOP_SCENES[StringName(area)], false)
	await _fade_to(0.0, STOP_FADE_SECONDS)
	_hud.set_busy(true)
	var delivery: Dictionary = await _hud.ask_delivery(area)
	_hud.set_busy(false)
	_hud.refresh()
	var revenue := int(delivery.get("revenue", 0))
	_hud.show_toast("Tiba di %s. +%d coin." % [GameData.region_name(area), revenue])

	var result := String(delivery.get("result", ""))
	if result != "":
		await _resolve_result(result)
	_travelling = false


func _return_to_depot() -> void:
	if RunState.is_awaiting_delivery():
		_hud.show_toast("Selesaikan serah terima dulu.")
		return
	_travelling = true
	_hud.set_busy(true)
	await _drive_off_screen()
	await _fade_to(1.0, FADE_SECONDS)
	RunState.return_to_depot()
	_show_scene(STOP_SCENES[&"depot"], false)
	await _fade_to(0.0, FADE_SECONDS)
	_hud.set_busy(false)
	_hud.refresh()
	_hud.open_shop()
	_hud.show_toast("Tiba di Depot. Resupply sebelum berangkat lagi.")
	_travelling = false


func _handle_pending_result() -> void:
	var result := RunState.pending_result()
	if result == "":
		_hud.set_busy(false)
		return
	await _resolve_result(result)


func _handle_pending_delivery() -> void:
	if not RunState.is_awaiting_delivery():
		_hud.set_busy(false)
		return
	var area := RunState.current_area()
	var delivery: Dictionary = await _hud.ask_delivery(area)
	_hud.set_busy(false)
	_hud.refresh()
	var result := String(delivery.get("result", ""))
	if result != "":
		await _resolve_result(result)


func _resolve_result(result: String) -> void:
	_hud.set_busy(true)
	if result == "win":
		var withdraw: bool = await _hud.ask_result(RunState.result_summary())
		if withdraw:
			RunState.withdraw()
			get_tree().change_scene_to_file(MAIN_MENU)
		else:
			RunState.continue_round()
			_show_scene(STOP_SCENES[&"depot"], false)
			_hud.refresh()
			_hud.set_busy(false)
			_hud.open_shop()
			_hud.show_toast("Putaran %d dimulai. Target %d wilayah." % [RunState.round_number(), RunState.target_count()])
			_travelling = false
	else:
		var retry: bool = await _hud.ask_failure(RunState.result_summary())
		if retry:
			RunState.new_run()
			get_tree().reload_current_scene()
		else:
			RunState.abandon_run()
			get_tree().change_scene_to_file(MAIN_MENU)


func _current_stop_scene() -> PackedScene:
	var area := StringName(RunState.current_area())
	return STOP_SCENES.get(area, STOP_SCENES[&"depot"])


func _show_scene(scene: PackedScene, traveling := false) -> Node:
	for child in _host.get_children():
		_host.remove_child(child)
		child.queue_free()
	var area := scene.instantiate()
	_host.add_child(area)
	_configure_player(area, traveling)
	return area


func _find_player(area: Node) -> Node:
	if area == null:
		return null
	for node in area.find_children("*", "", true, false):
		if node.has_method("set_traveling"):
			return node
	return null


func _configure_player(area: Node, traveling: bool) -> void:
	var player = _find_player(area)
	if player == null or not player.has_method("set_traveling"):
		return
	player.call("set_customization", RunState.cart_level, RunState.accessories)
	player.set("input_enabled", false)
	player.set("external_travel", true)
	player.call("set_traveling", traveling)
	var area_camera := area.get_node_or_null("Camera2D") as Camera2D
	var player_camera := player.get_node_or_null("Camera2D") as Camera2D
	if area_camera != null and player_camera != null:
		player_camera.enabled = false


func _drive_off_screen() -> void:
	if _host.get_child_count() == 0:
		return
	var scene: Node = _host.get_child(0)
	var caravan: Node2D = null
	for node in scene.find_children("*", "CharacterBody2D", true, false):
		if node.has_method(&"play_run"):
			caravan = node as Node2D
			break
	if caravan == null:
		return
	caravan.call(&"play_run")
	var camera := get_viewport().get_camera_2d()
	var target_x: float
	if camera != null:
		target_x = camera.get_screen_center_position().x + get_viewport().get_visible_rect().size.x * 0.5 + EXIT_MARGIN
	else:
		target_x = caravan.global_position.x + 1200.0
	var duration: float = maxf((target_x - caravan.global_position.x) / departure_speed, 0.05)
	var tween := create_tween()
	tween.tween_property(caravan, "global_position:x", target_x, duration)
	await tween.finished


func _sync_player_customization() -> void:
	if _host.get_child_count() == 0:
		return
	var player = _find_player(_host.get_child(0))
	if player != null and player.has_method("set_customization"):
		player.call("set_customization", RunState.cart_level, RunState.accessories)


func _fade_to(alpha: float, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "modulate:a", alpha, duration)
	await tween.finished
