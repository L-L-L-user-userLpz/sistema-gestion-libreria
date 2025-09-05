@echo off
chcp 65001 > nul
echo.
echo ========================================
echo    INSTALACIÓN SISTEMA DE GESTIÓN
echo ========================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH.
    echo.
    echo 📥 Por favor, instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo 💡 Durante la instalación, asegúrate de marcar:
    echo    "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Mostrar versión de Python
echo 🔍 Versión de Python:
python --version

:: Verificar e instalar dependencias
echo.
echo ========================================
echo    VERIFICANDO DEPENDENCIAS
echo ========================================
echo.

python check_deps.py

if errorlevel 1 (
    echo.
    echo ❌ Error en la verificación de dependencias.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    CREANDO ESTRUCTURA DE DIRECTORIOS
echo ========================================
echo.

:: Crear directorios necesarios
if not exist facturas mkdir facturas
if not exist backups mkdir backups
if not exist icons mkdir icons

echo ✅ Directorios creados: facturas/, backups/, icons/

echo.
echo ========================================
echo    INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo ✅ Sistema instalado correctamente!
echo.
echo 🚀 Para ejecutar el sistema:
echo    python sistema.py
echo.
echo 📖 Consulta manual_usuario.md para más información
echo.
pause