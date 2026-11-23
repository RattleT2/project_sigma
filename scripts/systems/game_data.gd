class_name GameData
extends RefCounted

## Data statis untuk loop permainan. Semua id memakai String agar aman untuk JSON.

const START_COINS := 500
const MAX_ROUND := 10

const RESOURCES := {
	"iron": {"name": "Iron", "short": "Iron", "buy": 15, "sell": 18,
		"icon": "res://asset/horse_caravan_ui_parts/icons/icon_iron_ingot.png"},
	"gold": {"name": "Koin Emas", "short": "Emas", "buy": 10, "sell": 12,
		"icon": "res://asset/horse_caravan_ui_parts/icons/icon_coin.png"},
	"diamond": {"name": "Diamond", "short": "Diamond", "buy": 30, "sell": 36,
		"icon": "res://asset/horse_caravan_ui_parts/icons/icon_gem.png"},
}

const REGION_ORDER := ["snow", "forest", "desert", "village"]

const REGIONS := {
	"snow": {"name": "Salju", "risk": 25.0, "drive": 1050.0,
		"needs": {"iron": 6, "gold": 6, "diamond": 16}},
	"forest": {"name": "Forest", "risk": 18.0, "drive": 900.0,
		"needs": {"iron": 6, "gold": 16, "diamond": 6}},
	"desert": {"name": "Desert", "risk": 12.0, "drive": 600.0,
		"needs": {"iron": 16, "gold": 6, "diamond": 6}},
	"village": {"name": "Village", "risk": 15.0, "drive": 750.0,
		"needs": {"iron": 10, "gold": 10, "diamond": 10}},
}

const BUFFS := {
	"guard": {"name": "Penjaga", "cost": 80, "turns": 2,
		"desc": "Bandit tidak bisa mencuri."},
	"speed": {"name": "Cepat", "cost": 60, "turns": 2,
		"desc": "Waktu travel -30%."},
	"bargain": {"name": "Tawar", "cost": 70, "turns": 2,
		"desc": "Harga resupply -20%."},
}

const BASE_CAPACITY := 30
const BASE_DRIVE_SPEED := 90.0
const MAX_CART_LEVEL := 2
const CART_UPGRADE_COST := 500

const CART_LEVELS := {
	1: {"name": "Gerobak Dasar", "body": 1, "capacity": 0, "speed": 0.0},
	2: {"name": "Gerobak Ekspedisi", "body": 2, "capacity": 6, "speed": 0.05},
}

const ACCESSORY_ORDER := ["capacity", "chest", "tools", "lantern", "sack"]

const ACCESSORIES := {
	"capacity": {"name": "Rak Kargo", "cost": 150, "capacity": 2, "speed": 0.0,
		"desc": "+2 kapasitas"},
	"chest": {"name": "Peti Kargo", "cost": 200, "capacity": 2, "speed": 0.0,
		"desc": "+2 kapasitas"},
	"tools": {"name": "Perkakas", "cost": 250, "capacity": 0, "speed": 0.05,
		"desc": "+5% speed"},
	"lantern": {"name": "Lentera", "cost": 300, "capacity": 0, "speed": 0.05,
		"desc": "+5% speed"},
	"sack": {"name": "Karung", "cost": 250, "capacity": 2, "speed": 0.0,
		"desc": "+2 kapasitas"},
}


static func region_name(region_id: String) -> String:
	return String(REGIONS[region_id]["name"])


static func resource_name(resource_id: String) -> String:
	return String(RESOURCES[resource_id]["name"])


static func resource_short(resource_id: String) -> String:
	return String(RESOURCES[resource_id]["short"])


static func buy_price(resource_id: String) -> int:
	return int(RESOURCES[resource_id]["buy"])


static func sell_price(resource_id: String) -> int:
	return int(RESOURCES[resource_id]["sell"])


static func round_demand_multiplier(round_number: int) -> float:
	return 1.0 + 0.5 * float(mini(round_number, MAX_ROUND) - 1)


static func need_for(region_id: String, round_number: int, resource_id: String) -> int:
	var base := int(REGIONS[region_id]["needs"][resource_id])
	return int(ceil(float(base) * round_demand_multiplier(round_number)))


static func turns_for_round(round_number: int) -> int:
	return 5 + mini(round_number, MAX_ROUND) - 1


static func target_regions(round_number: int) -> int:
	return mini(round_number, 4)


static func drive_distance(region_id: String) -> float:
	return float(REGIONS[region_id]["drive"])


static func bandit_risk(region_id: String) -> float:
	return float(REGIONS[region_id]["risk"])


static func cart_data(level: int) -> Dictionary:
	return CART_LEVELS[clampi(level, 1, MAX_CART_LEVEL)]


static func cart_name(level: int) -> String:
	return String(cart_data(level)["name"])


static func cart_body(level: int) -> int:
	return int(cart_data(level)["body"])


static func accessory_data(accessory_id: String) -> Dictionary:
	return ACCESSORIES[accessory_id]


static func accessory_name(accessory_id: String) -> String:
	if not ACCESSORIES.has(accessory_id):
		return accessory_id
	return String(ACCESSORIES[accessory_id]["name"])
