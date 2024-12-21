import pandas as pd
import zipfile
from pydub import AudioSegment
from io import BytesIO
import numpy as np

BIT_DEPTH = 32768.0



def read_zipped_mp3(file):
    # Reads binary data and returns mono signal
    mp3_data = file.read()  # Read the binary data of the mp3 file
    audio = AudioSegment.from_file(BytesIO(mp3_data), format="mp3")
    mono_audio = audio.set_channels(1)
    centered_mono = mono_audio.pan(-0.5)
    return centered_mono

data_path = "/Users/cemerturkan/Desktop/personal_projects/data/"
metadata_df = pd.read_csv(data_path + 'output_embed/embeddings_metadata.csv', index_col=0)

correct_indices = [int(file_idx.split('_')[-1]) for file_idx in list(metadata_df.index)]


with zipfile.ZipFile(data_path + 'fma_small.zip', 'r') as zip_ref:
    file_names = [file_name for file_name in zip_ref.namelist() if file_name.endswith('.mp3')]
    for idx, file_name in enumerate(file_names):
        if idx in correct_indices:
            print(idx)
            with zip_ref.open(file_name) as mp3_file:
                mono_signal = read_zipped_mp3(mp3_file)
            
            mono_signal.export(data_path + 'songs/' + str(idx) + '.mp3', format="mp3")
        
        