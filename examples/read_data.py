from typing import Dict, List
import numpy as np
from pylsl import StreamInlet, resolve_stream, StreamInfo
import mne
from datetime import datetime
from pylsl import StreamInlet, resolve_stream
from attrs import define, field, Factory
import os
import time
import signal
import sys
from .common import ActiveLSLStream, stream_names, stream_channels_dict

def main():
    ## INPUTS: stream_channels_dict
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams: List[StreamInlet] = resolve_stream()
    stream_inlet_dict = {a_stream.name():a_stream for a_stream in resolve_stream()}
    # streams: List[StreamInlet] = resolve_stream('name', 'Epoc X')
    print(f'streams: {streams}')        
    for a_stream in streams:
        print(f'a_stream: {a_stream.name()}')
    # # print("looking for an EEG stream...")
    # # streams = resolve_stream('type', 'EEG')

    # # create a new inlet to read from the stream
    # inlet = StreamInlet(streams[0])

    # active_steams_dict: Dict[str, ActiveLSLStream] = {a_stream_name:ActiveLSLStream.init_from_name(name=a_stream_name, ch_names=a_channels) for a_stream_name, a_channels in stream_channels_dict.items()}
        
    # while True:
    #     for a_stream_name, an_active_stream in active_steams_dict.items():
    #         an_active_stream
    #     # # get a new sample (you can also omit the timestamp part if you're not
    #     # # interested in it)
    #     # sample, timestamp = inlet.pull_sample()

    #     # print(sample, timestamp)


if __name__ == '__main__':
    main()
