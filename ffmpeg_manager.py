import subprocess
import os
import platform
import urllib.request
import zipfile
import tarfile

class FFmpegManager:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """Verifica si FFmpeg está instalado y devuelve la ruta."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
            # Extraer la ruta si FFmpeg ya está en PATH
            return 'ffmpeg'  # Asume que ffmpeg está en el PATH
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._install_ffmpeg()

    def _install_ffmpeg(self):
        """Instala FFmpeg si no se encuentra y devuelve la ruta."""
        current_os = self._get_platform()
        if current_os == "windows":
            return self._install_ffmpeg_windows()
        elif current_os == "linux":
            return self._install_ffmpeg_linux()
        else:
            print("Sistema operativo no compatible. Por favor, instale FFmpeg manualmente.")
            return None

    def _install_ffmpeg_windows(self):
        """Instala FFmpeg en Windows y devuelve la ruta a ffmpeg.exe."""
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"  # URL de descarga de FFmpeg
        zip_path = "ffmpeg.zip"
        extract_path = "ffmpeg"

        try:
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            bin_path = os.path.join(os.getcwd(), extract_path, "bin")
            os.environ["PATH"] += os.pathsep + bin_path
            ffmpeg_exe_path = os.path.join(bin_path, "ffmpeg.exe")

            print("FFmpeg instalado exitosamente en", bin_path)
            return ffmpeg_exe_path
        except Exception as e:
            print("Error al instalar FFmpeg:", e)
            return None

    def _install_ffmpeg_linux(self):
        """Instala FFmpeg en Linux y devuelve 'ffmpeg' (asumiendo que estará en el PATH)."""
        try:
            distro = platform.linux_distribution()[0].lower()
            if "ubuntu" in distro or "debian" in distro:
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=True)
            elif "fedora" in distro or "centos" in distro:
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'ffmpeg'], check=True)
            elif "arch" in distro:
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg'], check=True)
            else:
                print("Distribución de Linux no compatible. Por favor, instale FFmpeg manualmente.")
                return None

            print("FFmpeg instalado exitosamente.")
            return 'ffmpeg'  # Asume que ffmpeg está en el PATH
        except Exception as e:
            print("Error al instalar FFmpeg:", e)
            return None

    def _get_platform(self):
        """Devuelve el sistema operativo actual."""
        my_os = platform.system()
        if my_os == "Windows":
            return "windows"
        elif my_os == "Linux":
            return "linux"
        elif my_os == "Darwin":
            return "mac"
        else:
            return f"{my_os} OS"

    def get_ffmpeg_path(self):
        """Devuelve la ruta a ffmpeg.exe."""
        return self.ffmpeg_path

