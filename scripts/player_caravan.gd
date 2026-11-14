extends CharacterBody2D

enum State { IDLE, WALK, BOOST, STOPPING }

const HORSE_PREFIX := "horse_level1_"
const WHEEL_PREFIX := "wheel_level1_"
const COSTUME_PREFIX := "tent_costume4_level_1"

@export var input_enabled := true
@export var walk_speed := 90.0
@export var boost_speed := 220.0
@export var acceleration := 400.0
@export var deceleration := 700.0
@export var snort_delay_min := 4.0
@export var snort_delay_max := 9.0

@export_group("Lantern")
@export var lantern_flicker_enabled := true
@export var lantern_flicker_speed := 1.0
@export var lantern_flicker_strength := 2

@onready var driver: AnimatedSprite2D = $Driver
@onready var costume: AnimatedSprite2D = $Cariagetentcostume
@onready var wagon: AnimatedSprite2D = $Cariagetentcostume/Wagon
@onready var horse: AnimatedSprite2D = $Cariagetentcostume/Horse
@onready var harness: AnimatedSprite2D = $Cariagetentcostume/Horse/Harness
@onready var wheel_front: AnimatedSprite2D = $Cariagetentcostume/Wagon/wheel_front
@onready var wheel_back: AnimatedSprite2D = $Cariagetentcostume/Wagon/wheel_back
@onready var dust_particles: Array[GPUParticles2D] = [
	$Cariagetentcostume/Wagon/wheelparticlefront,
	$Cariagetentcostume/Wagon/wheelparticleback,
	$Cariagetentcostume/Horse/horsewalkparticleback,
	$Cariagetentcostume/Horse/horsewalkparticlefront,
]
@onready var snort_particle: GPUParticles2D = $Cariagetentcostume/Horse/horsesnortparticle_sync_with_sound
@onready var move_sound: AudioStreamPlayer2D = $sound_horse_and_wagon_run_and_boost
@onready var snort_sound: AudioStreamPlayer2D = $sound_horse_snort_random_when_idle
@onready var snort_timer: Timer = $SnortTimer
@onready var lantern_light: PointLight2D = $Cariagetentcostume/Wagon/lantern_light
@onready var lantern_accessory: AnimatedSprite2D = $Cariagetentcostume/Wagon/accessory_lantern_buff_speed_for_wagon2

var state: State = State.IDLE
var _move_requested := false
var _boost_requested := false
var _input_right_held := false
var _accessory_sprites: Array[AnimatedSprite2D] = []
var _accessory_bases: Array[String] = []
var _lantern_base_energy := 0.0
var _lantern_time := 0.0
var _lantern_noise := FastNoiseLite.new()


func _ready() -> void:
	_collect_accessories()
	_setup_move_sound()
	snort_timer.one_shot = true
	snort_timer.timeout.connect(_on_snort_timer_timeout)
	horse.animation_finished.connect(_on_horse_animation_finished)
	_apply_state_animations()
	_schedule_next_snort()
	_lantern_base_energy = lantern_light.energy
	_lantern_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	_lantern_noise.frequency = 1.0
	_lantern_noise.fractal_octaves = 2
	_lantern_noise.seed = randi()


func _process(delta: float) -> void:
	_update_lantern(delta)


func _update_lantern(delta: float) -> void:
	lantern_light.visible = lantern_accessory.visible
	if not lantern_flicker_enabled or not lantern_light.visible:
		lantern_light.energy = _lantern_base_energy
		return
	_lantern_time += delta * lantern_flicker_speed
	var flicker := _lantern_noise.get_noise_1d(_lantern_time)
	lantern_light.energy = maxf(0.0, _lantern_base_energy + flicker * lantern_flicker_strength)


func _physics_process(delta: float) -> void:
	_update_test_input()
	_update_movement(delta)
	velocity.y = 0.0
	move_and_slide()


func start_move(boost := false) -> void:
	_move_requested = true
	_boost_requested = boost


func stop_move() -> void:
	_move_requested = false
	_boost_requested = false


func set_boost(enabled: bool) -> void:
	_boost_requested = enabled


func _update_test_input() -> void:
	if not input_enabled:
		return
	if Input.is_physical_key_pressed(KEY_RIGHT):
		_move_requested = true
		_boost_requested = Input.is_physical_key_pressed(KEY_SPACE)
		_input_right_held = true
	elif _input_right_held:
		_move_requested = false
		_boost_requested = false
		_input_right_held = false


func _update_movement(delta: float) -> void:
	if _move_requested:
		var target_speed := boost_speed if _boost_requested else walk_speed
		velocity.x = move_toward(velocity.x, target_speed, acceleration * delta)
		_set_state(State.BOOST if _boost_requested else State.WALK)
	else:
		if state == State.WALK or state == State.BOOST:
			_set_state(State.STOPPING)
		velocity.x = move_toward(velocity.x, 0.0, deceleration * delta)


func _set_state(new_state: State) -> void:
	if state == new_state:
		return
	state = new_state
	_apply_state_animations()
	_update_move_sound()
	if state == State.IDLE:
		_schedule_next_snort()


func _apply_state_animations() -> void:
	match state:
		State.IDLE:
			_play(driver, "driver2_idle")
			_play(costume, COSTUME_PREFIX + "_idle")
			_play(wagon, "wagon_idle")
			_play(horse, HORSE_PREFIX + "idle")
			_play(harness, "harnes_idle")
			_play(wheel_front, WHEEL_PREFIX + "idle")
			_play(wheel_back, WHEEL_PREFIX + "idle")
			horse.speed_scale = 0.6
			harness.speed_scale = 0.6
			_play_accessories("_idle")
			_set_dust(false)
		State.WALK:
			_play(driver, "driver2_run")
			_play(costume, COSTUME_PREFIX + "_run")
			_play(wagon, "wagon_run")
			_play(horse, HORSE_PREFIX + "run")
			_play(harness, "harness_walk")
			_play(wheel_front, WHEEL_PREFIX + "rotate_walk")
			_play(wheel_back, WHEEL_PREFIX + "rotate_walk")
			horse.speed_scale = 1.0
			harness.speed_scale = 1.0
			_play_accessories("_run")
			_set_dust(true)
		State.BOOST:
			_play(driver, "driver2_giving_boost")
			_play(costume, COSTUME_PREFIX + "run_boost")
			_play(wagon, "wagon_run_boost")
			_play(horse, HORSE_PREFIX + "run_boost")
			_play(harness, "harness_run_boost")
			_play(wheel_front, WHEEL_PREFIX + "rotate_boost")
			_play(wheel_back, WHEEL_PREFIX + "rotate_boost")
			horse.speed_scale = 1.0
			harness.speed_scale = 1.0
			_play_accessories("_run_boost")
			_set_dust(true)
		State.STOPPING:
			_play(driver, "driver2_idle")
			_play(costume, COSTUME_PREFIX + "_idle")
			_play(wagon, "wagon_idle")
			_play(horse, HORSE_PREFIX + "stop")
			_play(harness, "harness_stop")
			_play(wheel_front, WHEEL_PREFIX + "idle")
			_play(wheel_back, WHEEL_PREFIX + "idle")
			horse.speed_scale = 1.0
			harness.speed_scale = 1.0
			_play_accessories("_idle")
			_set_dust(false)


func _play(sprite: AnimatedSprite2D, animation_name: String) -> void:
	if sprite.animation == animation_name and sprite.is_playing():
		return
	if not sprite.sprite_frames.has_animation(animation_name):
		push_warning("Animasi tidak ditemukan: %s pada %s" % [animation_name, sprite.name])
		return
	sprite.play(animation_name)


func _play_accessories(suffix: String) -> void:
	for i in _accessory_sprites.size():
		_play(_accessory_sprites[i], _accessory_bases[i] + suffix)


func _collect_accessories() -> void:
	for child in wagon.get_children():
		if child is AnimatedSprite2D and child.animation.begins_with("accessory_"):
			_accessory_sprites.append(child)
			var base: String = child.animation
			base = base.trim_suffix("_run_boost").trim_suffix("_run").trim_suffix("_idle")
			_accessory_bases.append(base)


func _setup_move_sound() -> void:
	move_sound.finished.connect(_on_move_sound_finished)


func _on_move_sound_finished() -> void:
	if state == State.WALK or state == State.BOOST:
		move_sound.play()


func _update_move_sound() -> void:
	if state == State.WALK or state == State.BOOST:
		move_sound.pitch_scale = 1.2 if state == State.BOOST else 1.0
		if not move_sound.playing:
			move_sound.play()
	elif move_sound.playing:
		move_sound.stop()


func _set_dust(enabled: bool) -> void:
	for particle in dust_particles:
		particle.emitting = enabled


func _schedule_next_snort() -> void:
	snort_timer.start(randf_range(snort_delay_min, snort_delay_max))


func _on_snort_timer_timeout() -> void:
	if state != State.IDLE:
		snort_timer.start(2.0)
		return
	snort_sound.pitch_scale = randf_range(0.95, 1.1)
	snort_sound.play()
	snort_particle.restart()
	_schedule_next_snort()


func _on_horse_animation_finished() -> void:
	if state == State.STOPPING:
		_set_state(State.IDLE)
