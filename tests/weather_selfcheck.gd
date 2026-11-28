extends SceneTree

## Self-check pasang cuaca. Jalankan:
## godot --headless --path . --script tests/weather_selfcheck.gd

const SCENES := {
	"res://scenes/map/snow.tscn": "snow",
	"res://scenes/map/stop/snow_stop.tscn": "snow",
	"res://scenes/map/forest.tscn": "drizzle",
	"res://scenes/map/stop/forest_stop.tscn": "drizzle",
	"res://scenes/map/village.tscn": "fog",
	"res://scenes/map/stop/village_stop.tscn": "fog",
}

var _failures := 0


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	for shader in ["rain", "snow", "fog"]:
		_check(shader in WeatherFX.effects(), "shader %s terpasang" % shader)
	for path in SCENES:
		var scene := load(path) as PackedScene
		_check(scene != null, "scene %s termuat" % path)
		if scene == null:
			continue
		var root := scene.instantiate()
		var weather := root.get_node_or_null("Weather") as WeatherSystem
		_check(weather != null, "%s punya Weather" % path)
		if weather != null:
			_check(weather.weather == SCENES[path], "%s cuaca %s" % [path, SCENES[path]])
		root.free()
	print("WEATHER_SELFCHECK_OK" if _failures == 0 else "WEATHER_SELFCHECK_FAILED=%d" % _failures)
	quit(1 if _failures > 0 else 0)


func _check(condition: bool, label: String) -> void:
	if condition:
		print("OK: ", label)
	else:
		_failures += 1
		print("FAIL: ", label)
