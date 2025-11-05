import logging
from typing import Dict, List, Tuple, Optional, Callable, Union, Any

import pylsl
from pylsl import StreamInfo
from attrs import define, field, Factory

from emotiv_lsl.emotiv_base import EmotivBase


class RecorderService:
	""" Aims to record the outlets produced by an EmotivBase class as inlets, which are saved to file.
	"""
	@property
	def delegate(self) -> EmotivBase:
		"""The delegate property."""
		return self._delegate
	@delegate.setter
	def delegate(self, value):
		self._delegate = value


	def get_lsl_outlets(self) -> Dict[str, StreamInfo]:
		return {
			'Epoc X': self.delegate.get_lsl_outlet_eeg_stream_info(),
			'Epoc X Motion': self.delegate.get_lsl_outlet_motion_stream_info(),
			'Epoc X eQuality': self.delegate.get_lsl_outlet_electrode_quality_stream_info(),
		}
