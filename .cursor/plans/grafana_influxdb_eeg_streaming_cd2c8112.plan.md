---
name: Grafana InfluxDB EEG Streaming
overview: Implement a modular LSL-to-InfluxDB-to-Grafana pipeline for real-time EEG power spectrum visualization as a scrolling heatmap. The solution will support both raw EEG data (with power spectrum computation) and pre-computed spectra, stream to InfluxDB, and visualize in Grafana.
todos:
  - id: add_scipy_dependency
    content: Add scipy>=1.11.0 to pyproject.toml dependencies for spectrogram computation
    status: pending
  - id: create_influxdb_streamer_module
    content: Create src/phologtolabstreaminglayer/influxdb_eeg_streamer.py with EEGInfluxDBStreamer class supporting raw EEG and pre-computed spectra
    status: pending
  - id: implement_power_spectrum_computation
    content: Implement power spectrum computation using scipy.signal.spectrogram with configurable parameters (nperseg, noverlap)
    status: pending
  - id: implement_influxdb_writer
    content: Implement InfluxDB batch writing with proper data structure (measurement, tags, fields, timestamps)
    status: pending
  - id: implement_lsl_connection
    content: Implement LSL stream discovery and connection with reconnection logic
    status: pending
  - id: create_standalone_script
    content: Create scripts/eeg_to_influxdb.py as entry point with CLI argument parsing and graceful shutdown
    status: pending
  - id: add_configuration_support
    content: Add environment variable and CLI argument support for InfluxDB connection and LSL stream configuration
    status: pending
  - id: create_grafana_documentation
    content: Create docs/grafana_eeg_heatmap_setup.md with InfluxDB data source setup, heatmap panel configuration, and Flux query examples
    status: pending
---

# Grafana + InfluxDB EEG Power Spectrum Streaming

## Architecture Overview

```
LSL Stream (EEG) → Python Module → InfluxDB → Grafana Heatmap
```

The solution consists of:

1. **New module**: `src/phologtolabstreaminglayer/influxdb_eeg_streamer.py` - Core streaming logic
2. **Configuration**: Environment variables or config file for InfluxDB connection and stream selection
3. **Standalone script**: `scripts/eeg_to_influxdb.py` - Entry point for running the streamer
4. **Grafana dashboard**: Documentation/instructions for setting up the heatmap visualization

## Implementation Details

### 1. Core Module: `influxdb_eeg_streamer.py`

**Location**: `src/phologtolabstreaminglayer/influxdb_eeg_streamer.py`

**Key Components**:

- `EEGInfluxDBStreamer` class that:
  - Connects to LSL streams (configurable stream name/type)
  - Supports both raw EEG (computes power spectrum) and pre-computed spectra
  - Computes full frequency spectrum using `scipy.signal.spectrogram` (similar to `stream_viewer` approach)
  - Buffers data for efficient batch writes to InfluxDB
  - Handles reconnection and error recovery

**Power Spectrum Computation** (for raw EEG):

- Use `scipy.signal.spectrogram` with configurable parameters:
  - `nperseg`: FFT window size (power of 2 for performance)
  - `noverlap`: Overlap between segments
  - `scaling='density'`, `mode='psd'`
- Convert to dB: `10 * log10(power + epsilon)`
- Extract full frequency spectrum (all frequencies, not just bands)

**InfluxDB Data Structure**:

- Measurement: `eeg_spectrum`
- Tags: `channel` (channel name), `stream_name` (LSL stream name)
- Fields: `power_<frequency>Hz` (one field per frequency bin) OR `power` with frequency as tag
- Time: LSL timestamp (converted to InfluxDB format)

**Alternative Structure** (more efficient for heatmap):

- Measurement: `eeg_spectrum`
- Tags: `channel`, `stream_name`, `frequency_bin` (frequency value)
- Fields: `power` (single value)
- Time: LSL timestamp

### 2. Configuration

**Environment Variables** (preferred):

- `INFLUXDB_URL`: InfluxDB server URL (default: `http://localhost:8086`)
- `INFLUXDB_TOKEN`: Authentication token
- `INFLUXDB_ORG`: Organization name (default: `phoprivate`)
- `INFLUXDB_BUCKET`: Bucket name (default: `neuroscience`)
- `LSL_STREAM_NAME`: Name of LSL stream to connect to (required)
- `LSL_STREAM_TYPE`: Type of LSL stream (optional, for filtering)
- `SPECTRUM_MODE`: `raw` (compute from EEG) or `precomputed` (already computed)
- `SPECTRUM_NPERSEG`: FFT window size (default: 256)
- `SPECTRUM_NOVERLAP`: Overlap samples (default: 128)
- `BATCH_SIZE`: Number of samples to batch before writing (default: 10)
- `BATCH_INTERVAL_SEC`: Maximum time to wait before flushing batch (default: 1.0)

### 3. Standalone Script

**Location**: `scripts/eeg_to_influxdb.py`

**Functionality**:

- Parse command-line arguments and environment variables
- Initialize `EEGInfluxDBStreamer`
- Run streaming loop with graceful shutdown (Ctrl+C)
- Log status and errors

### 4. Dependencies

**Already in `pyproject.toml`**:

- `influxdb-client>=1.49.0` ✓
- `pylsl>=1.17.6` ✓
- `numpy` (via other deps) ✓

**Need to add**:

- `scipy>=1.11.0` (for `signal.spectrogram`)

### 5. Grafana Dashboard Setup

**Documentation**: Create `docs/grafana_eeg_heatmap_setup.md` with:

- InfluxDB data source configuration
- Heatmap panel setup:
  - X-axis: Time
  - Y-axis: Frequency (from frequency_bin tag or field names)
  - Color: Power (dB)
- Query example using Flux:
  ```flux
  from(bucket: "neuroscience")
    |> range(start: -5m)
    |> filter(fn: (r) => r._measurement == "eeg_spectrum")
    |> filter(fn: (r) => r.channel == "Cz")
    |> pivot(rowKey: ["_time"], columnKey: ["frequency_bin"], valueColumn: "_value")
  ```

- Real-time refresh settings (auto-refresh every 1-5 seconds)
- Threshold configuration for power levels

## Data Flow

1. **LSL Connection**: Streamer discovers and connects to specified LSL stream
2. **Data Acquisition**: Pulls samples from LSL inlet
3. **Processing**:

   - If `raw` mode: Buffer samples, compute spectrogram when buffer is full
   - If `precomputed` mode: Use data directly from stream

4. **InfluxDB Write**: Batch writes using `WritePrecision.NS` for high precision
5. **Grafana Visualization**: Heatmap queries InfluxDB and displays scrolling view

## Error Handling

- LSL stream disconnection: Automatic reconnection with exponential backoff
- InfluxDB connection errors: Retry with backoff, log errors
- Invalid data: Skip samples, log warnings
- Buffer overflow: Drop oldest samples, log warning

## Performance Considerations

- Batch writes to InfluxDB (configurable batch size)
- Efficient spectrogram computation (power-of-2 FFT sizes)
- Optional downsampling for high sample rates
- Thread-safe operations for concurrent access

## Testing

- Unit tests for power spectrum computation
- Integration test with mock LSL stream
- Test both `raw` and `precomputed` modes
- Verify InfluxDB data structure matches Grafana query expectations