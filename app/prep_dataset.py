from os import listdir
from os.path import isfile, join
import re
from math import floor
from math import ceil
from pydub import AudioSegment

import pandas as pd

DATA_PATH='../data/'

def main():
    grid_files = [f for f in listdir(DATA_PATH) if isfile(join(DATA_PATH, f)) and f.endswith('.TextGrid')]
    if len(grid_files) == 0:
        return 1

    time_regex = re.compile(r"[0-9\.]+")
    file_dict = []
    for grid_file in grid_files:
        with open(join(DATA_PATH, grid_file), 'r', encoding='cp1252') as f:
            audio_fname = join(DATA_PATH, grid_file[:grid_file.index('.')] + '.wav')
            audio_file = AudioSegment.from_wav(audio_fname)
            audio_file = audio_file.set_frame_rate(16000).set_channels(1)
            init_t = None
            end_t = None
            text = ""
            for line in f:
                if 'xmin' in line:
                    init_t = float(time_regex.search(line).group(0)) * 1000
                elif 'xmax' in line:
                    end_t = float(time_regex.search(line).group(0)) * 1000
                elif 'text = ' in line and init_t is not None and end_t is not None:
                    text = line[(line.index('=') + 3):-2]
                    if len(text) < 5:
                        continue
                    temp_audio = audio_file[floor(init_t):ceil(end_t)]
                    filename = f"{grid_file[:(grid_file.index('.'))]}_{floor(init_t // 1000)}.wav"
                    temp_audio.export("../data/processed/" + filename, format="wav")
                    file_dict.append({'file': "../data/processed/" + filename, 'text': text})
                    init_t = None
                    end_t = None
                else:
                    init_t = None
                    end_t = None
                    text = None

    df = pd.DataFrame(file_dict, columns=['file', 'text'])
    df['text'] = df['text'].str.strip(', "')
    print(df)
    df.to_csv("../data/processed/kaqchikel_dataset.csv")

if __name__ == '__main__':
    main()
