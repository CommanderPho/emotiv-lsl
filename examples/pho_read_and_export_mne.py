import numpy as np
from pylsl import StreamInlet, resolve_stream
import mne
from datetime import datetime
import os
import time
import signal
import sys

# Flag to control the recording loop
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit the recording loop"""
    global running
    print("\nStopping recording...")
    running = False

def main():
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # first resolve an EEG stream on the lab network
    print('Looking for an EEG stream...')
    streams = resolve_stream('type', 'EEG')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    # get the stream info
    info = inlet.info()
    
    # get the sampling frequency
    sfreq = float(info.nominal_srate())
    
    # Get channel count
    n_channels = info.channel_count()
    
    # For Emotiv EPOC X, we know the channel names
    # This is safer than trying to extract from LSL which might be causing the error
    ch_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
    
    # Ensure we have the right number of channel names
    if len(ch_names) != n_channels:
        print(f"Warning: Expected {n_channels} channels but have {len(ch_names)} channel names")
        # If channel count doesn't match, create generic channel names
        ch_names = [f'CH{i+1}' for i in range(n_channels)]
    
    # Create MNE info object
    mne_info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
    
    # Define recording parameters
    chunk_duration_minutes = 10
    chunk_samples = int(sfreq * 60 * chunk_duration_minutes)
    
    print(f"Recording in {chunk_duration_minutes}-minute chunks. Press Ctrl+C to stop.")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Channels: {ch_names}")
    
    chunk_count = 0
    
    while running:
        chunk_count += 1
        print(f"\nStarting chunk {chunk_count}...")
        
        # Create a buffer for this chunk
        buffer = np.zeros((n_channels, chunk_samples))
        
        # Record start time for this chunk
        chunk_start_time = time.time()
        
        # Fill the buffer
        for i in range(chunk_samples):
            if not running:
                print("Recording interrupted.")
                break
                
            try:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
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
            if i % int(sfreq * 5) == 0 and i > 0:
                elapsed = time.time() - chunk_start_time
                total = chunk_samples / sfreq
                print(f"Recording: {elapsed:.1f}s / {total:.1f}s ({elapsed/total*100:.1f}%)")
        
        # If we have data and haven't been interrupted mid-chunk
        if running or i > sfreq * 10:  # At least 10 seconds of data
            # Create a raw object with the recorded data
            # If interrupted, use only the filled portion of the buffer
            if not running and i < chunk_samples - 1:
                buffer = buffer[:, :i+1]
                
            raw = mne.io.RawArray(buffer, mne_info)
            
            # Create a valid filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_{timestamp}_chunk{chunk_count}_raw.fif"
            
            # Save the raw data
            print(f"Saving chunk {chunk_count}...")
            raw.save(filename)
            print(f"Data saved to {os.path.abspath(filename)}")
        
    print("Recording stopped.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
