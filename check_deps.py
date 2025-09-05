import sys
import subprocess
import importlib

def check_python_version():
    """Verifica que Python tenga la versión correcta"""
    print("🔍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        print("✅ Se requiere Python 3.8 o superior")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
        return True

def check_dependency(name, pip_name=None):
    """Verifica una dependencia específica"""
    if pip_name is None:
        pip_name = name
    
    print(f"🔍 Verificando {name}...")
    try:
        importlib.import_module(name if name != "opencv-python" else "cv2")
        print(f"✅ {name} - OK")
        return True
    except ImportError:
        print(f"❌ {name} no está instalado")
        return False

def install_dependency(name):
    """Instala una dependencia"""
    print(f"📦 Instalando {name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", name])
        print(f"✅ {name} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error al instalar {name}")
        return False

def main():
    print("=" * 50)
    print("VERIFICACIÓN DE DEPENDENCIAS DEL SISTEMA")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        return False
        
    # Lista de dependencias a verificar
    dependencies = [
        ("ttkthemes", "ttkthemes"),
        ("reportlab", "reportlab"),
        ("matplotlib", "matplotlib"),
        ("opencv-python", "opencv-python"),
        # ("pyzbar", "pyzbar"),
        ("Pillow", "Pillow"),
        ("numpy", "numpy"),
        ("schedule", "schedule")
    ]
    
    missing_deps = []
    
    # Verificar cada dependencia
    for name, pip_name in dependencies:
        if not check_dependency(name, pip_name):
            missing_deps.append(pip_name)
    
    # Instalar dependencias faltantes
    if missing_deps:
        print("\n" + "=" * 50)
        print("INSTALANDO DEPENDENCIAS FALTANTES")
        print("=" * 50)
        
        for dep in missing_deps:
            if not install_dependency(dep):
                print(f"❌ No se pudo completar la instalación debido a errores")
                return False
    
    print("\n" + "=" * 50)
    print("✅ TODAS LAS DEPENDENCIAS ESTÁN INSTALADAS CORRECTAMENTE")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ La verificación encontró problemas que deben resolverse manualmente")
        sys.exit(1)
    else:
        print("\n🎉 ¡El sistema está listo para usar!")
        print("Ejecuta: python sistema.py")