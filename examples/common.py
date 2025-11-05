import sys, os

from datetime import datetime

import numpy as np
from mne import Info, create_info
from mne.io.array import RawArray
from pathlib import Path
from typing import List
from pylsl import StreamInlet, resolve_stream, StreamInfo
import mne
from datetime import datetime
from pylsl import StreamInlet, resolve_stream
from attrs import define, field, Factory
import os
import time
import signal
import sys

stream_names = ['Epoc X eQuality', 'Epoc X', 'Epoc X Motion']
stream_channels_dict = {'Epoc X': ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'],
                          'Epoc X Motion': ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ'],
                            'Epoc X eQuality': None,
}


# modality_sfreq_dict = {'EEG': 128, 'MOTION': 16,  'Epoc X eQuality': 128
# }


@define(slots=False)
class ActiveLSLStream:
    """ Attempts to manage an independent recorder for an LSL stream
    from emotiv-lsl.examples.common import ActiveLSLStream
    """
    name: str = field()
    stream: StreamInlet = field()
    ch_names: List[str] = field(default=Factory(list))

    chunk_duration_minutes: int = field(default=10)

    ## Computed:    
    info: StreamInfo = field(init=False)
    sfreq: float = field(init=False)
    n_channels: int = field(init=False)

    chunk_samples: int = field(init=False) 
    mne_info: mne.Info = field(init=False)
    # int(sfreq * 60 * chunk_duration_minutes)

    running: bool = field(default=True)
    chunk_count: int = field(default=0)


    def __attrs_post_init__(self):
        # get the stream info
        self.info = self.stream.info()

        # get the sampling frequency
        self.sfreq = float(self.info.nominal_srate())

        # Get channel count
        self.n_channels = self.info.channel_count()

        assert self.n_channels == len(self.ch_names), f"self.ch_names: {self.ch_names} is of length {len(self.ch_names)} which is not equal to self.n_channels {self.n_channels} in the stream!"

        # Ensure we have the right number of channel names
        if len(self.ch_names) != self.n_channels:
            print(f"Warning: Expected {self.n_channels} channels but have {len(self.ch_names)} channel names")
            # If channel count doesn't match, create generic channel names
            self.ch_names = [f'CH{i+1}' for i in range(self.n_channels)]

        # Create MNE info object
        self.mne_info = mne.create_info(ch_names=self.ch_names, sfreq=self.sfreq, ch_types='eeg')

        self.chunk_samples = int(self.sfreq * 60 * self.chunk_duration_minutes)



    @classmethod
    def init_from_name(cls, name: str, ch_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']):
        # first resolve an EEG stream on the lab network
        print('Looking for an EEG stream...')
        # streams = resolve_stream('type', 'EEG')
        # create a new inlet to read from the stream
        # inlet = StreamInlet(streams[0])
        
        stream_inlet_dict = {a_stream.name():a_stream for a_stream in resolve_stream()}
        assert name in stream_inlet_dict, f"name: {name} is missing from {list(stream_inlet_dict.keys())}"
        # create a new inlet to read from the stream
        inlet = StreamInlet(stream_inlet_dict[name])

        _obj = cls(name=name, stream=inlet, ch_names=ch_names)
        return _obj



    def run(self):
        """ main run loop 
        """
        print(f"Recording in {self.chunk_duration_minutes}-minute chunks. Press Ctrl+C to stop.")
        print(f"Sampling rate: {self.sfreq} Hz")
        print(f"Channels: {self.ch_names}") 

        while self.running:
            self.chunk_count += 1
            print(f"\nStarting chunk {self.chunk_count}...")

            # Create a buffer for this chunk
            buffer = np.zeros((self.n_channels, self.chunk_samples))

            # Record start time for this chunk
            chunk_start_time = time.time()

            # Fill the buffer
            for i in range(self.chunk_samples):
                if not self.running:
                    print("Recording interrupted.")
                    break

                try:
                    sample, timestamp = self.inlet.pull_sample(timeout=1.0)
                    if sample:
                        buffer[:, i] = sample
                    else:
                        # If no sample received, repeat the last sample or use zeros
                        if i > 0:
                            buffer[:, i] = buffer[:, i-1]
                        continue
                except Exception as e:
                    print(f"Error reading sample: {e}")
                    if i > 0:
                        buffer[:, i] = buffer[:, i-1]
                    continue

                # Print progress every 5 seconds
                if i % int(self.sfreq * 5) == 0 and i > 0:
                    elapsed = time.time() - chunk_start_time
                    total = self.chunk_samples / self.sfreq
                    print(f"Recording: {elapsed:.1f}s / {total:.1f}s ({elapsed/total*100:.1f}%)")

            # If we have data and haven't been interrupted mid-chunk
            if self.running or i > self.sfreq * 10:  # At least 10 seconds of data
                # Create a raw object with the recorded data
                # If interrupted, use only the filled portion of the buffer
                if not self.running and i < self.chunk_samples - 1:
                    buffer = buffer[:, :i+1]

                raw = mne.io.RawArray(buffer, self.mne_info)

                # Create a valid filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_{timestamp}_chunk{self.chunk_count}_raw.fif"

                # Save the raw data
                print(f"Saving chunk {self.chunk_count}...")
                raw.save(filename)
                print(f"Data saved to {os.path.abspath(filename)}")

        print("Recording stopped.")


    def stop(self):
        self.running = False ## stop running
        ## wait for a while


