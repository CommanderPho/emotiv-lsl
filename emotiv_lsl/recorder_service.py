import logging
from typing import Dict, List, Optional
from datetime import datetime

import pylsl
from pylsl import StreamInfo
from attrs import define, field

from emotiv_lsl.emotiv_base import EmotivBase
from labrecorder import LabRecorder

logger = logging.getLogger(__name__)


@define(slots=False)
class RecorderService:
    """ Records the LSL outlets produced by an EmotivBase delegate to XDF files using LabRecorder.
    
    Usage:
        emotiv = EmotivEpocX()
        recorder = RecorderService(delegate=emotiv)
        recorder.start_recording("my_recording.xdf")
        # ... data is being recorded ...
        recorder.stop_recording()
    """
    delegate: EmotivBase = field(default=None)
    filename: str = field(default=None)
    _recorder: Optional[LabRecorder] = field(default=None, init=False)
    _stream_names: List[str] = field(factory=list, init=False)

    def __attrs_post_init__(self):
        if self.filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"emotiv_recording_{timestamp}.xdf"


    def get_lsl_outlet_stream_names(self) -> List[str]:
        """Returns the expected LSL outlet stream names from the delegate."""
        if self.delegate is None:
            return []
        return ['Epoc X', 'Epoc X Motion', 'Epoc X eQuality']


    def get_lsl_outlets(self) -> Dict[str, StreamInfo]:
        """Returns the LSL outlet stream infos from the delegate."""
        if self.delegate is None:
            return {}
        return {'Epoc X': self.delegate.get_lsl_outlet_eeg_stream_info(), 'Epoc X Motion': self.delegate.get_lsl_outlet_motion_stream_info(), 'Epoc X eQuality': self.delegate.get_lsl_outlet_electrode_quality_stream_info()}


    def find_delegate_streams(self, timeout: float = 5.0) -> List[StreamInfo]:
        """Discover LSL streams that match the delegate's expected outlet names."""
        expected_names = set(self.get_lsl_outlet_stream_names())
        all_streams = pylsl.resolve_streams(timeout)
        matched_streams = [s for s in all_streams if s.name() in expected_names]
        logger.info(f"Found {len(matched_streams)} matching streams out of {len(all_streams)} total streams")
        return matched_streams


    def start_recording(self, filename: Optional[str] = None) -> bool:
        """Start recording the delegate's LSL outlets to an XDF file.
        
        Args:
            filename: Output XDF filename. If None, uses the default filename.
            
        Returns:
            True if recording started successfully, False otherwise.
        """
        if self._recorder is not None and self._recorder.is_recording():
            logger.warning("Recording is already in progress")
            return False

        if filename is not None:
            self.filename = filename

        # Initialize LabRecorder
        self._recorder = LabRecorder(filename=self.filename, enable_remote_control=False)

        # Find streams matching delegate outlets
        streams = self.find_delegate_streams()
        if not streams:
            logger.error("No matching LSL streams found. Make sure the Emotiv device is streaming.")
            self._recorder.cleanup()
            self._recorder = None
            return False

        # Store stream names for reference
        self._stream_names = [s.name() for s in streams]
        logger.info(f"Recording streams: {self._stream_names}")

        # Select and start recording
        stream_uids = [s.uid() for s in streams]
        self._recorder.select_streams_to_record(stream_uids)

        try:
            self._recorder.start_recording()
            logger.info(f"Started recording to {self.filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self._recorder.cleanup()
            self._recorder = None
            return False


    def stop_recording(self) -> bool:
        """Stop the current recording.
        
        Returns:
            True if recording stopped successfully, False otherwise.
        """
        if self._recorder is None:
            logger.warning("No recording in progress")
            return False

        if not self._recorder.is_recording():
            logger.warning("Recording is not currently active")
            self._recorder.cleanup()
            self._recorder = None
            return False

        try:
            self._recorder.stop_recording()
            logger.info(f"Stopped recording. File saved to: {self.filename}")
            return True
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return False
        finally:
            self._recorder.cleanup()
            self._recorder = None


    def is_recording(self) -> bool:
        """Check if recording is currently in progress."""
        return self._recorder is not None and self._recorder.is_recording()


    def get_status(self) -> Dict:
        """Get current recorder status."""
        if self._recorder is None:
            return {'recording': False, 'filename': self.filename, 'streams': []}
        status = self._recorder.get_status()
        status['streams'] = self._stream_names
        return status
