extends VBoxContainer

## Preview + pembelian gerobak/aksesoris. Dipakai HUD (Depot) dan main menu.

@export var in_game := false

@onready var _preview = %CaravanPreview
@onready var _preview_label: Label = %PreviewLabel
@onready var _stats_info: Label = %StatsInfo
@onready var _cart_name: Label = %CartName
@onready var _cart_effect: Label = %CartEffect
@onready var _cart_button: Button = %CartUpgradeButton
@onready var _forge_hint: Label = %ForgeHint

@onready var _rows: Dictionary = {
	"capacity": {
		"status": $Content/InfoColumn/AccessoryCapacity/Status,
		"button": $Content/InfoColumn/AccessoryCapacity/Buy,
	},
	"chest": {
		"status": $Content/InfoColumn/AccessoryChest/Status,
		"button": $Content/InfoColumn/AccessoryChest/Buy,
	},
	"tools": {
		"status": $Content/InfoColumn/AccessoryTools/Status,
		"button": $Content/InfoColumn/AccessoryTools/Buy,
	},
	"lantern": {
		"status": $Content/InfoColumn/AccessoryLantern/Status,
		"button": $Content/InfoColumn/AccessoryLantern/Buy,
	},
	"sack": {
		"status": $Content/InfoColumn/AccessorySack/Status,
		"button": $Content/InfoColumn/AccessorySack/Buy,
	},
}


func _ready() -> void:
	_cart_button.pressed.connect(_on_buy_cart)
	for accessory_id in GameData.ACCESSORY_ORDER:
		var id := String(accessory_id)
		var button: Button = _rows[id]["button"] as Button
		button.pressed.connect(_on_buy_accessory.bind(id))
	RunState.changed.connect(refresh)
	refresh()


func open() -> void:
	refresh()


func refresh() -> void:
	if not is_node_ready():
		return
	var cart := RunState.cart_level
	var speed_percent := int(round(RunState.speed_bonus() * 100.0))
	_preview.call("show_customization", cart, RunState.accessories)
	_preview_label.text = "Level %d - %s" % [cart, RunState.cart_name()]
	_stats_info.text = "Kapasitas %d - Speed +%d%% - Koin menu %d" % [RunState.capacity(), speed_percent, RunState.menu_coins]
	_cart_name.text = "Gerobak Level %d/%d" % [cart, GameData.MAX_CART_LEVEL]

	if cart >= GameData.MAX_CART_LEVEL:
		_cart_effect.text = "Sudah level maksimal"
		_cart_button.text = "MAX LEVEL"
		_cart_button.disabled = true
	else:
		var next_data := GameData.cart_data(cart + 1)
		_cart_effect.text = "Upgrade: +%d kapasitas, +%d%% speed" % [
			int(next_data["capacity"]), int(round(float(next_data["speed"]) * 100.0))
		]
		_cart_button.text = "UPGRADE %d" % GameData.CART_UPGRADE_COST
		_cart_button.disabled = RunState.menu_coins < GameData.CART_UPGRADE_COST or _blocked_in_game()

	for accessory_id in GameData.ACCESSORY_ORDER:
		var id := String(accessory_id)
		var owned := RunState.is_accessory_owned(id)
		var data: Dictionary = GameData.ACCESSORIES[id]
		var status: Label = _rows[id]["status"] as Label
		var button: Button = _rows[id]["button"] as Button
		status.text = "TERPASANG" if owned else "TERKUNCI"
		status.modulate = Color(0.68, 0.88, 0.58) if owned else Color(0.8, 0.7, 0.55)
		button.visible = not owned
		if not owned:
			button.text = "BELI %d" % int(data["cost"])
			button.disabled = RunState.menu_coins < int(data["cost"]) or _blocked_in_game()

	if _blocked_in_game():
		_forge_hint.text = "Upgrade hanya di Depot atau main menu. Di wilayah lain Forge hanya preview."
	elif RunState.menu_coins < GameData.CART_UPGRADE_COST and not _all_maxed():
		_forge_hint.text = "Koin menu tidak cukup untuk sebagian upgrade."
	else:
		_forge_hint.text = "Pembelian permanen; preview berubah langsung."


func _blocked_in_game() -> bool:
	return in_game and not RunState.is_at_depot()


func _all_maxed() -> bool:
	if RunState.cart_level < GameData.MAX_CART_LEVEL:
		return false
	for accessory_id in GameData.ACCESSORY_ORDER:
		if not RunState.is_accessory_owned(String(accessory_id)):
			return false
	return true


func _on_buy_cart() -> void:
	RunState.buy_cart_upgrade()


func _on_buy_accessory(accessory_id: String) -> void:
	RunState.buy_accessory(accessory_id)
