extends Control

## HUD in-game: topbar, nav bawah, panel Depot/Forge/Jurnal, modal bandit & hasil.

signal map_requested
signal _modal_choice(primary: bool)
signal _delivery_done(result: Dictionary)

@onready var _coin_value: Label = %CoinValue
@onready var _cargo_value: Label = %CargoValue
@onready var _stable_value: Label = %StableValue
@onready var _round_label: Label = %RoundLabel
@onready var _turn_label: Label = %TurnLabel
@onready var _area_label: Label = %AreaLabel

@onready var _panel_host: PanelContainer = %PanelHost
@onready var _board_layer: Control = %BoardLayer
@onready var _shop_panel: VBoxContainer = %ShopPanel
@onready var _forge_panel: Control = %ForgePanel
@onready var _journal_panel: Control = %JournalPanel
@onready var _shop_hint: Label = %ShopHint
@onready var _buy_button: Button = %BuyButton
@onready var _total_cost: Label = %TotalCost
@onready var _shop_cargo: Label = %ShopCargo
@onready var _shop_coin: Label = %ShopCoin
@onready var _buff_guard: Button = %BuffGuard
@onready var _buff_speed: Button = %BuffSpeed
@onready var _buff_bargain: Button = %BuffBargain

@onready var _delivery_panel: VBoxContainer = $PanelHost/Margin/Stack/DeliveryPanel
@onready var _delivery_title: Label = $PanelHost/Margin/Stack/DeliveryPanel/DeliveryTitle
@onready var _delivery_hint: Label = $PanelHost/Margin/Stack/DeliveryPanel/DeliveryHint
@onready var _delivery_sliders: Dictionary = {
	"iron": $PanelHost/Margin/Stack/DeliveryPanel/IronRow/Slider,
	"gold": $PanelHost/Margin/Stack/DeliveryPanel/GoldRow/Slider,
	"diamond": $PanelHost/Margin/Stack/DeliveryPanel/DiamondRow/Slider,
}
@onready var _delivery_infos: Dictionary = {
	"iron": $PanelHost/Margin/Stack/DeliveryPanel/IronRow/Info,
	"gold": $PanelHost/Margin/Stack/DeliveryPanel/GoldRow/Info,
	"diamond": $PanelHost/Margin/Stack/DeliveryPanel/DiamondRow/Info,
}
@onready var _delivery_revenues: Dictionary = {
	"iron": $PanelHost/Margin/Stack/DeliveryPanel/IronRow/Revenue,
	"gold": $PanelHost/Margin/Stack/DeliveryPanel/GoldRow/Revenue,
	"diamond": $PanelHost/Margin/Stack/DeliveryPanel/DiamondRow/Revenue,
}
@onready var _delivery_revenue_value: Label = $PanelHost/Margin/Stack/DeliveryPanel/Summary/RevenueValue
@onready var _delivery_cargo_value: Label = $PanelHost/Margin/Stack/DeliveryPanel/Summary/CargoValue
@onready var _delivery_confirm: Button = $PanelHost/Margin/Stack/DeliveryPanel/Buttons/Confirm
@onready var _delivery_skip: Button = $PanelHost/Margin/Stack/DeliveryPanel/Buttons/Skip

@onready var _travel_progress: ProgressBar = %TravelProgress
@onready var _travel_label: Label = %TravelLabel
@onready var _toast: Label = %Toast
@onready var _modal_layer: Control = %ModalLayer
@onready var _modal_title: Label = %ModalTitle
@onready var _modal_body: Label = %ModalBody
@onready var _modal_primary: Button = %ModalPrimary
@onready var _modal_secondary: Button = %ModalSecondary

@onready var _shop_button: TextureButton = %ShopButton
@onready var _map_button: TextureButton = %MapButton
@onready var _forge_button: TextureButton = %ForgeButton
@onready var _journal_button: TextureButton = %JournalButton

var _sliders: Dictionary = {}
var _qty_labels: Dictionary = {}
var _cost_labels: Dictionary = {}
var _panel_name := ""
var _busy := false
var _last_area := ""
var _toast_tween: Tween


func _ready() -> void:
	_sliders = {"iron": %IronSlider, "gold": %GoldSlider, "diamond": %DiamondSlider}
	_qty_labels = {"iron": %IronQty, "gold": %GoldQty, "diamond": %DiamondQty}
	_cost_labels = {"iron": %IronCost, "gold": %GoldCost, "diamond": %DiamondCost}

	for resource_id in _sliders.keys():
		var id := String(resource_id)
		_sliders[id].value_changed.connect(_on_slider_changed.bind(id))

	_shop_button.pressed.connect(_show_panel.bind("shop"))
	_forge_button.pressed.connect(_show_panel.bind("forge"))
	_journal_button.pressed.connect(_show_panel.bind("journal"))
	_map_button.pressed.connect(_on_map_pressed)
	_journal_panel.connect("map_requested", _on_map_pressed)
	_journal_panel.connect("close_requested", close_panels)
	_buy_button.pressed.connect(_on_buy_pressed)
	_buff_guard.pressed.connect(_buy_buff.bind("guard"))
	_buff_speed.pressed.connect(_buy_buff.bind("speed"))
	_buff_bargain.pressed.connect(_buy_buff.bind("bargain"))
	_modal_primary.pressed.connect(_on_modal_primary)
	_modal_secondary.pressed.connect(_on_modal_secondary)
	for resource_id in _delivery_sliders.keys():
		_delivery_sliders[resource_id].value_changed.connect(_on_delivery_slider_changed)
	_delivery_confirm.pressed.connect(_on_delivery_confirm)
	_delivery_skip.pressed.connect(_on_delivery_skip)

	RunState.changed.connect(refresh)
	_panel_host.hide()
	_board_layer.hide()
	_delivery_panel.hide()
	_modal_layer.hide()
	_travel_progress.hide()
	_travel_label.hide()
	refresh()


func refresh() -> void:
	if not is_node_ready() or not RunState.has_run():
		return
	var cap := RunState.capacity()
	var area := RunState.current_area()
	if area != _last_area:
		_last_area = area
		_reset_sliders()
	_coin_value.text = str(RunState.coin_balance())
	_cargo_value.text = "%d/%d" % [RunState.carried_total(), cap]
	_stable_value.text = "%d/%d" % [RunState.stable_count(), RunState.target_count()]
	_round_label.text = "PUTARAN %d" % RunState.round_number()
	_turn_label.text = "TURN %d/%d" % [mini(RunState.turn(), RunState.turns_total()), RunState.turns_total()]
	_area_label.text = "DEPOT" if area == "depot" else GameData.region_name(area).to_upper()
	_refresh_shop()
	_refresh_journal()


func set_busy(busy: bool) -> void:
	_busy = busy
	for button in [_shop_button, _map_button, _forge_button, _journal_button]:
		button.disabled = busy
	if busy:
		close_panels()


func show_travel_progress(region_id: String) -> void:
	_travel_label.text = "MENUJU %s" % GameData.region_name(region_id).to_upper()
	_travel_label.show()
	_travel_progress.value = 0.0
	_travel_progress.show()


func set_travel_progress(value: float) -> void:
	_travel_progress.value = clampf(value, 0.0, 1.0) * 100.0


func hide_travel_progress() -> void:
	_travel_progress.hide()
	_travel_label.hide()


func open_shop() -> void:
	_show_panel("shop")


func close_panels() -> void:
	_panel_name = ""
	_shop_panel.hide()
	_forge_panel.hide()
	_journal_panel.hide()
	_delivery_panel.hide()
	_panel_host.hide()
	_board_layer.hide()


func show_toast(text: String) -> void:
	if _toast_tween != null:
		_toast_tween.kill()
	_toast.text = text
	_toast.modulate.a = 1.0
	_toast.show()
	_toast_tween = create_tween()
	_toast_tween.tween_interval(1.8)
	_toast_tween.tween_property(_toast, "modulate:a", 0.0, 0.45)
	_toast_tween.tween_callback(_toast.hide)


func ask_bandit(event: Dictionary) -> bool:
	var demand := int(event.get("demand", 0))
	_prepare_modal(
		"BANDIT!",
		"Bandit meminta %d coin. Kalau menolak, dia mencuri %s." % [demand, _format_units(event.get("steal", {}))],
		"BAYAR %d" % demand,
		"AMBIL RISIKO"
	)
	_modal_primary.disabled = RunState.coin_balance() < demand
	return await _ask_modal()


func ask_result(summary: Dictionary) -> bool:
	var stable := int(summary.get("stable", 0))
	var target := int(summary.get("target", 1))
	var score_value := int(summary.get("score", 0))
	var coins := int(summary.get("coins", 0))
	_prepare_modal(
		"PUTARAN SELESAI",
		"Wilayah stabil %d/%d.\nScore %d. Koin in-game %d." % [stable, target, score_value, coins],
		"WITHDRAW (+%d)" % coins,
		"LANJUT"
	)
	return await _ask_modal()


func ask_failure(summary: Dictionary) -> bool:
	var stable := int(summary.get("stable", 0))
	var target := int(summary.get("target", 1))
	_prepare_modal(
		"PUTARAN GAGAL",
		"Hanya %d/%d wilayah yang stabil saat turn habis.\nPerjalanan berakhir." % [stable, target],
		"COBA LAGI",
		"MAIN MENU"
	)
	return await _ask_modal()


func _ask_modal() -> bool:
	close_panels()
	_modal_layer.show()
	_modal_primary.grab_focus()
	var primary: bool = await _modal_choice
	_modal_layer.hide()
	return primary


func _prepare_modal(title: String, body: String, primary_text: String, secondary_text: String) -> void:
	_modal_title.text = title
	_modal_body.text = body
	_modal_primary.text = primary_text
	_modal_secondary.text = secondary_text
	_modal_primary.disabled = false


func _on_modal_primary() -> void:
	_modal_choice.emit(true)


func _on_modal_secondary() -> void:
	_modal_choice.emit(false)


func _show_panel(name: String) -> void:
	if _busy:
		return
	if _panel_name == name and (_panel_host.visible or _board_layer.visible):
		close_panels()
		return
	_panel_name = name
	_delivery_panel.hide()
	if name == "shop":
		_board_layer.hide()
		_shop_panel.show()
		_panel_host.show()
	else:
		_shop_panel.hide()
		_forge_panel.visible = name == "forge"
		_journal_panel.visible = name == "journal"
		_panel_host.hide()
		_board_layer.show()
		if name == "forge":
			_forge_panel.call("open")
	refresh()


func _on_map_pressed() -> void:
	if _busy:
		return
	close_panels()
	map_requested.emit()


func _on_slider_changed(_value: float, resource_id: String) -> void:
	var available := maxi(RunState.capacity() - RunState.carried_total(), 0)
	var total := _planned_total()
	if total > available:
		var slider: HSlider = _sliders[resource_id]
		slider.set_value_no_signal(maxf(slider.value - float(total - available), 0.0))
	_update_shop_costs()


func _update_shop_costs() -> void:
	var total_cost := 0
	var total_units := 0
	for resource_id in _sliders.keys():
		var id := String(resource_id)
		var qty := int(_sliders[id].value)
		var cost := qty * RunState.resupply_price(id)
		_qty_labels[id].text = str(qty)
		_cost_labels[id].text = "%d coin" % cost
		total_cost += cost
		total_units += qty
	_total_cost.text = "%d coin" % total_cost
	_shop_cargo.text = "%d/%d" % [RunState.carried_total() + total_units, RunState.capacity()]
	_shop_coin.text = str(RunState.coin_balance())
	var at_depot := RunState.is_at_depot()
	_buy_button.disabled = not at_depot or total_units <= 0 or total_cost > RunState.coin_balance()
	_shop_hint.text = "Resupply hanya di Depot." if at_depot else "Karavan tidak di Depot. Kembali ke Depot untuk resupply."


func _refresh_shop() -> void:
	if not is_node_ready() or not RunState.has_run():
		return
	var at_depot := RunState.is_at_depot()
	var available := maxi(RunState.capacity() - RunState.carried_total(), 0)
	for resource_id in _sliders.keys():
		var id := String(resource_id)
		_sliders[id].editable = at_depot
		_sliders[id].max_value = float(available)
		if _sliders[id].value > available:
			_sliders[id].set_value_no_signal(available)
	_buff_guard.disabled = not at_depot or RunState.coin_balance() < int(GameData.BUFFS["guard"]["cost"])
	_buff_speed.disabled = not at_depot or RunState.coin_balance() < int(GameData.BUFFS["speed"]["cost"])
	_buff_bargain.disabled = not at_depot or RunState.coin_balance() < int(GameData.BUFFS["bargain"]["cost"])
	_buff_guard.text = "PENJAGA %d" % int(GameData.BUFFS["guard"]["cost"])
	_buff_speed.text = "CEPAT %d" % int(GameData.BUFFS["speed"]["cost"])
	_buff_bargain.text = "TAWAR %d" % int(GameData.BUFFS["bargain"]["cost"])
	_update_shop_costs()


func _on_buy_pressed() -> void:
	if not RunState.is_at_depot():
		show_toast("Resupply hanya bisa di Depot.")
		return
	var quantities := {}
	for resource_id in _sliders.keys():
		var id := String(resource_id)
		quantities[id] = int(_sliders[id].value)
	if _planned_total() <= 0:
		show_toast("Pilih jumlah resource dulu.")
		return
	if RunState.carried_total() + _planned_total() > RunState.capacity():
		show_toast("Melebihi kapasitas karavan.")
		return
	if _planned_cost() > RunState.coin_balance():
		show_toast("Coin tidak cukup.")
		return
	if RunState.resupply(quantities):
		for resource_id in _sliders.keys():
			_sliders[String(resource_id)].set_value_no_signal(0)
		show_toast("Resupply berhasil.")
		_refresh_shop()


func _buy_buff(buff_id: String) -> void:
	if not RunState.is_at_depot():
		show_toast("Buff hanya bisa dibeli di Depot.")
		return
	var cost := int(GameData.BUFFS[buff_id]["cost"])
	if RunState.coin_balance() < cost:
		show_toast("Coin tidak cukup.")
		return
	if RunState.buy_buff(buff_id):
		show_toast("%s aktif selama 2 turn." % String(GameData.BUFFS[buff_id]["name"]))


func _refresh_journal() -> void:
	var summary := "Putaran %d\nTurn %d/%d\nTarget %d wilayah\nStabil %d/%d\nScore %d" % [
		RunState.round_number(), mini(RunState.turn(), RunState.turns_total()), RunState.turns_total(),
		RunState.target_count(), RunState.stable_count(), RunState.target_count(), RunState.score()
	]
	var lines: Array[String] = []
	for region_id in GameData.REGION_ORDER:
		var rid := String(region_id)
		var status := "STABIL" if RunState.is_stable(rid) else "BELUM"
		var demands: Array[String] = []
		for resource_id in GameData.RESOURCES.keys():
			var id := String(resource_id)
			demands.append("%s %d/%d" % [GameData.resource_short(id), RunState.stock(rid, id), RunState.need(rid, id)])
		lines.append("%s [%s]\n%s" % [GameData.region_name(rid), status, ", ".join(demands)])
	var log_entries := RunState.log_entries()
	var log_start := maxi(0, log_entries.size() - 6)
	var log_lines: Array[String] = []
	for i in range(log_start, log_entries.size()):
		log_lines.append("- %s" % String(log_entries[i]))
	_journal_panel.call("set_content", summary, "%s\n\nRIWAYAT\n%s" % ["\n".join(lines), "\n".join(log_lines)])


func ask_delivery(region_id: String) -> Dictionary:
	close_panels()
	_delivery_title.text = "SERAH TERIMA - %s" % GameData.region_name(region_id).to_upper()
	_delivery_hint.text = "Pilih resource yang diserahkan ke %s. Sisa kargo tetap dibawa." % GameData.region_name(region_id)
	for resource_id in _delivery_sliders.keys():
		var id := String(resource_id)
		var remaining := maxi(RunState.need(region_id, id) - RunState.stock(region_id, id), 0)
		var max_amount := RunState.delivery_max(region_id, id)
		var slider: HSlider = _delivery_sliders[id]
		slider.max_value = float(maxi(max_amount, 0))
		slider.set_value_no_signal(0)
		slider.editable = max_amount > 0
		_delivery_infos[id].text = "Bawa %d / butuh %d" % [RunState.carried(id), remaining]
		_delivery_revenues[id].text = "0 coin"
	_delivery_skip.disabled = false
	_delivery_panel.show()
	_panel_host.show()
	_update_delivery_totals()
	var result: Dictionary = await _delivery_done
	_delivery_panel.hide()
	return result


func _on_delivery_slider_changed(_value: float) -> void:
	_update_delivery_totals()


func _update_delivery_totals() -> void:
	var total_revenue := 0
	var total_units := 0
	for resource_id in _delivery_sliders.keys():
		var id := String(resource_id)
		var qty := int(_delivery_sliders[id].value)
		var revenue := qty * GameData.sell_price(id)
		total_units += qty
		total_revenue += revenue
		_delivery_revenues[id].text = "%d coin" % revenue
	_delivery_revenue_value.text = "%d coin" % total_revenue
	_delivery_cargo_value.text = str(RunState.carried_total() - total_units)
	_delivery_confirm.disabled = total_units <= 0


func _on_delivery_confirm() -> void:
	_delivery_confirm.disabled = true
	_delivery_skip.disabled = true
	var quantities := {}
	for resource_id in _delivery_sliders.keys():
		var id := String(resource_id)
		quantities[id] = int(_delivery_sliders[id].value)
	var result: Dictionary = RunState.deliver_selected(quantities)
	_delivery_done.emit(result)


func _on_delivery_skip() -> void:
	_delivery_confirm.disabled = true
	_delivery_skip.disabled = true
	var result: Dictionary = RunState.skip_delivery()
	_delivery_done.emit(result)


func _reset_sliders() -> void:
	for resource_id in _sliders.keys():
		_sliders[String(resource_id)].set_value_no_signal(0)


func _planned_total() -> int:
	var total := 0
	for resource_id in _sliders.keys():
		total += int(_sliders[String(resource_id)].value)
	return total


func _planned_cost() -> int:
	var total := 0
	for resource_id in _sliders.keys():
		var id := String(resource_id)
		total += int(_sliders[id].value) * RunState.resupply_price(id)
	return total


func _format_units(units: Dictionary) -> String:
	var parts: Array[String] = []
	for resource_id in units.keys():
		var id := String(resource_id)
		parts.append("%d %s" % [int(units[id]), GameData.resource_short(id)])
	return ", ".join(parts) if not parts.is_empty() else "kargo"
