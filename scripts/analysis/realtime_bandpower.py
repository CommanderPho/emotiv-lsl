import time
import numpy as np
import pylsl
from scipy.signal import welch
from scipy.integrate import simps

# --- Analysis Parameters ---

# Length of the analysis window in seconds
WINDOW_LENGTH = 2.0

# Time step between consecutive windows in seconds
WINDOW_STEP = 0.5

# Frequency bands of interest (in Hz)
BANDS = {
    'Delta': (1, 4),
    'Theta': (4, 8),
    'Alpha': (8, 12),
    'Beta': (12, 30),
    'Gamma': (30, 45)
}

def compute_band_powers(data, sfreq):
    """
    Computes the power in specified frequency bands from EEG data.

    Args:
        data (np.ndarray): EEG data of shape (n_samples, n_channels).
        sfreq (float): The sampling frequency of the data.

    Returns:
        dict: A dictionary where keys are band names and values are the
              band powers for each channel.
    """
    # Use Welch's method to compute the Power Spectral Density (PSD)
    # nperseg is the length of each segment, here we use the full window
    freqs, psd = welch(data, sfreq, nperseg=data.shape[0], axis=0)

    # Transpose PSD to have shape (n_channels, n_freqs) for easier iteration
    psd = psd.T

    band_powers = {}
    for band, (low, high) in BANDS.items():
        # Find the indices of frequencies that fall within the band
        freq_indices = np.where((freqs >= low) & (freqs <= high))[0]

        # Compute the absolute power by integrating the PSD over the band
        # using Simpson's rule for a more accurate integral
        power_per_channel = simps(psd[:, freq_indices], freqs[freq_indices], axis=1)
        band_powers[band] = power_per_channel

    return band_powers


def main():
    """
    Connects to an LSL stream, receives data, and computes band powers in real-time.
    """
    print("Looking for an EEG stream...")
    streams = pylsl.resolve_stream('type', 'EEG')
    if not streams:
        print("No EEG stream found. Make sure a stream is running.")
        return

    # Create a new inlet to read from the stream
    inlet = pylsl.StreamInlet(streams[0])

    # Get stream information
    info = inlet.info()
    sfreq = info.nominal_srate()
    n_channels = info.channel_count()
    ch_names_info = info.desc().child("channels").child("channel")
    ch_names = [ch_names_info.child_value("label")]
    for i in range(1, n_channels):
        ch_names_info = ch_names_info.next_sibling()
        ch_names.append(ch_names_info.child_value("label"))


    print(f"Connected to '{info.name()}' stream.")
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Number of channels: {n_channels}")
    print(f"Channel names: {ch_names}")

    # Calculate window and step sizes in samples
    window_samples = int(sfreq * WINDOW_LENGTH)
    step_samples = int(sfreq * WINDOW_STEP)

    # Initialize a buffer to hold the data for one window
    buffer = np.zeros((window_samples, n_channels))
    samples_in_buffer = 0

    print("\nStarting real-time bandpower analysis... Press Ctrl+C to stop.")

    try:
        while True:
            # Pull a chunk of data. This is more efficient than pull_sample().
            # The timeout is set to slightly more than the window step to ensure
            # we have data to process in each iteration.
            samples, _ = inlet.pull_chunk(timeout=WINDOW_STEP * 2, max_samples=step_samples)

            if samples:
                samples = np.array(samples)
                n_new_samples = samples.shape[0]

                # Update the buffer by removing the oldest samples and appending the new ones
                buffer = np.roll(buffer, -n_new_samples, axis=0)
                buffer[-n_new_samples:, :] = samples

                # Keep track of total samples, but don't exceed the window size
                samples_in_buffer = min(samples_in_buffer + n_new_samples, window_samples)

                # Only compute bandpower if the buffer is full
                if samples_in_buffer >= window_samples:
                    # Compute band powers for the current window
                    band_powers = compute_band_powers(buffer, sfreq)

                    # --- Print the results ---
                    print("\n" + "="*30)
                    print(f"Timestamp: {time.time():.2f}")
                    # Example: Print the Alpha power for the first channel
                    # You can customize this to display the information you need
                    alpha_power_ch1 = band_powers['Alpha'][0]
                    print(f"Alpha Power (Ch1 - {ch_names[0]}): {alpha_power_ch1:.4f} uV^2/Hz")

                    beta_power_ch1 = band_powers['Beta'][0]
                    print(f"Beta Power (Ch1 - {ch_names[0]}): {beta_power_ch1:.4f} uV^2/Hz")
                    print("="*30)


    except KeyboardInterrupt:
        print("\nAnalysis stopped by user.")
    finally:
        inlet.close_stream()
        print("Stream closed.")


if __name__ == '__main__':
    main()
