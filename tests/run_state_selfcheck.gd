extends SceneTree

## Self-check cepat untuk loop utama. Jalankan:
## godot --headless --path . --script tests/run_state_selfcheck.gd

var _failures := 0


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var script = load("res://scripts/autoload/run_state.gd")
	var state = script.new()
	state.save_path = "user://run_state_check.json"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(state.save_path))
	state.load_state()

	state.new_run()
	_check(state.coin_balance() == 500, "modal awal 500")
	_check(state.cart_level == 1 and state.capacity() == 30, "gerobak awal level 1")
	_check(state.turns_total() == 5 and state.target_count() == 1, "nilai awal run")

	_check(state.resupply({"gold": 20}), "resupply")
	_check(state.carried_total() == 20 and state.coin_balance() == 300, "kargo dan coin")
	_check(not state.resupply({"gold": 20}), "kapasitas ditolak")

	state.arrive_at_region("forest")
	_check(state.is_awaiting_delivery(), "tiba menunggu serah terima")
	_check(state.turn() == 1, "turn belum habis sebelum serah terima")
	var delivery: Dictionary = state.deliver_selected({"gold": 16})
	_check(int(delivery.get("revenue", 0)) == 192, "harga jual 120%")
	_check(state.turn() == 2 and state.stock("forest", "gold") == 14, "turn dan delivery")
	_check(not state.is_awaiting_delivery(), "serah terima selesai")

	state.arrive_at_region("village")
	var skipped: Dictionary = state.skip_delivery()
	_check(state.turn() == 3 and int(skipped.get("revenue", 0)) == 0, "skip tetap menghabiskan turn")

	state.run["regions"]["snow"] = {"iron": 6, "gold": 6, "diamond": 16}
	state.run["carried"] = {"iron": 0, "gold": 0, "diamond": 0}
	state.run["turn"] = 5
	state.run["turns_total"] = 5
	state.run["target"] = 1
	state.arrive_at_region("snow")
	delivery = state.deliver_selected({})
	_check(String(delivery.get("result", "")) == "win", "menang saat turn habis")

	var payout: int = state.withdraw()
	_check(payout > 0 and not state.has_run(), "withdraw dan reset run")

	state.menu_coins = 2000
	_check(state.buy_cart_upgrade(), "beli gerobak level 2")
	_check(state.cart_level == 2 and state.capacity() == 36, "kapasitas gerobak level 2")
	_check(state.buy_accessory("capacity"), "beli rak kargo")
	_check(state.buy_accessory("chest"), "beli peti")
	_check(state.buy_accessory("tools"), "beli perkakas")
	_check(state.buy_accessory("lantern"), "beli lentera")
	_check(state.buy_accessory("sack"), "beli karung")
	_check(state.capacity() == 42, "kapasitas maksimal 42")
	_check(is_equal_approx(state.speed_bonus(), 0.15), "speed maksimal +15%")

	state.new_run()
	state.resupply({"diamond": 10})
	state.save_state()
	var loaded = script.new()
	loaded.save_path = state.save_path
	loaded.load_state()
	_check(loaded.has_run() and loaded.carried("diamond") == 10, "save/load")
	_check(loaded.cart_level == 2 and loaded.capacity() == 42, "save/load gerobak")
	_check(loaded.is_accessory_owned("lantern"), "save/load aksesoris")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(state.save_path))
	state.free()
	loaded.free()
	print("RUN_STATE_SELFCHECK_OK" if _failures == 0 else "RUN_STATE_SELFCHECK_FAILED=%d" % _failures)
	quit(1 if _failures > 0 else 0)


func _check(condition: bool, label: String) -> void:
	if condition:
		print("OK: ", label)
	else:
		_failures += 1
		print("FAIL: ", label)
