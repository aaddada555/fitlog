[app]

title = 健身日志
package.name = fitlog
package.domain = org.fitlog

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt

version = 0.1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

p4a.branch = master
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
