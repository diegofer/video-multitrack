from PySide6.QtCore import QThread, Signal
import os
import torchaudio
import torch
import soundfile as sf
from demucs.apply import apply_model
from demucs.pretrained import get_model
from pathlib import Path
import subprocess
import unicodedata
from ffmpeg_manager import FFmpegManager

class TracksExtractThread(QThread):
    result = Signal(list)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        self.process_video(self.video_path)

    def process_video(self, input_mp4_path):      
        
        def delete_wav_files(folder):
            for file in os.listdir(folder):
                if file.endswith(".wav"):
                    os.remove(os.path.join(folder, file))
                    print(f"Eliminado: {file}")
        
        def normalize_filename(filename):
            nfkd_form = unicodedata.normalize('NFKD', filename)
            return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper()
        
        output_folder_name = normalize_filename(os.path.splitext(input_mp4_path)[0])
        output_folder = os.path.join(output_folder_name)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        print("OUTPUT FOLDER", output_folder)
        output_wav = os.path.join(output_folder, "extracted_audio.wav")
        
        print("Extrayendo audio del archivo MP4...")
        ffmpeg_manager = FFmpegManager()
        ffmpeg_path = ffmpeg_manager.get_ffmpeg_path()
        cmd = [ffmpeg_path, "-i", input_mp4_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", output_wav, "-y"]
        subprocess.run(cmd, check=True)
        
        print("Cargando modelo Demucs...")
        model = get_model("htdemucs_6s")
        
        waveform, sample_rate = torchaudio.load(output_wav)
        
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        
        waveform = waveform.unsqueeze(0)
        
        print("Separando pistas...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Usando dispositivo: {device}")
        separated = apply_model(model, waveform, split=True, overlap=0.25, device=device, segment=7.8)
        
        stem_names = model.sources
        separated = separated.squeeze(0)
        stem_names = ["drums", "bass", "other", "vocals", "piano", "guitar"]
        sample_rate = 44100
        
        for i, stem in enumerate(stem_names):
            output_wav_path = os.path.join(output_folder, f"{stem}.wav")
            output_ogg_path = os.path.join(output_folder, f"{stem}.ogg")
            audio_data = separated[i].cpu().numpy().T
            
            sf.write(output_wav_path, audio_data, sample_rate)
            print(f"Guardado: {output_wav_path}")
            
            cmd = [ffmpeg_path, "-i", output_wav_path, "-c:a", "libvorbis", output_ogg_path, "-y"]
            subprocess.run(cmd, check=True)
            print(f"Convertido a OGG: {output_ogg_path}")
        
        output_extracted_ogg = os.path.join(output_folder, "full.ogg")
        cmd = [ffmpeg_path, "-i", output_wav, "-c:a", "libvorbis", "-q:a", "10", output_extracted_ogg, "-y"]
        subprocess.run(cmd, check=True)
        print(f"Convertido a OGG: {output_extracted_ogg}")
        
        delete_wav_files(output_folder)
        
        self.result.emit(["Proceso finalizado."])
        self.quit()
