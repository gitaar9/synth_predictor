import unittest
from pathlib import Path
from unittest import skip

import surgepy

from patch_to_scaled_python import get_patch_in_python, load_python_patch, load_python_patch_unscaled
from utils import play_buffer, play_C7_chord, ensure_synth_loaded


class TestSurgePatchLoading(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(r"/home/gitaar9/Documents/Surge XT/Patches/")
        self.presets = list(self.root_dir.rglob("*.fxp"))
        self.preset_path_1 = str(self.presets[6])
        self.preset_path_2 = str(self.presets[10])

    @staticmethod
    def init_synth():
        return surgepy.createSurge(44100)

    @staticmethod
    def load_synth_with_preset(preset_path: str):
        synth = TestSurgePatchLoading.init_synth()
        synth.loadPatch(preset_path)
        return synth

    @staticmethod
    def get_buffer(synth):
        return play_C7_chord(synth)

    @staticmethod
    def play_sound(synth):
        play_buffer(TestSurgePatchLoading.get_buffer(synth))

    @staticmethod
    def get_unequal_params(patch_1, patch_2):
        mistakes = []
        for (patch_1_id, patch_1_param, patch_1_value), (patch_2_id, patch_2_param, patch_2_value) in zip(patch_1, patch_2):
            if not patch_1_id == patch_2_id:
                raise RuntimeError("Patch ids dont match")
            if not patch_1_value == patch_2_value:
                mistakes.append((patch_1_param, patch_1_value, patch_2_value))
        return mistakes

    def assert_patch_equal(self, patch_1, patch_2):
        self.assertEqual(len(self.get_unequal_params(patch_1, patch_2)), 0)

    @skip
    def test_get_scaled_python_patch_and_load(self):
        synth = self.load_synth_with_preset(self.preset_path_1)
        python_patch_1 = get_patch_in_python(synth)

        synth = self.init_synth()
        # Load the patch
        load_python_patch(synth, python_patch_1)

        # Add assertions as needed
        python_patch_after_load = get_patch_in_python(synth)

        self.assert_patch_equal(python_patch_1, python_patch_after_load)

    @skip
    def test_get_unscaled_python_patch_and_load(self):
        synth = self.load_synth_with_preset(self.preset_path_1)
        python_patch_1 = get_patch_in_python(synth, scale=False)

        self.play_sound(synth)

        synth = self.init_synth()
        # Load the patch
        load_python_patch_unscaled(synth, python_patch_1)

        # Add assertions as needed
        python_patch_after_load = get_patch_in_python(synth, scale=False)
        python_patch_after_load = get_patch_in_python(synth, scale=False)

        self.play_sound(synth)

        unequal_params = self.get_unequal_params(python_patch_1, python_patch_after_load)
        for u in unequal_params:
            print(u)

        self.assert_patch_equal(python_patch_1, python_patch_after_load)

    def test_set_single_param(self):
        synth = self.init_synth()
        python_patch_1 = get_patch_in_python(synth, scale=False)
        load_python_patch_unscaled(synth, python_patch_1)

        param = synth.getPatch()['scene'][0]['osc'][2]['p'][0]
        set_to = 1.0

        synth.setParamVal(param, 1.0)
        self.assertEqual(synth.getParamVal(param), set_to)

    def test_patch_equally_long(self):
        synth = self.load_synth_with_preset(self.preset_path_1)
        ensure_synth_loaded(synth)
        python_patch_1 = get_patch_in_python(synth, scale=False)
        self.play_sound(synth)
        # Make sure a newly inited patch has same params
        synth = self.init_synth()
        ensure_synth_loaded(synth)

        self.assertEqual(
            [synth.getParameterName(param.getId()) for _, param, _ in python_patch_1],
            [synth.getParameterName(param.getId()) for _, param, _ in get_patch_in_python(synth, scale=False)]
        )

        # Make sure after loading the params are still the same
        load_python_patch_unscaled(synth, python_patch_1)
        ensure_synth_loaded(synth)
        load_python_patch_unscaled(synth, python_patch_1)
        ensure_synth_loaded(synth)
        load_python_patch_unscaled(synth, python_patch_1)
        ensure_synth_loaded(synth)
        load_python_patch_unscaled(synth, python_patch_1)
        ensure_synth_loaded(synth)
        load_python_patch_unscaled(synth, python_patch_1)
        ensure_synth_loaded(synth)
        self.play_sound(synth)

        self.assertEqual(
            [synth.getParameterName(param.getId()) for _, param, _ in python_patch_1],
            [synth.getParameterName(param.getId()) for _, param, _ in get_patch_in_python(synth, scale=False)]
        )

        unscaled_patch_after_load = get_patch_in_python(synth, scale=False)
        self.assertTrue('A Osc 3 Unison Detune' in [synth.getParameterName(param.getId()) for _, param, _ in unscaled_patch_after_load])
        self.assertTrue('A Osc 3 Unison Detune' in [synth.getParameterName(param.getId()) for _, param, _ in python_patch_1])

        unequal_params = self.get_unequal_params(python_patch_1, unscaled_patch_after_load)
        for param, old, new in unequal_params:
            print(synth.getParameterName(param.getId()), param, old, new)
        self.assert_patch_equal(python_patch_1, unscaled_patch_after_load)


if __name__ == '__main__':
    unittest.main()
