extends Node

## State perjalanan + progres meta. Autoload sebagai RunState.

signal changed

const SAVE_VERSION := 3
const SAVE_PATH := "user://caravan_save.json"

var save_path := SAVE_PATH
var menu_coins := 0
var cart_level := 1
var accessories := {
	"capacity": false,
	"chest": false,
	"tools": false,
	"lantern": false,
	"sack": false,
}
var run: Dictionary = {}
var active := false

# Dipakai tes headless agar jarak drive bisa dipersingkat.
var drive_distance_scale := 1.0
var bandit_enabled := true


func _ready() -> void:
	load_state()


func has_run() -> bool:
	return active and not run.is_empty()


func current_area() -> String:
	if run.is_empty():
		return "depot"
	return String(run.get("area", "depot"))


func is_at_depot() -> bool:
	return current_area() == "depot"


func coin_balance() -> int:
	return int(run.get("coins", 0)) if has_run() else 0


func turn() -> int:
	return int(run.get("turn", 1)) if has_run() else 1


func turns_total() -> int:
	return int(run.get("turns_total", 0)) if has_run() else 0


func turns_left() -> int:
	return maxi(turns_total() - turn() + 1, 0)


func round_number() -> int:
	return int(run.get("round", 1)) if has_run() else 1


func target_count() -> int:
	return int(run.get("target", 1)) if has_run() else 1


func capacity() -> int:
	var total := GameData.BASE_CAPACITY + int(GameData.cart_data(cart_level)["capacity"])
	for accessory_id in GameData.ACCESSORY_ORDER:
		var id := String(accessory_id)
		if is_accessory_owned(id):
			total += int(GameData.ACCESSORIES[id]["capacity"])
	return total


func speed_bonus() -> float:
	var bonus := float(GameData.cart_data(cart_level)["speed"])
	for accessory_id in GameData.ACCESSORY_ORDER:
		var id := String(accessory_id)
		if is_accessory_owned(id):
			bonus += float(GameData.ACCESSORIES[id]["speed"])
	return bonus


func drive_speed_scale() -> float:
	return 1.0 + speed_bonus()


func drive_distance(region_id: String) -> float:
	return GameData.route_seconds(current_area(), region_id) * GameData.BASE_DRIVE_SPEED * drive_distance_scale


func estimated_drive_seconds(region_id: String) -> float:
	return GameData.route_seconds(current_area(), region_id) / maxf(drive_speed_scale(), 0.01)


func cart_name() -> String:
	return GameData.cart_name(cart_level)


func cart_body_level() -> int:
	return GameData.cart_body(cart_level)


func is_accessory_owned(accessory_id: String) -> bool:
	return bool(accessories.get(accessory_id, false))


func owned_accessories() -> Array:
	var result: Array = []
	for accessory_id in GameData.ACCESSORY_ORDER:
		var id := String(accessory_id)
		if is_accessory_owned(id):
			result.append(id)
	return result


func is_awaiting_delivery() -> bool:
	return has_run() and bool(run.get("awaiting_delivery", false))


func pending_result() -> String:
	return String(run.get("pending_result", "")) if has_run() else ""


func carried_total() -> int:
	if not has_run():
		return 0
	var total := 0
	for resource_id in GameData.RESOURCES.keys():
		total += carried(String(resource_id))
	return total


func carried(resource_id: String) -> int:
	return int(run.get("carried", {}).get(resource_id, 0))


func stock(region_id: String, resource_id: String) -> int:
	return int(run.get("regions", {}).get(region_id, {}).get(resource_id, 0))


func need(region_id: String, resource_id: String) -> int:
	return GameData.need_for(region_id, round_number(), resource_id)


func is_stable(region_id: String) -> bool:
	for resource_id in GameData.RESOURCES.keys():
		if stock(region_id, String(resource_id)) < need(region_id, String(resource_id)):
			return false
	return true


func stable_count() -> int:
	if not has_run():
		return 0
	var count := 0
	for region_id in GameData.REGION_ORDER:
		if is_stable(String(region_id)):
			count += 1
	return count


func target_met() -> bool:
	return stable_count() >= target_count()


func score() -> int:
	if not has_run():
		return 0
	return int(run.get("delivered", 0)) * 10 + coin_balance() + stable_count() * 100


func resupply_price(resource_id: String) -> int:
	var price := GameData.buy_price(resource_id)
	if int(run.get("buffs", {}).get("bargain", 0)) > 0:
		return int(ceil(float(price) * 0.8))
	return price


func new_run() -> void:
	run = _default_run()
	active = true
	_seed_regions()
	await_save()
	changed.emit()


func continue_round() -> void:
	if not has_run():
		return
	var next_round := round_number() + 1
	run["round"] = next_round
	run["turn"] = 1
	run["turns_total"] = GameData.turns_for_round(next_round)
	run["target"] = GameData.target_regions(next_round)
	run["area"] = "depot"
	run["awaiting_delivery"] = false
	run["pending_result"] = ""
	_seed_regions()
	_log("Putaran %d dimulai: target %d wilayah stabil." % [next_round, int(run["target"])])
	await_save()
	changed.emit()


func withdraw() -> int:
	if not has_run():
		return 0
	var payout := coin_balance()
	menu_coins += payout
	active = false
	run = {}
	await_save()
	changed.emit()
	return payout


func abandon_run() -> void:
	active = false
	run = {}
	await_save()
	changed.emit()


func buy_cart_upgrade() -> bool:
	if cart_level >= GameData.MAX_CART_LEVEL:
		return false
	if menu_coins < GameData.CART_UPGRADE_COST:
		return false
	menu_coins -= GameData.CART_UPGRADE_COST
	cart_level += 1
	await_save()
	changed.emit()
	return true


func buy_accessory(accessory_id: String) -> bool:
	if not GameData.ACCESSORIES.has(accessory_id) or is_accessory_owned(accessory_id):
		return false
	var cost := int(GameData.ACCESSORIES[accessory_id]["cost"])
	if menu_coins < cost:
		return false
	menu_coins -= cost
	accessories[accessory_id] = true
	await_save()
	changed.emit()
	return true


func resupply(quantities: Dictionary) -> bool:
	if not has_run() or not is_at_depot():
		return false
	var total_units := 0
	var total_cost := 0
	for resource_id in GameData.RESOURCES.keys():
		var id := String(resource_id)
		var qty := int(quantities.get(id, 0))
		if qty < 0:
			return false
		total_units += qty
		total_cost += qty * resupply_price(id)
	if total_units <= 0:
		return false
	if carried_total() + total_units > capacity():
		return false
	if total_cost > coin_balance():
		return false
	run["coins"] = coin_balance() - total_cost
	for resource_id in GameData.RESOURCES.keys():
		var id := String(resource_id)
		run["carried"][id] = carried(id) + int(quantities.get(id, 0))
	_log("Resupply %d unit (-%d coin)." % [total_units, total_cost])
	await_save()
	changed.emit()
	return true


func buy_buff(buff_id: String) -> bool:
	if not has_run() or not is_at_depot() or not GameData.BUFFS.has(buff_id):
		return false
	var data: Dictionary = GameData.BUFFS[buff_id]
	var cost := int(data["cost"])
	if coin_balance() < cost:
		return false
	run["coins"] = coin_balance() - cost
	run["buffs"][buff_id] = int(data["turns"])
	_log("Membeli buff %s (-%d coin)." % [String(data["name"]), cost])
	await_save()
	changed.emit()
	return true


func can_travel(region_id: String) -> Dictionary:
	if not has_run():
		return {"ok": false, "reason": "Belum ada perjalanan aktif."}
	if is_awaiting_delivery():
		return {"ok": false, "reason": "Selesaikan serah terima dulu."}
	var area := String(region_id)
	if area == current_area():
		return {"ok": false, "reason": "Karavan sudah berada di sini."}
	if area == "depot":
		return {"ok": true, "reason": ""}
	if not GameData.REGIONS.has(area):
		return {"ok": false, "reason": "Wilayah tidak dikenal."}
	if turns_left() <= 0:
		return {"ok": false, "reason": "Turn sudah habis."}
	if carried_total() <= 0:
		return {"ok": false, "reason": "Kargo kosong. Resupply di Depot."}
	var useful := false
	for resource_id in GameData.RESOURCES.keys():
		var id := String(resource_id)
		if carried(id) > 0 and stock(area, id) < need(area, id):
			useful = true
			break
	if not useful:
		return {"ok": false, "reason": "Kargo tidak dibutuhkan wilayah ini."}
	return {"ok": true, "reason": ""}


func roll_bandit(region_id: String) -> Dictionary:
	if not bandit_enabled or not has_run() or not GameData.REGIONS.has(region_id):
		return {}
	if int(run.get("buffs", {}).get("guard", 0)) > 0:
		return {"blocked": true}
	if randf() >= GameData.bandit_risk(region_id) / 100.0:
		return {}
	var steal := _random_steal()
	if steal.is_empty():
		return {}
	return {
		"blocked": false,
		"demand": 30 + round_number() * 10,
		"steal": steal,
	}


func resolve_bandit(event: Dictionary, pay: bool) -> void:
	if not has_run() or event.is_empty() or bool(event.get("blocked", false)):
		return
	var demand := int(event.get("demand", 0))
	if pay and coin_balance() >= demand:
		run["coins"] = coin_balance() - demand
		_log("Membayar bandit %d coin agar kargo aman." % demand)
	else:
		var steal: Dictionary = event.get("steal", {})
		var stolen := 0
		for resource_id in steal.keys():
			var id := String(resource_id)
			var amount := mini(int(steal[id]), carried(id))
			if amount > 0:
				run["carried"][id] = carried(id) - amount
				stolen += amount
		_log("Bandit mencuri %d unit kargo." % stolen)
	await_save()
	changed.emit()


func arrive_at_region(region_id: String) -> void:
	if not has_run() or not GameData.REGIONS.has(region_id):
		return
	run["area"] = String(region_id)
	run["awaiting_delivery"] = true
	run["visited"][String(region_id)] = true
	_log("Tiba di %s. Pilih resource yang diserahkan." % GameData.region_name(region_id))
	_check_quests()
	await_save()
	changed.emit()


func delivery_max(region_id: String, resource_id: String) -> int:
	return mini(carried(resource_id), maxi(need(region_id, resource_id) - stock(region_id, resource_id), 0))


func deliver_selected(quantities: Dictionary) -> Dictionary:
	if not has_run() or not is_awaiting_delivery():
		return _result_payload({}, 0, "")
	var area := current_area()
	var delivered := {}
	var revenue := 0
	for resource_id in GameData.RESOURCES.keys():
		var id := String(resource_id)
		var amount := clampi(int(quantities.get(id, 0)), 0, delivery_max(area, id))
		if amount <= 0:
			continue
		run["carried"][id] = carried(id) - amount
		run["regions"][area][id] = stock(area, id) + amount
		delivered[id] = amount
		revenue += amount * GameData.sell_price(id)
		run["delivered"] = int(run.get("delivered", 0)) + amount
	run["coins"] = coin_balance() + revenue
	run["awaiting_delivery"] = false
	_log("Menyerahkan %d unit ke %s (+%d coin)." % [_units(delivered), GameData.region_name(area), revenue])
	if is_stable(area):
		run["ever_stable"][area] = true
	var keep_region := area if is_stable(area) else ""
	var turn_result := _advance_turn(keep_region)
	_check_quests()
	await_save()
	changed.emit()
	return _result_payload(delivered, revenue, String(turn_result.get("result", "")))


func skip_delivery() -> Dictionary:
	if not has_run() or not is_awaiting_delivery():
		return _result_payload({}, 0, "")
	var area := current_area()
	run["awaiting_delivery"] = false
	_log("Tidak ada resource yang diserahkan di %s." % GameData.region_name(area))
	var turn_result := _advance_turn("")
	_check_quests()
	await_save()
	changed.emit()
	return _result_payload({}, 0, String(turn_result.get("result", "")))


func end_turn() -> String:
	if not has_run() or is_at_depot() or is_awaiting_delivery() or pending_result() != "":
		return ""
	_log("Turn diakhiri di %s." % GameData.region_name(current_area()))
	var turn_result := _advance_turn("")
	_check_quests()
	await_save()
	changed.emit()
	return String(turn_result.get("result", ""))


func return_to_depot() -> void:
	if not has_run():
		return
	run["area"] = "depot"
	run["awaiting_delivery"] = false
	_log("Kembali ke Depot.")
	await_save()
	changed.emit()


func result_summary() -> Dictionary:
	return {
		"result": pending_result(),
		"stable": stable_count(),
		"target": target_count(),
		"score": score(),
		"coins": coin_balance(),
		"turns_left": turns_left(),
	}


func log_entries() -> Array:
	return run.get("log", [])


func is_quest_done(quest_id: String) -> bool:
	if not has_run():
		return false
	var done = run.get("quests_done", [])
	return typeof(done) == TYPE_ARRAY and done.has(quest_id)


func quest_progress(quest_id: String) -> int:
	if not has_run() or not GameData.QUESTS.has(quest_id):
		return 0
	var data: Dictionary = GameData.QUESTS[quest_id]
	match String(data["type"]):
		"delivered":
			return int(run.get("delivered", 0))
		"visited":
			return _flag_count(run.get("visited", {}))
		"stable":
			return _flag_count(run.get("ever_stable", {}))
		"rounds":
			return int(run.get("rounds_won", 0))
	return 0


func active_buffs() -> Array:
	var result: Array = []
	for buff_id in GameData.BUFFS.keys():
		var id := String(buff_id)
		var turns := int(run.get("buffs", {}).get(id, 0))
		if turns > 0:
			result.append({"id": id, "name": String(GameData.BUFFS[id]["name"]), "turns": turns})
	return result


func save_state() -> void:
	var payload := {
		"version": SAVE_VERSION,
		"menu_coins": menu_coins,
		"cart_level": cart_level,
		"accessories": accessories,
		"run": run if active else {},
	}
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		return
	file.store_string(JSON.stringify(payload))
	file.close()


func load_state() -> void:
	if not FileAccess.file_exists(save_path):
		return
	var file := FileAccess.open(save_path, FileAccess.READ)
	if file == null:
		return
	var text := file.get_as_text()
	file.close()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		_quarantine_save()
		return
	menu_coins = maxi(int(parsed.get("menu_coins", 0)), 0)
	accessories = {"capacity": false, "chest": false, "tools": false, "lantern": false, "sack": false}
	var loaded_cart := int(parsed.get("cart_level", 0))
	var loaded_accessories = parsed.get("accessories", null)
	if loaded_cart > 0 or typeof(loaded_accessories) == TYPE_DICTIONARY:
		cart_level = clampi(loaded_cart if loaded_cart > 0 else 1, 1, GameData.MAX_CART_LEVEL)
		if typeof(loaded_accessories) == TYPE_DICTIONARY:
			for accessory_id in GameData.ACCESSORY_ORDER:
				var id := String(accessory_id)
				accessories[id] = bool(loaded_accessories.get(id, false))
	else:
		# Migrasi save lama: costume_level atau upgrades.
		var legacy_level := int(parsed.get("costume_level", 0))
		if legacy_level <= 0:
			var legacy = parsed.get("upgrades", {})
			var legacy_step := 0
			if typeof(legacy) == TYPE_DICTIONARY:
				legacy_step = maxi(int(legacy.get("capacity", 0)), int(legacy.get("speed", 0)))
			legacy_level = 1 + clampi(legacy_step, 0, 2)
		cart_level = 1 if legacy_level <= 2 else GameData.MAX_CART_LEVEL
		if legacy_level == 2:
			accessories["capacity"] = true
			accessories["chest"] = true
			accessories["tools"] = true
		elif legacy_level >= 3:
			for accessory_id in GameData.ACCESSORY_ORDER:
				accessories[String(accessory_id)] = true
	var loaded_run = parsed.get("run", {})
	if typeof(loaded_run) == TYPE_DICTIONARY and not loaded_run.is_empty():
		run = _normalize_run(loaded_run)
		active = true
	else:
		run = {}
		active = false


func _default_run() -> Dictionary:
	return {
		"round": 1,
		"turn": 1,
		"turns_total": GameData.turns_for_round(1),
		"target": GameData.target_regions(1),
		"coins": GameData.START_COINS,
		"carried": _empty_resources(),
		"regions": _new_regions(),
		"buffs": {"guard": 0, "speed": 0, "bargain": 0},
		"area": "depot",
		"awaiting_delivery": false,
		"delivered": 0,
		"visited": _empty_region_flags(),
		"ever_stable": _empty_region_flags(),
		"rounds_won": 0,
		"quests_done": [],
		"score": 0,
		"pending_result": "",
		"log": ["Perjalanan dimulai di Depot."],
	}


func _seed_regions() -> void:
	if not has_run():
		return
	for region_id in GameData.REGION_ORDER:
		var rid := String(region_id)
		for resource_id in GameData.RESOURCES.keys():
			var id := String(resource_id)
			var floor_stock := GameData.round_start_stock(rid, round_number(), id)
			run["regions"][rid][id] = maxi(stock(rid, id), floor_stock)


func _normalize_run(source: Dictionary) -> Dictionary:
	var base := _default_run()
	for key in base.keys():
		if source.has(key):
			base[key] = source[key]

	base["round"] = maxi(int(base.get("round", 1)), 1)
	base["turns_total"] = maxi(int(base.get("turns_total", GameData.turns_for_round(int(base["round"])))), 1)
	base["turn"] = clampi(int(base.get("turn", 1)), 1, int(base["turns_total"]) + 1)
	base["target"] = clampi(int(base.get("target", GameData.target_regions(int(base["round"])))), 1, 4)
	base["coins"] = maxi(int(base.get("coins", 0)), 0)
	base["delivered"] = maxi(int(base.get("delivered", 0)), 0)
	base["area"] = String(base.get("area", "depot"))
	if base["area"] != "depot" and not GameData.REGIONS.has(base["area"]):
		base["area"] = "depot"
	base["awaiting_delivery"] = bool(base.get("awaiting_delivery", false))
	if base["area"] == "depot":
		base["awaiting_delivery"] = false

	var carried_source = source.get("carried", {})
	base["carried"] = _empty_resources()
	if typeof(carried_source) == TYPE_DICTIONARY:
		for resource_id in GameData.RESOURCES.keys():
			var id := String(resource_id)
			base["carried"][id] = maxi(int(carried_source.get(id, 0)), 0)

	var regions_source = source.get("regions", {})
	base["regions"] = _new_regions()
	if typeof(regions_source) == TYPE_DICTIONARY:
		for region_id in GameData.REGION_ORDER:
			var rid := String(region_id)
			var region_source = regions_source.get(rid, {})
			if typeof(region_source) != TYPE_DICTIONARY:
				continue
			for resource_id in GameData.RESOURCES.keys():
				var id := String(resource_id)
				base["regions"][rid][id] = maxi(int(region_source.get(id, 0)), 0)

	base["visited"] = _empty_region_flags()
	var visited_source = source.get("visited", {})
	if typeof(visited_source) == TYPE_DICTIONARY:
		var visited: Dictionary = visited_source
		for region_id in GameData.REGION_ORDER:
			var rid := String(region_id)
			base["visited"][rid] = bool(visited.get(rid, false))

	base["ever_stable"] = _empty_region_flags()
	var stable_source = source.get("ever_stable", {})
	if typeof(stable_source) == TYPE_DICTIONARY:
		var stable_flags: Dictionary = stable_source
		for region_id in GameData.REGION_ORDER:
			var rid := String(region_id)
			base["ever_stable"][rid] = bool(stable_flags.get(rid, false))

	base["rounds_won"] = maxi(int(base.get("rounds_won", 0)), 0)
	base["quests_done"] = []
	var quests_source = source.get("quests_done", [])
	if typeof(quests_source) == TYPE_ARRAY:
		for quest_id in quests_source:
			var qid := String(quest_id)
			if GameData.QUESTS.has(qid) and not base["quests_done"].has(qid):
				base["quests_done"].append(qid)

	var buffs_source = source.get("buffs", {})
	base["buffs"] = {"guard": 0, "speed": 0, "bargain": 0}
	if typeof(buffs_source) == TYPE_DICTIONARY:
		for buff_id in GameData.BUFFS.keys():
			var id := String(buff_id)
			base["buffs"][id] = maxi(int(buffs_source.get(id, 0)), 0)

	var log_source = source.get("log", [])
	base["log"] = log_source if typeof(log_source) == TYPE_ARRAY else []
	base["pending_result"] = String(base.get("pending_result", ""))
	if base["pending_result"] == "" and int(base["turn"]) > int(base["turns_total"]):
		base["pending_result"] = "win" if _stable_count_for(base) >= int(base["target"]) else "lose"
	base["score"] = maxi(int(base.get("score", 0)), 0)
	return base


func _advance_turn(supplied_region: String = "") -> Dictionary:
	run["turn"] = turn() + 1
	var result := ""
	if int(run["turn"]) > turns_total():
		result = "win" if target_met() else "lose"
		run["pending_result"] = result
		if result == "win":
			run["rounds_won"] = int(run.get("rounds_won", 0)) + 1
		run["score"] = score()
	else:
		# Wilayah yang baru disuplai tidak langsung decay di turn yang sama.
		_apply_decay(supplied_region)
		_tick_buffs()
	return {
		"result": result,
		"stable": stable_count(),
		"target": target_count(),
		"score": score(),
		"turns_left": turns_left(),
	}


func _apply_decay(skip_region: String = "") -> void:
	for region_id in GameData.REGION_ORDER:
		var rid := String(region_id)
		if rid == skip_region:
			continue
		var decay := 1 if is_stable(rid) else 2
		for resource_id in GameData.RESOURCES.keys():
			var id := String(resource_id)
			run["regions"][rid][id] = maxi(stock(rid, id) - decay, 0)


func _tick_buffs() -> void:
	for buff_id in GameData.BUFFS.keys():
		var id := String(buff_id)
		run["buffs"][id] = maxi(int(run["buffs"].get(id, 0)) - 1, 0)


func _result_payload(delivered: Dictionary, revenue: int, result: String) -> Dictionary:
	return {
		"result": result,
		"delivered": delivered,
		"revenue": revenue,
		"stable": stable_count(),
		"target": target_count(),
		"score": score(),
		"turns_left": turns_left(),
	}


func _random_steal() -> Dictionary:
	var options: Array = []
	for resource_id in GameData.RESOURCES.keys():
		var id := String(resource_id)
		if carried(id) > 0:
			options.append(id)
	if options.is_empty():
		return {}
	var chosen := String(options[randi() % options.size()])
	return {chosen: mini(randi_range(1, 3), carried(chosen))}


func _stable_count_for(source: Dictionary) -> int:
	var count := 0
	var round_value := int(source.get("round", 1))
	for region_id in GameData.REGION_ORDER:
		var rid := String(region_id)
		var stable := true
		for resource_id in GameData.RESOURCES.keys():
			var id := String(resource_id)
			var stock_value := int(source.get("regions", {}).get(rid, {}).get(id, 0))
			if stock_value < GameData.need_for(rid, round_value, id):
				stable = false
				break
		if stable:
			count += 1
	return count


func _empty_resources() -> Dictionary:
	var result := {}
	for resource_id in GameData.RESOURCES.keys():
		result[String(resource_id)] = 0
	return result


func _new_regions() -> Dictionary:
	var result := {}
	for region_id in GameData.REGION_ORDER:
		result[String(region_id)] = _empty_resources()
	return result


func _empty_region_flags() -> Dictionary:
	var result := {}
	for region_id in GameData.REGION_ORDER:
		result[String(region_id)] = false
	return result


func _flag_count(source) -> int:
	if typeof(source) != TYPE_DICTIONARY:
		return 0
	var flags: Dictionary = source
	var count := 0
	for region_id in GameData.REGION_ORDER:
		if bool(flags.get(String(region_id), false)):
			count += 1
	return count


func _check_quests() -> void:
	if not has_run():
		return
	for quest_id in GameData.QUEST_ORDER:
		var id := String(quest_id)
		if is_quest_done(id):
			continue
		var data: Dictionary = GameData.QUESTS[id]
		if quest_progress(id) < int(data["target"]):
			continue
		var done: Array = run.get("quests_done", [])
		done.append(id)
		run["quests_done"] = done
		run["coins"] = coin_balance() + int(data["reward"])
		_log("Quest selesai: %s (+%d coin)." % [String(data["name"]), int(data["reward"])])


func _units(quantities: Dictionary) -> int:
	var total := 0
	for key in quantities.keys():
		total += int(quantities[key])
	return total


func _log(text: String) -> void:
	if not has_run():
		return
	var entries: Array = run.get("log", [])
	entries.append(text)
	while entries.size() > 30:
		entries.pop_front()
	run["log"] = entries


func _quarantine_save() -> void:
	var directory := DirAccess.open("user://")
	if directory != null:
		directory.rename(save_path.get_file(), "%s.corrupt" % save_path.get_file())


func await_save() -> void:
	save_state()
