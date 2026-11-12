# Horse Caravan UI – potongan PNG

Semua file PNG transparan, skala HD 2x (sama dengan gambar asli 5152x2876).
Di Godot, set Texture Filter = Nearest (Project Settings → Rendering → Textures → Default Texture Filter) supaya pixel art tetap tajam.

## Folder
- topbar/          topbar_full, topbar_left, topbar_center (+ ornamen koin), topbar_right
- menu/            title_sign, menu_frame (rangka kosong), btn_play / btn_settings / btn_quit (+ _sheet)
- buttons_square/  nav_buttons_group (4 tombol kotak utuh), nav_shop / nav_map / nav_forge / nav_journal (+ _sheet)
- icons/           icon_coin, icon_coin_small, icon_gem, icon_iron_ingot, btn_plus_gold, btn_plus_brown
- misc/            progress_track, panel_plate, coin_big

## Sprite frame tombol
Tiap tombol punya 3 frame dengan ukuran kanvas sama:
  0 = normal, 1 = hover (lebih terang), 2 = pressed (lebih gelap + turun 8 px)

- `<nama>_sheet.png`      : strip horizontal 3 frame (1 baris x 3 kolom)
- `frames/<nama>_*.png`   : frame terpisah (normal / hover / pressed)

Pakai di Godot:
1. TextureButton → isi Texture Normal / Hover / Pressed dari folder frames/.
2. Atau AnimatedSprite2D → SpriteFrames → "Add frames from Sprite Sheet" → Horizontal 3, Vertical 1.
