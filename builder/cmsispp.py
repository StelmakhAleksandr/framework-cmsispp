Import("env")
import os
import shutil

home_dir = os.path.expanduser("~")
pio_packages_dir = os.path.join(home_dir, ".platformio", "packages")
framework_path = os.path.join(pio_packages_dir, "framework-cmsispp")

if not framework_path:
    env.Exit("❌ Error: framework-cmsispp не знайдено!")

print(f"✅ Використовується CMSIS++: {framework_path}")

# === 🟢 Автоматичний вибір LD-скрипта ===
def get_ld_script():
    mcu = env.BoardConfig().get("build.mcu", "").upper()
    ld_dir = os.path.join(framework_path, "cmsis", "Device", "ST", "STM32F4xx")
    ld_files = [f for f in os.listdir(ld_dir) if f.startswith(mcu) and f.endswith(".ld")]

    if not ld_files:
        env.Exit(f"❌ Error: Не знайдено LD-скрипт для {mcu} в {ld_dir}")

    return os.path.join(ld_dir, ld_files[0])

env.Replace(LDSCRIPT_PATH=get_ld_script())

# === 🟢 Додаємо потрібні шляхи ===
env.Append(
    CPPPATH=[
        os.path.join(framework_path, "include"),
        os.path.join(framework_path, "src"),
        os.path.join(framework_path, "cmsis", "Core"),
        os.path.join(framework_path, "cmsis", "Device", "ST", "STM32F4xx"),
    ],
    LIBPATH=[
        os.path.join(framework_path, "libs"),  # Якщо є кастомні бібліотеки
    ],
    LIBS=["c", "m", "gcc"]
)

# === 🟢 Генерація `cmsispp_conf.h`, якщо його немає ===
def generate_cmsispp_conf():
    config_path = os.path.join(framework_path, "include")
    conf_h_path = os.path.join(config_path, "cmsispp_conf.h")
    template_h_path = os.path.join(config_path, "cmsispp_conf_template.h")

    if os.path.isfile(conf_h_path):
        return  # Файл вже є

    if not os.path.isfile(template_h_path):
        env.Exit("❌ Error: Не знайдено шаблон конфігурації CMSIS++!")

    shutil.copy(template_h_path, conf_h_path)
    print(f"✅ Згенеровано cmsispp_conf.h: {conf_h_path}")

generate_cmsispp_conf()

# === 🟢 Додаємо `startup_xxx.S` у білд ===
def add_startup_file():
    mcu_family = "STM32F4xx"
    startup_file = os.path.join(framework_path, "cmsis", "Device", "ST", mcu_family, "startup_stm32f407xx.s")

    if os.path.isfile(startup_file):
        env.Append(
            SRC_FILTER=[
                "+<cmsis/Device/ST/STM32F4xx/startup_stm32f407xx.s>"
            ]
        )
    else:
        env.Exit(f"❌ Error: Не знайдено startup-файл {startup_file}")

add_startup_file()

# === 🟢 Додаємо всі `.c` та `.cpp` файли у `src/` ===
src_dirs = [
    os.path.join(framework_path, "src"),
    os.path.join(framework_path, "cmsis", "Device", "ST", "STM32F4xx")
]

sources = []
for src_dir in src_dirs:
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith((".c", ".cpp")):
                sources.append(os.path.join(root, file))

env.Append(
    SRC_FILTER=[
        "+<src/>",
        "+<cmsis/Device/ST/STM32F4xx/>"
    ],
    LIBS=sources
)

print("✅ CMSIS++ з CMSIS успішно додано до збірки")