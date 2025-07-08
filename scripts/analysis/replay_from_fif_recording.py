import argparse
import time
from pathlib import Path

import mne
import pylsl


def stream_from_fif(file_path: Path):
    """
    Loads an MNE Raw object from a .fif file and streams it over LSL.

    Args:
        file_path (Path): The path to the .fif file.


	Usage:
	## From the command line:

    	python scripts/analysis/replay_from_fif_recording.py  "E:/Dropbox (Personal)/Databases/UnparsedData/EmotivEpocX_EEGRecordings/fif/20250702-191054-Epoc X-raw.fif"
     
    """
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return

    print(f"Loading data from {file_path}...")
    # Preload data into memory to prevent disk I/O during streaming
    raw = mne.io.read_raw_fif(file_path, preload=True)

    # Extract information from the MNE Raw object
    sfreq = raw.info['sfreq']
    ch_names = raw.info['ch_names']
    n_channels = len(ch_names)
    # MNE loads data in shape (n_channels, n_samples)
    data = raw.get_data()

    # Create a new LSL stream outlet
    # Use the filename to create a unique stream name
    stream_name = f'Replay-{file_path.stem}'
    stream_type = 'EEG'
    # Use the full file path as a unique source identifier
    source_id = str(file_path.resolve())

    info = pylsl.StreamInfo(name=stream_name, type=stream_type,
                            channel_count=n_channels, nominal_srate=sfreq,
                            channel_format=pylsl.cf_float32, source_id=source_id)

    # Add channel information to the stream description (very useful for recipients)
    channels = info.desc().append_child("channels")
    for ch_name in ch_names:
        ch = channels.append_child("channel")
        ch.append_child_value("label", ch_name)
        # MNE's default unit for EEG is Volts. We'll specify it here.
        ch.append_child_value("unit", "volts")
        ch.append_child_value("type", "EEG")

    # Create the outlet
    outlet = pylsl.StreamOutlet(info)

    print(f"Streaming {n_channels} channels at {sfreq} Hz from stream '{stream_name}'...")
    print("Press Ctrl+C to stop.")

    try:
        # Transpose data for easier iteration over samples (n_samples, n_channels)
        data_to_stream = data.T
        total_samples = data_to_stream.shape[0]
        wait_time = 1.0 / sfreq

        for i, sample in enumerate(data_to_stream):
            # Push the sample to the LSL stream
            # The sample is a numpy array of shape (n_channels,)
            outlet.push_sample(sample)

            # Wait to maintain the original sampling rate
            time.sleep(wait_time)

            # Optional: Print progress every second
            if (i + 1) % int(sfreq) == 0:
                print(f"  ... streamed {i+1}/{total_samples} samples", end='\r')

    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    finally:
        print("\nStreaming finished.")


def main():
    """Parses command-line arguments and starts the streaming process."""
    parser = argparse.ArgumentParser(
        description="Replay an EEG recording from a .fif file as an LSL stream.")
    parser.add_argument("file_path", type=str,
                        help="Path to the .fif file to be streamed.")
    args = parser.parse_args()

    file_path = Path(args.file_path).resolve()
    stream_from_fif(file_path)


if __name__ == '__main__':
    main()
