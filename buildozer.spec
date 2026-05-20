[app]
title = Zavod Nichego
package.name = zavodnichego
package.domain = org.example
source.dir = .
source.include_exts = py,ttf
source.include_patterns = fonts/PressStart2P-Regular.ttf
source.exclude_patterns = .buildozer,bin,save.json,notebooklm_source.md,*.md,*.bat,*.ps1
version = 1.0
requirements = python3,pygame
orientation = portrait
fullscreen = 1

android.permissions =
android.archs = arm64-v8a
android.minapi = 21
android.sdk = 33
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
