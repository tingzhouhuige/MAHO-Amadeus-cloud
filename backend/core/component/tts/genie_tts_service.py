import os
import logging
import asyncio
import io
import tempfile
import struct
import wave
from pathlib import Path


class Client:
    """
    Genie TTS ???????- ????????? TTS ?????????
    ?????ONNX ???????????????????
    """
    
    def __init__(self,
                 character_name: str = "maho",
                 onnx_model_dir: str = "",
                 genie_data_dir: str = "",
                 language: str = "ja",
                 reference_audio_path: str = "",
                 reference_audio_text: str = "",
                 auto_load: bool = True):
        """
        ???????Genie TTS ???????
        ???????????????????????????????????????????????????????????????????????enie-TTS??????????????
        
        :param character_name: ?????????
        :param onnx_model_dir: ONNX ???????????????????????????????????
        :param genie_data_dir: GenieData ????????????????????????????????????
        :param language: ????????????a/zh/en??
        :param reference_audio_path: ??????????????
        :param reference_audio_text: ?????????????????????
        :param auto_load: ???????????????????
        """
        self.character_name = character_name
        self.language = language
        self.reference_audio_path = reference_audio_path
        self.reference_audio_text = reference_audio_text
        self.is_loaded = False
        
        # ??????????????????MAHO ???????        # __file__ = backend/core/component/tts/genie_tts_service.py
        # parents: 0=tts, 1=component, 2=core, 3=backend, 4=MAHO
        project_root = Path(__file__).resolve().parents[4]
        self.temp_dir = project_root / "backend" / "models" / ".tmp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # ?????ONNX ???????????????
        if onnx_model_dir:
            model_path = Path(onnx_model_dir)
            if not model_path.is_absolute():
                model_path = project_root / onnx_model_dir
            self.onnx_model_dir = str(model_path)
        else:
            # ????????????ackend/models/TTS-maho
            self.onnx_model_dir = str(project_root / "backend" / "models" / "TTS-maho")

        if not Path(self.onnx_model_dir).is_dir():
            raise FileNotFoundError(f"Genie TTS ????????????????? {self.onnx_model_dir}")
        
        # ?????GenieData ?????????
        if genie_data_dir:
            genie_path = Path(genie_data_dir)
            if not genie_path.is_absolute():
                genie_path = project_root / genie_data_dir
            genie_data_dir = str(genie_path)
        else:
            # ????????????ackend/models/GenieData
            genie_data_dir = str(project_root / "backend" / "models" / "GenieData")

        if not Path(genie_data_dir).is_dir():
            raise FileNotFoundError(f"GenieData ??????????? {genie_data_dir}")
        
        # ?????GENIE_DATA_DIR ????????????????????????genie_tts ???????
        os.environ["GENIE_DATA_DIR"] = genie_data_dir
        logging.info(f"GENIE_DATA_DIR ?????????: {genie_data_dir}")
        
        # ?????genie_tts?????????????????????????
        import genie_tts as genie
        self.genie = genie
        
        # ?????????????????????????????????
        if auto_load:
            self._load_model()
    
    def _load_model(self):
        """Load the Genie TTS model."""
        try:
            # ???????????????????
            self.genie.load_character(
                character_name=self.character_name,
                onnx_model_dir=self.onnx_model_dir,
                language=self.language,
            )
            logging.info(f"?????????????? {self.character_name}")
            
            # ??????????????????????????????????????
            if self.reference_audio_path and self.reference_audio_text:
                self._set_reference_audio(
                    self.reference_audio_path, 
                    self.reference_audio_text
                )
            
            self.is_loaded = True
            
        except Exception as e:
            logging.error(f"?????Genie TTS ??????????: {e}")
            raise
    
    def _set_reference_audio(self, audio_path: str, audio_text: str):
        """Set the reference audio."""
        try:
            # ??????????????
            ref_path = Path(audio_path)
            if not ref_path.is_absolute():
                project_root = Path(__file__).resolve().parents[4]
                ref_path = project_root / audio_path

            if not ref_path.is_file():
                raise FileNotFoundError(f"????????????????? {ref_path}")
            
            self.genie.set_reference_audio(
                character_name=self.character_name,
                audio_path=str(ref_path),
                audio_text=audio_text,
                language=self.language,
            )
            logging.info(f"????????????????? {ref_path}")
            
        except Exception as e:
            logging.error(f"??????????????????? {e}")
            raise
    
    def generate_audio(self, 
                      text: str, 
                      reference_audio_path: str = None,
                      reference_audio_text: str = None,
                      **kwargs) -> bytes | None:
        """
        ??????????????
        
        :param text: ??????????????
        :param reference_audio_path: ?????????????????????????????
        :param reference_audio_text: ?????????????????????????????
        :return: ??????????????????WAV ???????
        """
        if not self.is_loaded:
            logging.error("Genie TTS model is not loaded")
            return None
        
        try:
            # ???????????????????????????????????????????
            if reference_audio_path and reference_audio_text:
                self._set_reference_audio(reference_audio_path, reference_audio_text)

            audio_data = self._generate_audio_file(text)
            if not audio_data or len(audio_data) <= 16000:
                logging.warning("Genie TTS file mode returned tiny audio: %s bytes", len(audio_data) if audio_data else 0)
                self._reset_runtime()
                audio_data = asyncio.run(self._generate_audio_bytes(text))
            if not audio_data or len(audio_data) <= 16000:
                logging.warning("Genie TTS async fallback returned tiny audio: %s bytes", len(audio_data) if audio_data else 0)
                self._reset_runtime()
                audio_data = self._generate_audio_file(text)

            if audio_data and len(audio_data) > 16000:
                logging.info(f"???????????????????? {text[:50]}...")
                return audio_data

            logging.warning("Genie TTS returned no audio data")
            return None
                    
        except Exception as e:
            logging.error(f"TTS ?????????: {e}")
            return None

    def _reset_runtime(self):
        try:
            self.genie.stop()
        except Exception:
            pass

    async def _generate_audio_bytes(self, text: str) -> bytes | None:
        chunks = []
        async for chunk in self.genie.tts_async(
            character_name=self.character_name,
            text=text,
            play=False,
            split_sentence=False,
            save_path=None,
        ):
            if chunk:
                chunks.append(chunk)

        if not chunks:
            return None

        return self._pcm_to_wav(b"".join(chunks))

    def _generate_audio_file(self, text: str) -> bytes | None:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=self.temp_dir) as tmp_file:
                tmp_path = tmp_file.name

            self.genie.tts(
                character_name=self.character_name,
                text=text,
                play=False,
                split_sentence=False,
                save_path=tmp_path,
            )
            if not tmp_path or not Path(tmp_path).is_file():
                return None
            data = Path(tmp_path).read_bytes()
            return self._smooth_wav_edges(data)
        finally:
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception:
                    pass

    async def stream_audio(self, text: str):
        async for chunk in self.genie.tts_async(
            character_name=self.character_name,
            text=text,
            play=False,
            split_sentence=True,
            save_path=None,
        ):
            if chunk:
                yield self._pcm_to_wav(chunk)

    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
        pcm_data = self._smooth_pcm_edges(pcm_data)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(32000)
            wav_file.writeframes(pcm_data)
        return wav_buffer.getvalue()

    def _smooth_pcm_edges(self, pcm_data: bytes) -> bytes:
        sample_width = 2
        frame_count = len(pcm_data) // sample_width
        if frame_count < 64:
            return pcm_data

        fade_in_frames = min(320, frame_count // 8)
        fade_out_frames = min(3200, frame_count // 4)
        frames = bytearray(pcm_data)

        for i in range(fade_in_frames):
            start = i * sample_width
            factor = i / fade_in_frames
            sample = struct.unpack_from("<h", frames, start)[0]
            struct.pack_into("<h", frames, start, int(sample * factor))

        for offset in range(fade_out_frames):
            i = frame_count - fade_out_frames + offset
            start = i * sample_width
            factor = 1 - (offset / fade_out_frames)
            sample = struct.unpack_from("<h", frames, start)[0]
            struct.pack_into("<h", frames, start, int(sample * factor))

        return bytes(frames)

    def _smooth_wav_edges(self, wav_data: bytes) -> bytes:
        try:
            with wave.open(io.BytesIO(wav_data), "rb") as wav_in:
                channels = wav_in.getnchannels()
                sample_width = wav_in.getsampwidth()
                frame_rate = wav_in.getframerate()
                pcm_data = wav_in.readframes(wav_in.getnframes())

            if channels == 1 and sample_width == 2:
                pcm_data = self._smooth_pcm_edges(pcm_data)
            else:
                return wav_data

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_out:
                wav_out.setnchannels(channels)
                wav_out.setsampwidth(sample_width)
                wav_out.setframerate(frame_rate)
                wav_out.writeframes(pcm_data)
            return wav_buffer.getvalue()
        except Exception:
            return wav_data
    
    def set_reference(self, audio_path: str, audio_text: str):
        """
        ??????????????
        
        :param audio_path: ??????????????
        :param audio_text: ?????????????????????
        """
        self.reference_audio_path = audio_path
        self.reference_audio_text = audio_text
        if self.is_loaded:
            self._set_reference_audio(audio_path, audio_text)
