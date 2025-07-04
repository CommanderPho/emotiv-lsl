#!/usr/bin/env python3
"""
Advanced LSL receiver with signal processing and basic analysis.
"""

import time
import numpy as np
from collections import deque
from bsl import StreamReceiver
from bsl.utils import resolve_streams


class EEGReceiver:
    """Advanced EEG receiver with buffering and basic analysis."""

    def __init__(self, buffer_duration=10.0):
        """
        Initialize the EEG receiver.

        Args:
            buffer_duration (float): Duration of data to keep in buffer (seconds)
        """
        self.buffer_duration = buffer_duration
        self.receiver = None
        self.data_buffer = deque()
        self.timestamp_buffer = deque()
        self.is_running = False

    def connect(self, stream_name=None):
        """Connect to an LSL stream."""
        print("Resolving LSL streams...")
        streams = resolve_streams(timeout=10.0)

        if not streams:
            raise RuntimeError("No LSL streams found")

        # Find target stream
        target_stream = None
        if stream_name:
            for stream in streams:
                if stream_name.lower() in stream.name().lower():
                    target_stream = stream
                    break
        else:
            # Auto-select EEG stream
            for stream in streams:
                if (stream.type().lower() == 'eeg' or 
                    'emotiv' in stream.name().lower()):
                    target_stream = stream
                    break

        if target_stream is None:
            target_stream = streams[0]

        print(f"Connecting to: {target_stream.name()}")
        self.receiver = StreamReceiver(bufsize=2, winsize=1, stream=target_stream)

        return target_stream

    def start(self):
        """Start data acquisition."""
        if self.receiver is None:
            raise RuntimeError("Not connected to any stream")

        self.receiver.start()
        self.is_running = True
        print("Data acquisition started")

    def stop(self):
        """Stop data acquisition."""
        if self.receiver:
            self.receiver.stop()
        self.is_running = False
        print("Data acquisition stopped")

    def get_latest_data(self):
        """Get the latest data from the stream."""
        if not self.is_running:
            return None, None

        data, timestamps = self.receiver.acquire()

        if data is not None and len(data) > 0:
            # Add to buffer
            for sample, ts in zip(data, timestamps):
                self.data_buffer.append(sample)
                self.timestamp_buffer.append(ts)

            # Trim buffer to specified duration
            current_time = time.time()
            while (self.timestamp_buffer and 
                   current_time - self.timestamp_buffer[0] > self.buffer_duration):
                self.data_buffer.popleft()
                self.timestamp_buffer.popleft()

            return data, timestamps

        return None, None

    def get_buffer_data(self):
        """Get all buffered data as numpy arrays."""
        if not self.data_buffer:
            return None, None

        data = np.array(list(self.data_buffer))
        timestamps = np.array(list(self.timestamp_buffer))
        return data, timestamps

    def compute_statistics(self):
        """Compute basic statistics on buffered data."""
        data, timestamps = self.get_buffer_data()

        if data is None:
            return None

        stats = {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0),
            'samples': len(data),
            'duration': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
        }

        return stats


def main():
    """Main function for advanced EEG receiver."""
    receiver = EEGReceiver(buffer_duration=5.0)

    try:
        # Connect to stream
        stream = receiver.connect()
        receiver.start()

        print(f"Channel names: {receiver.receiver.ch_names}")
        print("Starting advanced data acquisition...")
        print("Press Ctrl+C to stop\n")

        last_stats_time = time.time()

        while True:
            # Get latest data
            data, timestamps = receiver.get_latest_data()

            if data is not None:
                # Print real-time data
                print(f"Latest sample: {data[-1]}")

                # Print statistics every 2 seconds
                current_time = time.time()
                if current_time - last_stats_time >= 2.0:
                    stats = receiver.compute_statistics()
                    if stats:
                        print(f"\nBuffer Statistics ({stats['samples']} samples, "
                              f"{stats['duration']:.1f}s):")
                        for i, ch_name in enumerate(receiver.receiver.ch_names):
                            print(f"  {ch_name}: "
                                  f"mean={stats['mean'][i]:.2f}, "
                                  f"std={stats['std'][i]:.2f}, "
                                  f"range=[{stats['min'][i]:.2f}, {stats['max'][i]:.2f}]")
                        print("-" * 60)

                    last_stats_time = current_time

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        receiver.stop()


if __name__ == "__main__":
    main()
