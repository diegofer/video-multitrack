import os
import torchaudio, torch
import soundfile as sf
from demucs.apply import apply_model
from demucs.pretrained import get_model
from pathlib import Path
import subprocess
import imageio_ffmpeg as ffmpeg

# Ruta al archivo MP4 de entrada
input_mp4 = "El Dios De Lo Extraordinario - Tercer Cielo.mp4"
output_folder = "separated"
output_wav = os.path.join(output_folder, "full.wav")

# Función para obtener la ruta de ffmpeg
def get_ffmpeg_path():
    return "ffmpeg" #ffmpeg.get_ffmpeg_version() # Descarga FFmpeg si no está presente

# Función para eliminar archivos WAV
def delete_wav_files(folder):
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            os.remove(os.path.join(folder, file))
            print(f"Eliminado: {file}")

# Crear carpeta de salida
Path(output_folder).mkdir(exist_ok=True)

# Extraer audio con ffmpeg
print("Extrayendo audio del archivo MP4...")
ffmpeg_path = get_ffmpeg_path()
cmd = [ffmpeg_path, "-i", input_mp4, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", output_wav]
subprocess.run(cmd, check=True)

# Cargar el modelo de Demucs (htdemucs_6s para 6 stems)
print("Cargando modelo Demucs...")
model = get_model("htdemucs_6s")  # Puedes cambiarlo si necesitas otro modelo


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
separated = apply_model(model, waveform, split=True, overlap=0.25, device=device, segment=7.8)

# Nombres de las pistas según el modelo
stem_names = model.sources  # ["drums", "bass", "other", "vocals", "piano", "guitar"]

separated = separated.squeeze(0)  # Ahora tiene forma (6, 2, N)
# Definir nombres de los stems (según HTDemucs 6S)
#stem_names = ["drums", "bass", "other", "vocals", "piano", "guitar"]
sample_rate = 44100  # Ajusta esto según tu modelo

# Guardar cada pista en formato WAV y luego convertir a OGG
for i, stem in enumerate(stem_names):
    output_wav_path = os.path.join(output_folder, f"{stem}.wav")
    output_ogg_path = os.path.join(output_folder, f"{stem}.ogg")
    audio_data = separated[i].cpu().numpy().T  # Convertir a numpy y transponer a (samples, channels)
    
    # Guardar en formato WAV
    sf.write(output_wav_path, audio_data, sample_rate)
    print(f"Guardado: {output_wav_path}")

    # Convertir a formato OGG usando ffmpeg
    cmd = [ffmpeg_path, "-i", output_wav_path, "-c:a", "libvorbis", output_ogg_path, "-y"]
    subprocess.run(cmd, check=True)
    print(f"Convertido a OGG: {output_ogg_path}")



# Convertir el audio extraído del video a OGG
output_extracted_ogg = os.path.join(output_folder, "full.ogg")
cmd = [ffmpeg_path, "-i", output_wav, "-c:a", "libvorbis", output_extracted_ogg, "-y"]
subprocess.run(cmd, check=True)
print(f"Convertido a OGG: {output_extracted_ogg}")

# Eliminar archivos WAV
delete_wav_files(output_folder)

print("Proceso finalizado.")
