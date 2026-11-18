class_name NPCData
extends Resource
## Data profil NPC. Buat resource baru via File > New Resource > NPCData,
## isi field di Inspector, lalu assign ke field "npc_data" pada npc_controller.
## NPCData bersifat opsional; controller tetap jalan tanpa resource ini.

@export var npc_name: String = ""
@export var profession_id: String = ""
@export var skill_description: String = ""

@export_group("Caravan Buffs")
@export var speed_bonus: float = 0.0
@export var trade_discount: float = 0.0
@export var stamina_regen_bonus: float = 0.0
@export var repair_bonus: float = 0.0

@export_group("Animation Names")
@export var work_animation: String = "work"
