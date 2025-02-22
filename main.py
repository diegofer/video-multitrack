import os
import torchaudio, torch
import soundfile as sf
from moviepy import VideoFileClip
from demucs.apply import apply_model
from demucs.pretrained import get_model
from pathlib import Path
import imageio_ffmpeg as ffmpeg
import subprocess

# Ruta al archivo MP4 de entrada
input_mp4 = "El Dios De Lo Extraordinario - Tercer Cielo.mp4"
output_wav = "extracted_audio.wav"
output_folder = "separated"

# Extraer audio con MoviePy
print("Extrayendo audio del archivo MP4...")
video = VideoFileClip(input_mp4)
audio = video.audio
audio.write_audiofile(output_wav, codec="pcm_s16le", fps=44100)

# Cargar el modelo de Demucs (htdemucs_6s para 6 stems)
print("Cargando modelo Demucs...")
model = get_model("htdemucs_6s")  # Puedes cambiarlo si necesitas otro modelo

# Crear carpeta de salida
Path(output_folder).mkdir(exist_ok=True)

# Cargar el audio
waveform, sample_rate = torchaudio.load(output_wav)

# Si el audio es mono, convertirlo a estéreo duplicando el canal
if waveform.shape[0] == 1:
    waveform = waveform.repeat(2, 1)  # Convierte de (1, N) a (2, N)

# Agregar batch dimension (1, canales, muestras)
waveform = waveform.unsqueeze(0)

# Aplicar Demucs para separar pistas
print("Separando pistas...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")
separated = apply_model(model, waveform, split=True, overlap=0.25, device=device)


# Nombres de las pistas según el modelo
stem_names = model.sources  # ["drums", "bass", "other", "vocals", "piano", "guitar"]

separated = separated.squeeze(0)  # Ahora tiene forma (6, 2, N)
# Definir nombres de los stems (según HTDemucs 6S)
stem_names = ["drums", "bass", "other", "vocals", "piano", "guitar"]
sample_rate = 44100  # Ajusta esto según tu modelo

# Guardar cada pista
for i, stem in enumerate(stem_names):
    output_path = f"{stem}.wav"  # Guardar en formato WAV
    audio_data = separated[i].cpu().numpy().T  # Convertir a numpy y transponer a (samples, channels)
    
    sf.write(output_path, audio_data, sample_rate)


    print(f"Guardado: {output_path}")

def get_ffmpeg_path():
    return ffmpeg.get_ffmpeg_version()  # Descarga FFmpeg si no está presente

def convert_wav_to_ogg(input_wav, output_ogg):
    ffmpeg_path = get_ffmpeg_path()
    cmd = [ffmpeg_path, "-i", input_wav, "-c:a", "libvorbis", output_ogg, "-y"]
    subprocess.run(cmd, check=True)

# Uso
convert_wav_to_ogg("input.wav", "output.ogg")






print("Proceso finalizado.")
