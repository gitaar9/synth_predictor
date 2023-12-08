import numpy as np
import sounddevice as sd
import surgepy
from matplotlib import pyplot as plt
import mido
from surgepy import SurgeSynthesizer, SurgeNamedParamId


def play_buffer(buffer, sample_rate=44100):
    sd.play(buffer.T, samplerate=sample_rate)
    sd.wait()


def plot_buf(buf, sample_rate=44100, show=True):
    t = np.linspace(0, np.shape(buf)[1] * 1.0 / sample_rate, np.shape(buf)[1])
    plt.plot(t, buf[0])
    plt.title("Waveform")
    plt.xlabel("Time (sec)")
    plt.ylabel("Wave")
    if show:
        plt.show()


def midi_to_buf(synth: SurgeSynthesizer, midi_file: str, start_time=0, end_time=25):
    curr_block = 0
    total_time = end_time - start_time
    mf = mido.MidiFile(midi_file)

    bps = synth.getSampleRate() / synth.getBlockSize()
    buf = synth.createMultiBlock(int(bps * total_time))

    for msg in mf:
        if start_time + msg.time > end_time:
            break
        if msg.time != 0:
            blocks = round(msg.time * bps)
            synth.processMultiBlock(buf, curr_block, blocks)
            curr_block = curr_block + blocks
            start_time = start_time + msg.time

        if msg.type == 'note_on' and msg.velocity != 0:
            synth.playNote(0, msg.note, msg.velocity, 0)
        if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            synth.releaseNote(0, msg.note, 0)

    return buf


def ensure_synth_loaded(synth: SurgeSynthesizer):
    onesec = int(synth.getSampleRate() / synth.getBlockSize())
    buf = synth.createMultiBlock(onesec)
    synth.processMultiBlock(buf, 0, onesec)


def play_C7_chord(synth: SurgeSynthesizer):
    onesec = int(synth.getSampleRate() / synth.getBlockSize())
    buf = synth.createMultiBlock(2 * onesec)

    chd = [60, 63, 67, 71]
    for n in chd:
        synth.playNote(0, n, 127, 0)
    synth.processMultiBlock(buf, 0, onesec)

    for n in chd:
        synth.releaseNote(0, n, 0)
    synth.processMultiBlock(buf, onesec)

    return buf


def named_param_to_string(synth: SurgeSynthesizer, named_param: SurgeNamedParamId):
    return synth.getParamInfo(named_param)
