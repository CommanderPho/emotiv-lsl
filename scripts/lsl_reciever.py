#!/usr/bin/env python3
"""
Lab Streaming Layer (LSL) receiver for Emotiv EEG data.
Connects to an LSL stream and prints EEG information.
"""

import time
import numpy as np
from bsl import StreamReceiver
from bsl.lsl import resolve_streams


def main():
    """Main function to receive and display EEG data from LSL stream."""

    print("Looking for available LSL streams...")

    # Resolve available streams (wait up to 10 seconds)
    streams = resolve_streams(timeout=10.0)

    if not streams:
        print("No LSL streams found. Make sure your Emotiv device is streaming data.")
        return

    # Display available streams
    print(f"Found {len(streams)} stream(s):")
    for i, stream in enumerate(streams):
        # Fixed: removed parentheses - these are properties, not methods
        print(f"  {i}: {stream.name} - {stream.stype} "
              f"({stream.n_channels} channels at {stream.sfreq} Hz)")

    # Find EEG stream (look for 'EEG' type or Emotiv-related names)
    eeg_stream = None
    for stream in streams:
        if (stream.stype.lower() == 'eeg' or 
            'emotiv' in stream.name.lower() or 
            'eeg' in stream.name.lower()):
            eeg_stream = stream
            break

    if eeg_stream is None:
        print("No EEG stream found. Using the first available stream.")
        eeg_stream = streams[0]

    print(f"\nConnecting to stream: {eeg_stream.name}")
    print(f"Stream info:")
    print(f"  Type: {eeg_stream.stype}")
    print(f"  Channels: {eeg_stream.n_channels}")
    print(f"  Sampling rate: {eeg_stream.sfreq} Hz")
    print(f"  Source ID: {eeg_stream.source_id}")

    # Create StreamReceiver
    try:
        receiver = StreamReceiver(stream=eeg_stream)
        receiver.start()

        print(f"\nChannel names: {receiver.ch_names}")
        print("\nStarting data acquisition... (Press Ctrl+C to stop)")
        print("-" * 60)

        sample_count = 0
        start_time = time.time()

        while True:
            # Get data (this will block until data is available)
            data, timestamps = receiver.acquire()

            if data is not None and len(data) > 0:
                sample_count += len(data)
                current_time = time.time()

                # Print data info every 100 samples to avoid spam
                if sample_count % 100 == 0:
                    elapsed_time = current_time - start_time

                    print(f"Time: {elapsed_time:.1f}s | Samples: {sample_count}")
                    print(f"Latest sample: {data[-1]}")
                    print(f"Timestamp: {timestamps[-1]:.6f}")

                    # Print channel-wise data
                    for i, (ch_name, value) in enumerate(zip(receiver.ch_names, data[-1])):
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
        if 'receiver' in locals():
            receiver.stop()
        print("Receiver stopped.")


if __name__ == "__main__":
    main()
