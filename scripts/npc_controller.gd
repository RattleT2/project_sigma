extends CharacterBody2D
## Tempel ke root CharacterBody2D scene npc_*.tscn.
## Assign target_prop (WorkProp_NPC_*) di Inspector, atau isi target_prop_path (NodePath) dari scene hub.
## Player dideteksi lewat group "player_caravan" atau nama node "Player_Caravan".
## Scene NPC perlu punya node InteractionArea (Area2D) + CollisionShape2D.
## Layer yang diasumsikan: 1 = tanah/player, 3 = NPC (collision_layer = 4).

enum State { IDLE, PATROL, WALK_TO_PROP, WORKING, GREET_CARAVAN }

const IDLE_ANIMS: Array[String] = ["idle", "diam"]
const WALK_ANIMS: Array[String] = ["walk", "jalan"]
const RUN_ANIMS: Array[String] = ["run", "lari"]
const TALK_ANIMS: Array[String] = ["talk", "talking", "ngobrol"]
const WAVE_ANIMS: Array[String] = ["wave", "waving", "melambai"]

# shortcut: auto-deteksi animasi kerja dari nama animasi; upgrade: isi NPCData.work_animation.
const WORK_KEYWORDS := [
	"cutting", "chop", "menebang",
	"forge", "menempa",
	"kneading", "menguleni",
	"hoe", "cangkul",
	"planting", "tanam",
	"broom", "menyapu",
	"carry", "caryy", "bawa",
	"cook", "masak",
	"fortune", "ramal",
	"tearing", "repair",
	"work", "kerja",
]

const ARRIVE_DISTANCE := 2.0

@export var npc_data: NPCData
@export var target_prop: Node2D
@export var target_prop_path: NodePath
@export var walk_speed := 35.0
@export var patrol_range := 60.0
@export var sprite_faces_right_by_default := true
@export var idle_duration_min := 2.0
@export var idle_duration_max := 5.0
@export var work_duration := 5.0
@export_range(0.0, 1.0) var work_chance := 0.5
@export var apply_gravity := true

var state: State = State.IDLE

var _sprite: AnimatedSprite2D
var _label: Label
var _audio: AudioStreamPlayer2D
var _state_timer: Timer
var _interaction_area: Area2D
var _start_x := 0.0
var _target_x := 0.0
var _work_time_left := 0.0
var _work_animation := ""
var _player_exception_added := false
var _greet_player: Node2D


func _ready() -> void:
	_start_x = global_position.x
	if not apply_gravity:
		floor_snap_length = 0.0
	_sprite = _find_sprite()
	_label = get_node_or_null("Label") as Label
	_audio = _find_audio()
	_state_timer = _find_state_timer()
	_interaction_area = find_child("InteractionArea", true, false) as Area2D
	if target_prop == null and not target_prop_path.is_empty():
		target_prop = get_node_or_null(target_prop_path) as Node2D
	_work_animation = _resolve_work_animation()
	_setup_label()
	_setup_timer()
	_setup_interaction_area()
	_enter_idle()


func _physics_process(delta: float) -> void:
	_ensure_player_exception()
	if not apply_gravity:
		_update_anchored(delta)
		return
	velocity.y += get_gravity().y * delta

	match state:
		State.PATROL, State.WALK_TO_PROP:
			_move_toward_target()
		State.WORKING:
			velocity.x = 0.0
			_work_time_left -= delta
			if _work_time_left <= 0.0:
				_enter_idle()
		_:
			velocity.x = 0.0

	move_and_slide()


func _update_anchored(delta: float) -> void:
	velocity = Vector2.ZERO
	match state:
		State.PATROL, State.WALK_TO_PROP:
			var distance := _target_x - global_position.x
			if absf(distance) <= ARRIVE_DISTANCE:
				global_position.x = _target_x
				if state == State.WALK_TO_PROP:
					_enter_working()
				else:
					_enter_idle()
			else:
				global_position.x = move_toward(global_position.x, _target_x, walk_speed * delta)
				_face_x(_target_x)
		State.WORKING:
			_work_time_left -= delta
			if _work_time_left <= 0.0:
				_enter_idle()


func _find_sprite() -> AnimatedSprite2D:
	for child in get_children():
		if child is AnimatedSprite2D:
			return child
	return null


func _find_audio() -> AudioStreamPlayer2D:
	for child in get_children():
		if child is AudioStreamPlayer2D:
			return child
	return null


func _find_state_timer() -> Timer:
	var timer := get_node_or_null("Timer") as Timer
	if timer == null:
		timer = get_node_or_null("StateTimer") as Timer
	if timer == null:
		for child in get_children():
			if child is Timer:
				timer = child
				break
	return timer


func _setup_label() -> void:
	if _label == null:
		return
	_label.visible = false
	if _label.text.is_empty():
		_label.text = "!"
	if _label.position == Vector2.ZERO:
		_label.position = Vector2(-20, -60)
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER


func _setup_timer() -> void:
	if _state_timer == null:
		push_warning("NPC %s tidak punya Timer/StateTimer." % name)
		return
	_state_timer.one_shot = true
	_state_timer.timeout.connect(_on_state_timer_timeout)


func _setup_interaction_area() -> void:
	if _interaction_area == null:
		push_warning("NPC %s tidak punya InteractionArea." % name)
		return
	_interaction_area.body_entered.connect(_on_interaction_body_entered)
	_interaction_area.body_exited.connect(_on_interaction_body_exited)


func _enter_idle() -> void:
	state = State.IDLE
	velocity.x = 0.0
	_play_anim_safe(IDLE_ANIMS)
	if _state_timer != null and _state_timer.is_inside_tree():
		_state_timer.start(randf_range(idle_duration_min, idle_duration_max))


func _enter_patrol() -> void:
	state = State.PATROL
	_target_x = _start_x + randf_range(-patrol_range, patrol_range)
	_stop_timer()
	_play_anim_safe(WALK_ANIMS)


func _enter_walk_to_prop() -> void:
	if not _has_valid_prop():
		_enter_patrol()
		return
	var spot = target_prop.get_random_spot()
	if not (spot is Marker2D):
		_enter_patrol()
		return
	state = State.WALK_TO_PROP
	_target_x = (spot as Marker2D).global_position.x
	_stop_timer()
	_play_anim_safe(WALK_ANIMS)


func _enter_working() -> void:
	state = State.WORKING
	velocity.x = 0.0
	_work_time_left = work_duration
	if _has_valid_prop():
		_face_x(target_prop.global_position.x)
		if not _work_animation.is_empty() and target_prop.has_method("play_work_sound"):
			target_prop.play_work_sound()
	# shortcut: suara kerja diputar sekali di awal, bukan sinkron per hit frame.
	# Upgrade: sambungkan sprite.frame_changed + NPCData.work_hit_frame.
	var work_candidates: Array = IDLE_ANIMS
	if not _work_animation.is_empty():
		work_candidates = [_work_animation]
	_play_anim_safe(work_candidates)


func _move_toward_target() -> void:
	var distance := _target_x - global_position.x
	if absf(distance) <= ARRIVE_DISTANCE:
		global_position.x = _target_x
		velocity.x = 0.0
		if state == State.WALK_TO_PROP:
			_enter_working()
		else:
			_enter_idle()
		return
	velocity.x = signf(distance) * walk_speed
	_face_x(_target_x)


func _face_x(target_x: float) -> void:
	if _sprite == null:
		return
	var facing_right := target_x >= global_position.x
	_sprite.flip_h = not facing_right if sprite_faces_right_by_default else facing_right


func _play_anim_safe(candidates: Array) -> bool:
	if _sprite == null or _sprite.sprite_frames == null:
		return false
	for candidate in candidates:
		var anim_name := String(candidate)
		if _sprite.sprite_frames.has_animation(anim_name):
			_sprite.play(anim_name)
			return true
	for candidate in candidates:
		var needle := String(candidate).to_lower()
		for anim_name in _sprite.sprite_frames.get_animation_names():
			if String(anim_name).to_lower().contains(needle):
				_sprite.play(anim_name)
				return true
	return false


func _resolve_work_animation() -> String:
	if _sprite == null or _sprite.sprite_frames == null:
		return ""
	if npc_data != null and not npc_data.work_animation.is_empty():
		if _sprite.sprite_frames.has_animation(npc_data.work_animation):
			return npc_data.work_animation
	for keyword in WORK_KEYWORDS:
		for anim_name in _sprite.sprite_frames.get_animation_names():
			if String(anim_name).to_lower().contains(keyword):
				return String(anim_name)
	return ""


func _has_valid_prop() -> bool:
	return target_prop != null and is_instance_valid(target_prop) and target_prop.has_method("get_random_spot")


func _stop_timer() -> void:
	if _state_timer != null:
		_state_timer.stop()


func _on_state_timer_timeout() -> void:
	if state != State.IDLE:
		return
	if _has_valid_prop() and randf() < work_chance:
		_enter_walk_to_prop()
	else:
		_enter_patrol()


func _is_player(node: Node) -> bool:
	return node != null and (node.is_in_group("player_caravan") or node.name == &"Player_Caravan")


func _on_interaction_body_entered(body: Node2D) -> void:
	if not _is_player(body) or state == State.GREET_CARAVAN:
		return
	_greet_player = body
	_enter_greet()


func _on_interaction_body_exited(body: Node2D) -> void:
	if body != _greet_player:
		return
	_greet_player = null
	_hide_label()
	if is_inside_tree():
		_enter_idle()


func _enter_greet() -> void:
	state = State.GREET_CARAVAN
	velocity.x = 0.0
	_stop_timer()
	if _greet_player != null:
		_face_x(_greet_player.global_position.x)
	if not _play_anim_safe(WAVE_ANIMS):
		if not _play_anim_safe(TALK_ANIMS):
			_play_anim_safe(IDLE_ANIMS)
	_show_label()
	if _audio != null and _audio.stream != null:
		_audio.play()


func _show_label() -> void:
	if _label != null:
		_label.visible = true


func _hide_label() -> void:
	if _label != null:
		_label.visible = false


func _find_player() -> Node2D:
	var player := get_tree().get_first_node_in_group("player_caravan") as Node2D
	if player != null:
		return player
	var tree_root := get_tree().root
	if tree_root != null:
		return tree_root.find_child("Player_Caravan", true, false) as Node2D
	return null


func _ensure_player_exception() -> void:
	if _player_exception_added:
		return
	var player := _find_player()
	if player is PhysicsBody2D:
		add_collision_exception_with(player)
		_player_exception_added = true
