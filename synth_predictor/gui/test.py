from pathlib import Path

import surgepy

from utils import play_buffer, plot_buf, midi_to_buf


def main():
    root_dir = Path(r"/home/gitaar9/Documents/Surge XT/Patches/")
    all_presets = root_dir.rglob("*.fxp")
    midi_path = r"/samsung_hdd/Files/Projects/surge_predictor/data/chpn_op7_1.mid"

    for preset in all_presets:
        synth = surgepy.createSurge(44100)
        synth.loadPatch(str(preset))
        buf = midi_to_buf(synth, midi_path)
        print(buf.shape)
        plot_buf(buf)
        play_buffer(buf)


if __name__ == '__main__':
    main()
