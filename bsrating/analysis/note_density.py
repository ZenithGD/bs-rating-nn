import numpy as np

def note_density(map_data, resolution, kernel_width) -> tuple[np.array, np.array, np.array, np.array]:

    max_ts = max(map_data, key=lambda m : m["beat"])["beat"]
    els = int(max_ts / resolution) + 1
    map_ts = np.linspace(0.0, max_ts, els)
    map_density = np.zeros(els)
    map_density_left = np.zeros(els)
    map_density_right = np.zeros(els)

    for note in map_data:

        # if it is a note, accumulate density into the array, otherwise skip
        if note["type"] not in [0, 1]:
            continue

        ts_range_min = np.maximum(note["beat"] - kernel_width / 2.0, 0)
        ts_range_max = np.minimum(note["beat"] + kernel_width / 2.0, max_ts)
        acc_mask = np.logical_and(map_ts > ts_range_min, map_ts < ts_range_max)

        map_density[acc_mask] += 1

        if note["type"] == 0:
            map_density_left[acc_mask] += 1

        if note["type"] == 1:
            map_density_right[acc_mask] += 1
        
    return map_ts, map_density / kernel_width * 2.0, map_density_left / kernel_width * 2.0, map_density_right / kernel_width * 2.0

