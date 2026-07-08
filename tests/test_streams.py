import unittest
import datetime
from unittest.mock import MagicMock, patch

from emotiv_lsl.emotiv_base import EmotivBase
from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
from emotiv_lsl.emotiv_epoc_plus import EmotivEpocPlus
from emotiv_lsl.recorder_service import RecorderService
import pylsl

class MockEmotivBase(EmotivBase):
    device_name = "Mock Device"
    KeyModel = 1

    def get_crypto_key(self) -> bytearray:
        return bytearray(b'1234')

class TestEmotivStreams(unittest.TestCase):
    def test_lsl_outlet_info_common(self):
        device = MockEmotivBase()
        info = pylsl.StreamInfo('Test', 'EEG', 14, 128, pylsl.cf_float32)

        # Mock desc to verify append_child_value calls
        mock_desc = MagicMock()
        info.desc = MagicMock(return_value=mock_desc)

        # Mock the mixin method that adds time sync stuff
        device.EasyTimeSyncParsingMixin_add_lsl_outlet_info = MagicMock(return_value=info)

        updated_info = device.add_lsl_outlet_info_common(info)

        self.assertEqual(updated_info, info)
        mock_desc.append_child_value.assert_any_call("manufacturer", "emotiv_lsl")
        mock_desc.append_child_value.assert_any_call("version", "0.1.4")

        # Verify the mixin was called
        device.EasyTimeSyncParsingMixin_add_lsl_outlet_info.assert_called_once_with(info=info)

    def test_recorder_service_filename_generation(self):
        service = RecorderService()
        self.assertTrue(service.filename.startswith("emotiv_recording_"))
        self.assertTrue(service.filename.endswith(".xdf"))

    def test_recorder_service_streams_names(self):
        device = MockEmotivBase()
        service = RecorderService(delegate=device)

        expected_names = ['Epoc X', 'Epoc X Motion', 'Epoc X eQuality']
        self.assertEqual(service.get_lsl_outlet_stream_names(), expected_names)

    @patch('emotiv_lsl.recorder_service.LabRecorder')
    def test_recorder_service_start_recording_no_streams(self, MockLabRecorder):
        service = RecorderService()
        service.find_delegate_streams = MagicMock(return_value=[])

        # Should return False if no streams found
        self.assertFalse(service.start_recording())

    @patch('emotiv_lsl.recorder_service.LabRecorder')
    def test_recorder_service_start_recording_success(self, MockLabRecorder):
        service = RecorderService()
        mock_stream = MagicMock()
        mock_stream.name.return_value = "Epoc X"
        mock_stream.uid.return_value = "uid-123"

        service.find_delegate_streams = MagicMock(return_value=[mock_stream])

        # Should return True if streams found
        self.assertTrue(service.start_recording())

        # Verify LabRecorder was initialized and started
        self.assertIsNotNone(service._recorder)
        service._recorder.select_streams_to_record.assert_called_once_with(["uid-123"])
        service._recorder.start_recording.assert_called_once()

    @patch('emotiv_lsl.emotiv_epoc_x.EmotivEpocX.get_hid_device', return_value={'serial_number': '1234567890123456'})
    def test_epoc_x_eeg_stream_info(self, mock_get_hid_device):
        device = EmotivEpocX()
        info = device.get_lsl_outlet_eeg_stream_info()

        self.assertEqual(info.name, 'Epoc X')
        self.assertEqual(info.type, 'EEG')
        self.assertEqual(info.channel_count, len(device.eeg_channel_names))
        self.assertEqual(info.channel_format, pylsl.cf_float32)

    @patch('emotiv_lsl.emotiv_epoc_x.EmotivEpocX.get_hid_device', return_value={'serial_number': '1234567890123456'})
    def test_epoc_x_motion_stream_info(self, mock_get_hid_device):
        device = EmotivEpocX()
        info = device.get_lsl_outlet_motion_stream_info()

        self.assertEqual(info.name, 'Epoc X Motion')
        self.assertEqual(info.type, 'SIGNAL')
        self.assertEqual(info.channel_count, 6)
        self.assertEqual(info.channel_format, pylsl.cf_float32)

    @patch('emotiv_lsl.emotiv_epoc_plus.EmotivEpocPlus.get_hid_device', return_value={'serial_number': '1234567890123456'})
    def test_epoc_plus_eeg_stream_info(self, mock_get_hid_device):
        device = EmotivEpocPlus()
        info = device.get_lsl_outlet_eeg_stream_info()

        self.assertEqual(info.name, 'Epoc+')
        self.assertEqual(info.type, 'EEG')
        self.assertEqual(info.channel_count, 14)
        self.assertEqual(info.channel_format, 'float32')

if __name__ == '__main__':
    unittest.main()
