extends Control

signal destination_confirmed(area_id: StringName)

# shortcut: data placeholder statis; ganti dengan TurnManager/RouteManager/ResourceManager saat wiring.
const AREA_DATA := {
	&"village": {"name": "Village & Castle", "stable": true, "iron": 8, "iron_need": 12, "diamond": 3, "diamond_need": 6, "coin": 14, "coin_need": 20, "distance": 6, "cost": 5, "risk": 15},
	&"snow": {"name": "Snow", "stable": false, "iron": 2, "iron_need": 12, "diamond": 6, "diamond_need": 8, "coin": 5, "coin_need": 20, "distance": 9, "cost": 8, "risk": 25},
	&"forest": {"name": "Forest", "stable": false, "iron": 5, "iron_need": 10, "diamond": 1, "diamond_need": 6, "coin": 9, "coin_need": 18, "distance": 7, "cost": 6, "risk": 18},
	&"desert": {"name": "Desert", "stable": false, "iron": 7, "iron_need": 14, "diamond": 4, "diamond_need": 8, "coin": 11, "coin_need": 22, "distance": 5, "cost": 4, "risk": 12},
	&"depot": {"name": "Depot", "stable": false, "iron": 0, "iron_need": 0, "diamond": 0, "diamond_need": 0, "coin": 0, "coin_need": 0, "distance": 0, "cost": 0, "risk": 0},
}

const CARAVAN := {"iron": 12, "diamond": 4, "coin": 18, "capacity": 30}
const LINE_COLOR := Color(1, 1, 1, 0.22)
const LINE_ACTIVE_COLOR := Color(1, 0.82, 0.35, 0.95)
const LINE_WIDTH := 6.0
const LINE_ACTIVE_WIDTH := 10.0

@export var current_area_id: StringName = &"depot"

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

var _selected_id: StringName = &""


func _ready() -> void:
	for id in _regions:
		var region: Control = _regions[id]
		region.region_hovered.connect(_on_region_hovered)
		region.region_unhovered.connect(_on_region_unhovered)
		region.region_selected.connect(_on_region_selected)
	%ConfirmDestinationButton.pressed.connect(_on_confirm_pressed)
	%ConfirmDestinationButton.hide()
	refresh(current_area_id, 1, 10)


func refresh(area_id: StringName, current_turn: int, turns_left: int) -> void:
	current_area_id = area_id
	_selected_id = &""
	for id in _regions:
		_regions[id].selected = false
	%TurnLabel.text = "Turn %d" % current_turn
	%TurnsLeftLabel.text = "%d turn tersisa" % turns_left
	_update_caravan_summary()
	_update_marker()
	_update_lines()
	_set_detail(current_area_id)


func _on_region_hovered(region: Control) -> void:
	_set_detail(region.area_id)
	_set_line_active(region.area_id, true)


func _on_region_unhovered(region: Control) -> void:
	_set_detail(_selected_id if _selected_id != &"" else current_area_id)
	_set_line_active(region.area_id, region.area_id == _selected_id)


func _on_region_selected(region: Control) -> void:
	_selected_id = region.area_id
	for id in _regions:
		_regions[id].selected = id == _selected_id
	_set_detail(_selected_id)
	_update_lines()
	_on_confirm_pressed()


func _set_detail(id: StringName) -> void:
	var data: Dictionary = AREA_DATA[id]
	%AreaNameLabel.text = data.name
	%StableBadge.text = "STABIL" if data.stable else "BELUM STABIL"
	%StableBadge.modulate = Color(0.55, 0.9, 0.55) if data.stable else Color(0.95, 0.65, 0.45)
	%IronValue.text = "%d / %d" % [data.iron, data.iron_need]
	%DiamondValue.text = "%d / %d" % [data.diamond, data.diamond_need]
	%CoinValue.text = "%d / %d" % [data.coin, data.coin_need]
	if id == &"depot":
		%IronValue.text = "-"
		%DiamondValue.text = "-"
		%CoinValue.text = "-"
		%DistanceRow.text = "Depot: isi resource, upgrade, skin"
		%CostRow.text = "Biaya perjalanan: -"
		%RiskRow.text = "Risiko bandit: -"
	else:
		%DistanceRow.text = "Jarak: %d" % data.distance
		%CostRow.text = "Biaya perjalanan: %d coin" % data.cost
		%RiskRow.text = "Risiko bandit: %d%%" % data.risk
	%ReasonLabel.text = _blocked_reason(id)
	_update_confirm_state()


func _blocked_reason(id: StringName) -> String:
	if id == &"":
		return "Pilih wilayah tujuan dulu."
	if id == current_area_id:
		return "Karavan sudah berada di sini."
	if CARAVAN.coin < AREA_DATA[id].cost:
		return "Coin karavan tidak cukup untuk biaya perjalanan."
	return ""


func _update_confirm_state() -> void:
	%ConfirmDestinationButton.disabled = _blocked_reason(_selected_id) != ""


func _update_caravan_summary() -> void:
	%CaravanIron.text = str(CARAVAN.iron)
	%CaravanDiamond.text = str(CARAVAN.diamond)
	%CaravanCoin.text = str(CARAVAN.coin)
	%CaravanCapacity.max_value = CARAVAN.capacity
	%CaravanCapacity.value = CARAVAN.coin
	%CaravanCapacityValue.text = "%d / %d" % [CARAVAN.coin, CARAVAN.capacity]
	%CaravanEffect.text = "Tanpa efek aktif"


func _update_marker() -> void:
	var anchor: Marker2D = _regions[current_area_id].get_node("Anchor")
	_marker.position = anchor.position - _marker.pivot_offset


func _update_lines() -> void:
	var from: Vector2 = _regions[current_area_id].get_node("Anchor").position
	for id in _lines:
		var line: Line2D = _lines[id]
		line.visible = id != current_area_id
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
	if _blocked_reason(_selected_id) != "":
		return
	# shortcut: sampai TravelController ada, konfirmasi hanya di-emit.
	destination_confirmed.emit(_selected_id)
	print("Tujuan dikonfirmasi: ", AREA_DATA[_selected_id].name)
