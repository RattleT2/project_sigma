extends Control

signal map_requested
signal close_requested

@onready var _summary: Label = $JournalSummary
@onready var _text: RichTextLabel = $JournalText
@onready var _map_button: Button = $JournalMapButton
@onready var _close_button: TextureButton = $JournalClose


func _ready() -> void:
	_map_button.pressed.connect(func(): map_requested.emit())
	_close_button.pressed.connect(func(): close_requested.emit())


func set_content(summary: String, body: String) -> void:
	_summary.text = summary
	_text.text = body
