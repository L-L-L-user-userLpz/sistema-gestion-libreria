# Script de Instalación para Linux
#!/bin/bash
echo
echo "========================================"
echo "   INSTALACIÓN SISTEMA DE GESTIÓN"
echo "========================================"
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado."
    echo
    echo "📥 Instala Python3 con:"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    echo
    exit 1
fi

# Mostrar versión de Python
echo "🔍 Versión de Python:"
python3 --version

# Verificar e instalar dependencias
echo
echo "========================================"
echo "   VERIFICANDO DEPENDENCIAS"
echo "========================================"
echo

python3 check_deps.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Error en la verificación de dependencias."
    echo
    exit 1
fi

echo
echo "========================================"
echo "   CREANDO ESTRUCTURA DE DIRECTORIOS"
echo "========================================"
echo

# Crear directorios necesarios
mkdir -p facturas backups icons

echo "✅ Directorios creados: facturas/, backups/, icons/"

echo
echo "========================================"
echo "   INSTALACIÓN COMPLETADA"
echo "========================================"
echo
echo "✅ Sistema instalado correctamente!"
echo
echo "🚀 Para ejecutar el sistema:"
echo "   python3 sistema.py"
echo
echo "📖 Consulta manual_usuario.md para más información"
echo