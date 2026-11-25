extends Control

signal destination_confirmed(area_id: StringName)
signal close_requested

const LINE_COLOR := Color(1, 1, 1, 0.22)
const LINE_ACTIVE_COLOR := Color(1, 0.82, 0.35, 0.95)
const LINE_WIDTH := 6.0
const LINE_ACTIVE_WIDTH := 10.0

@onready var _regions: Dictionary = {
	&"village": $MapBoard/Regions/VillageCastle,
	&"snow": $MapBoard/Regions/Snow,
	&"forest": $MapBoard/Regions/Forest,
	&"desert": $MapBoard/Regions/Desert,
	&"depot": $MapBoard/Regions/Depot,
}
@onready var _lines: Dictionary = {
	&"village": $MapBoard/RouteLines/ToVillage,
	&"snow": $MapBoard/RouteLines/ToSnow,
	&"forest": $MapBoard/RouteLines/ToForest,
	&"desert": $MapBoard/RouteLines/ToDesert,
	&"depot": $MapBoard/RouteLines/ToDepot,
}
@onready var _marker: TextureRect = $MapBoard/CaravanMarker
@onready var _confirm: Button = %ConfirmDestinationButton

var _selected_id: StringName = &""


func _ready() -> void:
	for id in _regions:
		var region: Control = _regions[id]
		region.region_hovered.connect(_on_region_hovered)
		region.region_unhovered.connect(_on_region_unhovered)
		region.region_selected.connect(_on_region_selected)
	_confirm.pressed.connect(_on_confirm_pressed)
	%BackButton.pressed.connect(_on_back_pressed)
	refresh()


func refresh() -> void:
	if not RunState.has_run():
		return
	_selected_id = &""
	for id in _regions:
		_regions[id].selected = false
	_confirm.hide()
	%TurnLabel.text = "Putaran %d - Turn %d/%d" % [
		RunState.round_number(), mini(RunState.turn(), RunState.turns_total()), RunState.turns_total()
	]
	%TurnsLeftLabel.text = "%d turn tersisa - target %d wilayah stabil" % [RunState.turns_left(), RunState.target_count()]
	_update_caravan_summary()
	_update_marker()
	_update_lines()
	_set_detail(StringName(RunState.current_area()))


func _on_region_hovered(region: Control) -> void:
	_set_detail(region.area_id)
	_set_line_active(region.area_id, true)


func _on_region_unhovered(region: Control) -> void:
	_set_detail(_selected_id if _selected_id != &"" else StringName(RunState.current_area()))
	_set_line_active(region.area_id, region.area_id == _selected_id)


func _on_region_selected(region: Control) -> void:
	_selected_id = region.area_id
	for id in _regions:
		_regions[id].selected = id == _selected_id
	_set_detail(_selected_id)
	_update_lines()
	_confirm.show()
	_update_confirm_state()


func _set_detail(id: StringName) -> void:
	var key := String(id)
	if key == "depot":
		%AreaNameLabel.text = "Depot Utama"
		%StableBadge.text = "RESUPPLY & BUFF"
		%StableBadge.modulate = Color(0.7, 0.85, 0.95)
		%IronValue.text = "-"
		%DiamondValue.text = "-"
		%CoinValue.text = "-"
		%DistanceRow.text = "Pulang ke Depot: gratis, tanpa turn"
		%CostRow.text = "Depot: resupply & buff"
		%RiskRow.text = "Risiko bandit: -"
	else:
		var data: Dictionary = GameData.REGIONS[key]
		%AreaNameLabel.text = String(data["name"])
		var stable := RunState.is_stable(key)
		%StableBadge.text = "STABIL" if stable else "BELUM STABIL"
		%StableBadge.modulate = Color(0.55, 0.9, 0.55) if stable else Color(0.95, 0.65, 0.45)
		%IronValue.text = "%d / %d" % [RunState.stock(key, "iron"), RunState.need(key, "iron")]
		%DiamondValue.text = "%d / %d" % [RunState.stock(key, "diamond"), RunState.need(key, "diamond")]
		%CoinValue.text = "%d / %d" % [RunState.stock(key, "gold"), RunState.need(key, "gold")]
		%DistanceRow.text = "Estimasi drive: %.0f detik" % RunState.estimated_drive_seconds(key)
		%CostRow.text = "Biaya: 1 turn + serah terima manual"
		var risk := int(GameData.bandit_risk(key))
		if int(RunState.run.get("buffs", {}).get("guard", 0)) > 0:
			risk = 0
		%RiskRow.text = "Risiko bandit: %d%%" % risk
	%ReasonLabel.text = _blocked_reason(String(id))
	_update_confirm_state()


func _blocked_reason(id: String) -> String:
	if id == "":
		return "Pilih wilayah tujuan dulu."
	var check: Dictionary = RunState.can_travel(id)
	return String(check.get("reason", ""))


func _update_confirm_state() -> void:
	var reason := _blocked_reason(String(_selected_id))
	_confirm.disabled = reason != ""
	_confirm.text = "KEMBALI KE DEPOT" if _selected_id == &"depot" else "BERANGKAT"
	if _selected_id != &"":
		_confirm.show()
	else:
		_confirm.hide()


func _update_caravan_summary() -> void:
	%CaravanIron.text = str(RunState.carried("iron"))
	%CaravanDiamond.text = str(RunState.carried("diamond"))
	%CaravanCoin.text = str(RunState.carried("gold"))
	%CaravanCapacity.max_value = RunState.capacity()
	%CaravanCapacity.value = RunState.carried_total()
	%CaravanCapacityValue.text = "%d / %d" % [RunState.carried_total(), RunState.capacity()]
	var buffs := RunState.active_buffs()
	if buffs.is_empty():
		%CaravanEffect.text = "Tanpa efek aktif"
	else:
		var parts: Array[String] = []
		for buff in buffs:
			parts.append("%s (%dT)" % [String(buff["name"]), int(buff["turns"])])
		%CaravanEffect.text = ", ".join(parts)


func _update_marker() -> void:
	var area := StringName(RunState.current_area())
	if not _regions.has(area):
		return
	var anchor: Marker2D = _regions[area].get_node("Anchor")
	_marker.position = anchor.position - _marker.pivot_offset


func _update_lines() -> void:
	var area := StringName(RunState.current_area())
	if not _regions.has(area):
		return
	var from: Vector2 = _regions[area].get_node("Anchor").position
	for id in _lines:
		var line: Line2D = _lines[id]
		line.visible = id != area
		if not line.visible:
			continue
		line.points = PackedVector2Array([from, _regions[id].get_node("Anchor").position])
		_set_line_active(id, id == _selected_id)


func _set_line_active(id: StringName, active: bool) -> void:
	if not _lines.has(id):
		return
	var line: Line2D = _lines[id]
	line.default_color = LINE_ACTIVE_COLOR if active else LINE_COLOR
	line.width = LINE_ACTIVE_WIDTH if active else LINE_WIDTH


func _on_confirm_pressed() -> void:
	if _selected_id == &"" or _blocked_reason(String(_selected_id)) != "":
		return
	destination_confirmed.emit(_selected_id)


func _on_back_pressed() -> void:
	close_requested.emit()
