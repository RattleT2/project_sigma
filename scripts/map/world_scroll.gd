extends Node

## Menyelaraskan scroll dunia dengan kecepatan karavan.
## Saat karavan idle, semua background/tanah/props berhenti.

var _parallax_base: Dictionary = {}
var _speed_base: Dictionary = {}


func _ready() -> void:
	var map := get_parent()
	for node in map.find_children("*", "Parallax2D", true, false):
		var parallax := node as Parallax2D
		_parallax_base[parallax] = parallax.autoscroll
		parallax.autoscroll = Vector2.ZERO
	for node in map.find_children("*", "Node", true, false):
		var path := _script_path(node)
		if not (path.contains("ground_looper") or path.contains("prop_spawn") or path.contains("house_group_spawner")):
			continue
		_speed_base[node] = float(node.get("scroll_speed"))
		node.set("scroll_speed", 0.0)


func _process(_delta: float) -> void:
	var player = get_tree().get_first_node_in_group("player_caravan")
	var speed := 0.0
	if player != null and not bool(player.get("external_travel")):
		speed = float(player.velocity.x)
	var ratio := clampf(speed / GameData.BASE_DRIVE_SPEED, -4.0, 4.0)
	for node in _parallax_base:
		var parallax := node as Parallax2D
		var base: Vector2 = _parallax_base[node]
		parallax.autoscroll = Vector2(base.x * ratio, base.y * ratio)
	for node in _speed_base:
		node.set("scroll_speed", float(_speed_base[node]) * ratio)


func _script_path(node: Node) -> String:
	var script = node.get_script()
	if script == null:
		return ""
	return String(script.resource_path)
