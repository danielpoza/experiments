#!/usr/bin/env python3
"""
Script de verificación de configuración MCP

Este script ayuda a verificar que el servidor MCP está correctamente
configurado y puede comunicarse con GitHub Copilot Chat.
"""

import subprocess
import sys
import time
import json

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...\n")
    
    try:
        import fastapi
        print("✅ FastAPI instalado")
    except ImportError:
        print("❌ FastAPI no encontrado")
        return False
    
    try:
        import mcp
        print("✅ MCP instalado")
    except ImportError:
        print("❌ MCP no encontrado")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic instalado")
    except ImportError:
        print("❌ Pydantic no encontrado")
        return False
    
    print()
    return True

def test_fastapi_server():
    """Prueba que el servidor FastAPI arranca correctamente"""
    print("🚀 Probando servidor FastAPI...\n")
    
    try:
        proc = subprocess.Popen(
            ["python", "-m", "app.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que el servidor arranque
        time.sleep(3)
        
        # Intentar hacer una petición
        import httpx
        try:
            response = httpx.get("http://localhost:8080/", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor FastAPI funcionando correctamente")
                print(f"   Respuesta: {response.json()}\n")
                result = True
            else:
                print(f"❌ Servidor respondió con código {response.status_code}\n")
                result = False
        except Exception as e:
            print(f"❌ No se pudo conectar al servidor: {e}\n")
            result = False
        finally:
            proc.terminate()
            proc.wait(timeout=5)
        
        return result
        
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}\n")
        return False

def test_mcp_mode():
    """Prueba que el modo MCP se ejecuta sin errores"""
    print("🔧 Probando modo MCP...\n")
    
    try:
        proc = subprocess.Popen(
            ["python", "-m", "app.main", "--mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un poco
        time.sleep(2)
        
        # Terminar el proceso
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        
        # Verificar que no hay errores de sintaxis o importación
        if "Error" not in stderr and "Traceback" not in stderr:
            print("✅ Modo MCP se ejecuta correctamente")
            print("   (El servidor espera comunicación MCP vía stdin/stdout)\n")
            return True
        else:
            print("❌ Errores encontrados en modo MCP:")
            print(stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error al probar modo MCP: {e}\n")
        return False

def print_next_steps():
    """Imprime los siguientes pasos para el usuario"""
    print("\n" + "="*60)
    print("📋 SIGUIENTES PASOS")
    print("="*60 + "\n")
    
    print("1. Configurar el servidor MCP en GitHub Copilot:")
    print("   Edita tu archivo de configuración MCP:")
    print("   - macOS/Linux: ~/.config/mcp/servers.json")
    print("   - Windows: %APPDATA%\\mcp\\servers.json\n")
    
    print("2. Añade la configuración del servidor:")
    print('   {')
    print('     "mcpServers": {')
    print('       "foscam-notifier": {')
    print('         "command": "python",')
    print('         "args": ["-m", "app.main", "--mcp"],')
    print('         "cwd": "/ruta/absoluta/a/services/service3-notifier"')
    print('       }')
    print('     }')
    print('   }\n')
    
    print("3. Reinicia tu IDE o GitHub Copilot Chat\n")
    
    print("4. Prueba la integración desde Copilot Chat:")
    print('   "Muéstrame las últimas imágenes de las cámaras"\n')
    
    print("📚 Más información:")
    print("   - docs/copilot-chat-integration.md")
    print("   - docs/copilot-usage-examples.md\n")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN MCP")
    print("="*60 + "\n")
    
    all_passed = True
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Por favor instala las dependencias:")
        print("   pip install -r requirements.txt\n")
        all_passed = False
        sys.exit(1)
    
    # Probar servidor FastAPI
    if not test_fastapi_server():
        all_passed = False
    
    # Probar modo MCP
    if not test_mcp_mode():
        all_passed = False
    
    # Resumen
    print("="*60)
    if all_passed:
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("="*60)
        print_next_steps()
        sys.exit(0)
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("="*60)
        print("\nPor favor corrige los errores antes de continuar.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
