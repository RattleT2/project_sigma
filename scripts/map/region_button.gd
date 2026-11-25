extends Control

signal region_hovered(region)
signal region_unhovered(region)
signal region_selected(region)

@export var area_id: StringName = &""
@export var display_name: String = ""
@export var hover_color := Color(1, 0.95, 0.65, 0.28)
@export var selected_color := Color(1, 0.9, 0.5, 0.42)
@export var outline_color := Color(1, 0.68, 0.12, 1)
@export var outline_width := 16.0

var selected := false:
	set(value):
		selected = value
		_update_visual()

var _hovered := false

@onready var _highlight: Polygon2D = $Highlight
@onready var _outline: Line2D = $Outline


func _ready() -> void:
	var points := _highlight.polygon
	if points.size() > 0:
		points.append(points[0])
	_outline.points = points
	_outline.width = outline_width
	mouse_entered.connect(_on_mouse_entered)
	mouse_exited.connect(_on_mouse_exited)
	_update_visual()


# Hanya bagian dalam poligon wilayah yang menerima hover/klik.
func _has_point(point: Vector2) -> bool:
	return _highlight.polygon.size() > 2 and Geometry2D.is_point_in_polygon(point, _highlight.polygon)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		region_selected.emit(self)
		accept_event()


func _on_mouse_entered() -> void:
	_hovered = true
	_update_visual()
	region_hovered.emit(self)


func _on_mouse_exited() -> void:
	_hovered = false
	_update_visual()
	region_unhovered.emit(self)


func _update_visual() -> void:
	if not is_node_ready():
		return
	_highlight.visible = selected or _hovered
	_highlight.color = selected_color if selected else hover_color
	_outline.visible = selected or _hovered
	_outline.default_color = outline_color
