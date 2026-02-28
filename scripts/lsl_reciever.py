#!/usr/bin/env python3
"""
Lab Streaming Layer (LSL) receiver for Emotiv EEG data.
Connects to an LSL stream, displays data in console, and records to XDF file.
"""

import time
import argparse
from datetime import datetime
from typing import List, Optional
import pylsl
from pylsl import StreamInfo, StreamInlet
from labrecorder import LabRecorder


def get_channel_names_from_stream(stream_info: StreamInfo) -> List[str]:
    """Extract channel names from LSL stream info XML description."""
    channel_names = []
    ch = stream_info.desc().child("channels").child("channel")
    while not ch.empty():
        label = ch.child_value("label")
        if label:
            channel_names.append(label)
        ch = ch.next_sibling("channel")
    # Fallback to generic names if no labels found
    if not channel_names:
        channel_names = [f"Ch{i}" for i in range(stream_info.channel_count())]
    return channel_names


def find_eeg_stream(streams: List[StreamInfo]) -> Optional[StreamInfo]:
    """Find an EEG stream from the list of available streams."""
    for stream in streams:
        if (stream.type().lower() == 'eeg' or 'emotiv' in stream.name().lower() or 'eeg' in stream.name().lower()):
            return stream
    return None


def main():
    """Main function to receive, display, and record EEG data from LSL stream."""
    parser = argparse.ArgumentParser(description='LSL Receiver for Emotiv EEG data with XDF recording')
    parser.add_argument('--filename', '-f', default=None, help='Output XDF filename (default: recording_<timestamp>.xdf)')
    parser.add_argument('--no-record', action='store_true', help='Disable XDF recording, only display data')
    parser.add_argument('--timeout', '-t', type=float, default=10.0, help='Stream discovery timeout in seconds (default: 10.0)')
    args = parser.parse_args()

    # Generate default filename with timestamp if not provided
    if args.filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.filename = f"recording_{timestamp}.xdf"

    print("Looking for available LSL streams...")

    # Use LabRecorder to find streams
    recorder = LabRecorder(filename=args.filename, enable_remote_control=False)
    streams = recorder.find_streams(timeout=args.timeout)

    if not streams:
        print("No LSL streams found. Make sure your Emotiv device is streaming data.")
        recorder.cleanup()
        return

    # Display available streams
    print(f"Found {len(streams)} stream(s):")
    for i, stream in enumerate(streams):
        print(f"  {i}: {stream.name()} - {stream.type()} ({stream.channel_count()} channels at {stream.nominal_srate()} Hz)")

    # Find EEG stream for display (look for 'EEG' type or Emotiv-related names)
    eeg_stream = find_eeg_stream(streams)

    if eeg_stream is None:
        print("No EEG stream found. Using the first available stream for display.")
        eeg_stream = streams[0]

    print(f"\nConnecting to stream for display: {eeg_stream.name()}")
    print(f"Stream info:")
    print(f"  Type: {eeg_stream.type()}")
    print(f"  Channels: {eeg_stream.channel_count()}")
    print(f"  Sampling rate: {eeg_stream.nominal_srate()} Hz")
    print(f"  Source ID: {eeg_stream.source_id()}")

    # Create StreamInlet for real-time display
    inlet = StreamInlet(eeg_stream, max_buflen=360, recover=True)
    channel_names = get_channel_names_from_stream(inlet.info())

    print(f"\nChannel names: {channel_names}")

    # Start recording if enabled
    if not args.no_record:
        print(f"\nStarting XDF recording to: {args.filename}")
        # Select all streams for recording
        stream_uids = [s.uid() for s in streams]
        recorder.select_streams_to_record(stream_uids)
        recorder.start_recording()
    else:
        print("\nRecording disabled (--no-record flag)")

    print("\nStarting data acquisition... (Press Ctrl+C to stop)")
    print("-" * 60)

    sample_count = 0
    start_time = time.time()

    try:
        while True:
            # Pull chunk of data from the inlet for display
            samples, timestamps = inlet.pull_chunk(timeout=0.1, max_samples=128)

            if timestamps:
                sample_count += len(timestamps)
                current_time = time.time()

                # Print data info every 100 samples to avoid spam
                if sample_count % 100 < len(timestamps):
                    elapsed_time = current_time - start_time
                    latest_sample = samples[-1]
                    latest_timestamp = timestamps[-1]

                    print(f"Time: {elapsed_time:.1f}s | Samples: {sample_count}")
                    print(f"Latest sample: {latest_sample}")
                    print(f"Timestamp: {latest_timestamp:.6f}")

                    # Print channel-wise data
                    for ch_name, value in zip(channel_names, latest_sample):
                        print(f"  {ch_name}: {value:.2f} µV")

                    print("-" * 60)

            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\nStopping data acquisition...")
    except Exception as e:
        print(f"Error during data acquisition: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the display inlet
        inlet.close_stream()
        print("Display inlet closed.")

        # Stop recording and cleanup
        if not args.no_record and recorder.is_recording():
            recorder.stop_recording()
        recorder.cleanup()
        print("Receiver stopped.")


if __name__ == "__main__":
    main()
