import json
import math

WIDTH = 256
HEIGHT = 256
SEED = 1337

def _hash(ix, iy, seed):
    n = (ix * 374761393 + iy * 668265263 + seed * 1442695040888963407) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0x7FFFFFFF) / 0x7FFFFFFF

def _smooth(t):
    return t * t * (3.0 - 2.0 * t)

def _lerp(a, b, t):
    return a + (b - a) * t

def _value_noise(x, y, scale, seed):
    gx, gy = x / scale, y / scale
    ix, iy = int(math.floor(gx)), int(math.floor(gy))
    fx, fy = gx - ix, gy - iy
    v00 = _hash(ix, iy, seed)
    v10 = _hash(ix + 1, iy, seed)
    v01 = _hash(ix, iy + 1, seed)
    v11 = _hash(ix + 1, iy + 1, seed)
    sx, sy = _smooth(fx), _smooth(fy)
    return _lerp(_lerp(v00, v10, sx), _lerp(v01, v11, sx), sy)

def fbm(x, y, seed=0, octaves=4, base_scale=40.0):
    value, amp, freq, total = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        value += _value_noise(x, y, base_scale / freq, seed + o) * amp
        total += amp
        amp *= 0.5
        freq *= 2.0
    return value / total

def generate_relief():
    world = []
    
    cx, cy = WIDTH / 2.0, HEIGHT / 2.0
    max_r = math.sqrt(cx * cx + cy * cy)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            
            # 1. ГЕНЕРАЦИЯ ОСТРОГО РЕЛЬЕФА
            # Вытягиваем скалы по диагонали (x и y с разными коэффициентами)
            noise_x = x * 0.7
            noise_y = y * 1.3
            
            # Берем шум и возводим в степень, чтобы сделать пики острыми
            base_noise = fbm(noise_x, noise_y, seed=SEED, octaves=4, base_scale=25.0)
            
            # Радиальный градиент для краев карты
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy) / max_r
            
            # Формула высоты: добавляем градиент и возводим в квадрат для остроты
            height_val = (base_noise * 0.8 + dist * 0.4)
            
            # 2. ОПРЕДЕЛЕНИЕ БЛОКА
            # Порог 0.55. Всё, что выше — скала. Всё, что ниже — песок.
            if height_val > 0.55:
                # Скалы. Используем только песчаные стены, так как биом один.
                # Добавляем рандом для текстуры, чтобы не было однотонно.
                wall_variant = fbm(x, y, seed=777, octaves=1, base_scale=10.0)
                if wall_variant < 0.3:
                    block_name = "sand-wall1"
                elif wall_variant < 0.7:
                    block_name = "sand-wall2"
                else:
                    block_name = "sand-wall-large"
            else:
                # Песок. Тоже добавляем вариации.
                sand_variant = fbm(x, y, seed=888, octaves=1, base_scale=15.0)
                if sand_variant < 0.4:
                    block_name = "sand-floor1"
                elif sand_variant < 0.8:
                    block_name = "sand-floor2"
                else:
                    block_name = "sand-floor3"

            # 3. ОГРАНИЧЕНИЕ ПО КРАЯМ (чтобы карта не была открыта)
            # Если x или y меньше 5 или больше WIDTH-5, ставим стену
            if x < 5 or x > WIDTH - 5 or y < 5 or y > HEIGHT - 5:
                block_name = "sand-wall-large"

            world.append({"x": x, "y": y, "name": block_name})

    with open("relief.json", "w", encoding="utf-8") as f:
        json.dump(world, f, separators=(",", ":"))

def generate_blocks():
    rocks = []
    
    cx, cy = WIDTH / 2.0, HEIGHT / 2.0
    max_r = math.sqrt(cx * cx + cy * cy)

    # Проходим по всей карте
    for y in range(HEIGHT):
        for x in range(WIDTH):
            
            # Вытягиваем скалы (по диагонали)
            noise_x = x * 0.7
            noise_y = y * 1.3
            
            # Базовый шум для определения зон, где могут быть скалы
            base_noise = fbm(noise_x, noise_y, seed=SEED, octaves=4, base_scale=25.0)
            
            # Радиальный градиент (чтобы по краям скал было больше)
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy) / max_r
            
            height_val = base_noise * 0.8 + dist * 0.4
            
            # Если высота больше порога — мы в зоне скал
            if height_val > 0.55:
                # Дополнительный высокочастотный шум для остроты
                sharp_noise = fbm(x * 1.5, y * 1.5, seed=777, octaves=3, base_scale=8.0)
                
                # Если шум дает высокое значение, ставим скалу
                if sharp_noise > 0.45:
                    # Выбираем вариант текстуры для скалы
                    wall_variant = fbm(x, y, seed=999, octaves=1, base_scale=5.0)
                    if wall_variant < 0.4:
                        block_name = "stone-wall1"
                    elif wall_variant < 0.8:
                        block_name = "stone-wall2"
                    else:
                        block_name = "stone-wall-large"
                    
                    rocks.append({"x": x, "y": y, "name": block_name})

    # Сохраняем только скалы
    with open("blocks.json", "w", encoding="utf-8") as f:
        json.dump(rocks, f, separators=(",", ":"))

if __name__ == "__main__":
    generate_relief()
    generate_blocks()
    print("ok")
