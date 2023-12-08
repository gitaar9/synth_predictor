from copy import copy
from pathlib import Path
from typing import List, Tuple

import surgepy
from surgepy import SurgeNamedParamId, SurgeSynthesizer

from utils import play_buffer, play_C7_chord, named_param_to_string


def scale_value(value, min_value, max_value):
    """
    Scale a value between 0 and 1 based on min and max values.

    Parameters:
    - value: The original value to be scaled.
    - min_value: The minimum value of the range.
    - max_value: The maximum value of the range.

    Returns:
    - The scaled value between 0 and 1.
    """
    return (value - min_value) / (max_value - min_value)


def inverse_scale_value(scaled_value, min_value, max_value):
    """
    Inverse scale a value from 0 to 1 back to the original range.

    Parameters:
    - scaled_value: The scaled value between 0 and 1.
    - min_value: The minimum value of the original range.
    - max_value: The maximum value of the original range.

    Returns:
    - The original value.
    """
    return scaled_value * (max_value - min_value) + min_value


def named_param_to_scalar(synth: SurgeSynthesizer, named_param: SurgeNamedParamId, scale=True):
    val = copy(synth.getParamVal(named_param))
    minimum = synth.getParamMin(named_param)
    maximum = synth.getParamMax(named_param)
    val_type = synth.getParamValType(named_param)
    if not scale:
        return val
    if val_type == 'bool':
        return scale_value(val, minimum, maximum)
    elif val_type == 'int':  # TODO: use minimum aswell
        return scale_value(val, minimum, maximum)
    elif val_type == 'float':
        return scale_value(val, minimum, maximum)
    else:
        raise TypeError(f'Unknown type {val_type}')


def walk_patch(synth: SurgeSynthesizer, part_of_patch, scale=True):
    if isinstance(part_of_patch, list):
        return [walk_patch(synth, item, scale=scale) for item in part_of_patch]
    elif isinstance(part_of_patch, dict):
        return [walk_patch(synth, value, scale=scale) for value in part_of_patch.values()]
    elif isinstance(part_of_patch, SurgeNamedParamId):
        return part_of_patch.getId().getSynthSideId(), part_of_patch, named_param_to_scalar(synth, part_of_patch, scale=scale)
    else:
        raise TypeError(f'Unknown type {type(part_of_patch)}')


def flatten_list(nested_list):
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten_list(item))
        else:
            flattened_list.append(item)
    return flattened_list


def get_patch_in_python(synth: SurgeSynthesizer, scale=True) -> List[Tuple[SurgeNamedParamId, float]]:
    python_patch = flatten_list(walk_patch(synth, synth.getPatch(), scale=scale))

    order = ['Disable', 'Type']
    order = ['Type', 'Disable']

    def custom_sort(p):
        if order[0] in synth.getParameterName(p[1].getId()):
            return (0, p[0])
        elif order[1] in synth.getParameterName(p[1].getId()):
            return (1, p[0])
        else:
            return (2, p[0])

    python_patch = list(sorted(python_patch, key=custom_sort))
    return python_patch


def load_python_patch(synth: SurgeSynthesizer, python_patch: List[Tuple[SurgeNamedParamId, float]]):
    for param_id, named_param, value in python_patch:
        minimum = synth.getParamMin(named_param)
        maximum = synth.getParamMax(named_param)
        val_type = synth.getParamValType(named_param)

        # if minimum == -2147483648.0 and maximum == 2147483648.0:
        #     synth.setParamVal(named_param, synth.getParamDef(named_param))
        #     continue

        unscaled_value = inverse_scale_value(value, minimum, maximum)
        # if val_type == 'bool':
        #     unscaled_value = round(unscaled_value)
        # elif val_type == 'int':
        #     unscaled_value = round(unscaled_value)

        # synth.setParamVal(named_param, synth.getParamDef(named_param))
        synth.setParamVal(named_param, float(unscaled_value))
        # play_C7_chord(synth)
        # if unscaled_value != synth.getParamVal(named_param) or param_id == 218:
        #     print(type(synth.getParamDef(named_param)))
        #
        #     print(unscaled_value, synth.getParamVal(named_param), minimum, maximum)


def load_python_patch_unscaled(synth: SurgeSynthesizer, python_patch: List[Tuple[SurgeNamedParamId, float]]):
    for param_id, named_param, value in python_patch:
        synth.setParamVal(named_param, value)


def main():
    root_dir = Path(r"/home/gitaar9/Documents/Surge XT/Patches/")
    presets = list(root_dir.rglob("*.fxp"))
    preset_path_1 = presets[0]
    preset_path_2 = presets[10]

    # Load patch 1 and play
    synth = surgepy.createSurge(44100)
    synth.loadPatch(str(preset_path_1))
    buf = play_C7_chord(synth)
    python_patch_1 = get_patch_in_python(synth)
    print([i for i, _, _ in python_patch_1])
    unscaled_patch_before = get_patch_in_python(synth, scale=False)
    play_buffer(buf)

    # Load patch 1 again using the python patch and play
    synth = surgepy.createSurge(44100)
    synth.loadPatch(str(preset_path_1))

    load_python_patch(synth, python_patch_1)
    buf = play_C7_chord(synth)
    print()
    load_python_patch(synth, python_patch_1)
    buf = play_C7_chord(synth)
    unscaled_patch_after = get_patch_in_python(synth, scale=False)

    buf = play_C7_chord(synth)
    play_buffer(buf)

    total_mistakes = 0
    for (scaled_before_id, _, scaled_before_value), (before_id, before_param, before_value), (after_id, after_param, after_value) in zip(python_patch_1, unscaled_patch_before, unscaled_patch_after):
        if before_value != after_value:
            print(scaled_before_id, before_id, after_id)
            print(before_value, after_value)
            minimum = synth.getParamMin(after_param)
            maximum = synth.getParamMax(after_param)
            print(inverse_scale_value(scaled_before_value, minimum, maximum))

            print(named_param_to_string(synth, before_param))
            print(synth.getParameterName(after_param.getId()))
            print()
            total_mistakes += 1

    print(total_mistakes)

    exit()
    # Load patch2 and play
    synth = surgepy.createSurge(44100)
    synth.loadPatch(str(preset_path_2))
    python_patch_2 = get_patch_in_python(synth)
    buf = play_C7_chord(synth)
    play_buffer(buf)

    # Load patch 1 again using the python patch and play
    synth = surgepy.createSurge(44100)
    load_python_patch(synth, python_patch_1)
    buf = play_C7_chord(synth)
    play_buffer(buf)

    # Load patch 2 again using the python patch and play
    synth = surgepy.createSurge(44100)
    buf = play_C7_chord(synth)
    load_python_patch(synth, python_patch_2)
    play_buffer(buf)


if __name__ == '__main__':
    main()
