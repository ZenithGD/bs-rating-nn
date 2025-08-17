import argparse 
import json
from matplotlib import pyplot as plt
from pprint import pprint
from tqdm import tqdm, trange
from bsrating.analysis import *
from scipy import signal

from dotenv import load_dotenv

def load_map(path: str) -> dict:

    with open(path) as fp:
        return json.load(fp)

def main(args):

    map_data = load_map(args.data)

    # 1. analyze note density
    map_ts, density, d_left, d_right = note_density(map_data["data"], 1 / 8, args.kernel_width)
    _, density_k1, d_left_k1, d_right_k1 = note_density(map_data["data"], 1 / 8, 2)

    # 2. peak analysis
    peaks = signal.find_peaks_cwt(-density, 16, gap_thresh=16)
    peaks_left = signal.find_peaks_cwt(-d_left, 16, gap_thresh=16)
    peaks_right = signal.find_peaks_cwt(-d_right, 16, gap_thresh=16)

    # 3. plot density graph for both and separate hands
    fig, (ax_both, ax_left, ax_right) = plt.subplots(3, 1)
    
    ax_both.plot(map_ts, density, '-g')
    ax_both.plot(map_ts, density_k1, '-g', alpha=0.4)
    ax_both.set_title("Both hands")
    ax_both.set_xlim(map_ts.min(), map_ts.max())
    for peak in peaks:
        ax_both.axvline(map_ts[peak], linestyle="--", c="red", linewidth=1.0)

    ax_left.plot(map_ts, d_left, '-r')
    ax_left.plot(map_ts, d_left_k1, '-r', alpha=0.4)
    ax_left.set_title("Left hand")
    ax_left.set_xlim(map_ts.min(), map_ts.max())
    for peak in peaks_left:
        ax_left.axvline(map_ts[peak], linestyle="--", c="red", linewidth=1.0)

    ax_right.plot(map_ts, d_right, '-b')
    ax_right.plot(map_ts, d_right_k1, '-b', alpha=0.4)
    ax_right.set_title("Right hands")
    ax_right.set_xlim(map_ts.min(), map_ts.max())
    for peak in peaks_right:
        ax_right.axvline(map_ts[peak], linestyle="--", c="red", linewidth=1.0)

    fig.suptitle("Note density")
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Analyze ")

    parser.add_argument("data", help="The file containing the processed difficulty data")
    parser.add_argument("--kernel_width", "-k", help="The width of the averaging kernel", type=float, default=8)
    main(parser.parse_args())