#!/bin/bash
# ===============================================
# 📦 Script de instalación para entorno ETL
# Ubuntu (para UTM en Mac M3)
# ===============================================

set -e  # Detiene el script si hay algún error

echo "🚀 Iniciando instalación del entorno ETL..."

# 1️. Actualizar el sistema
echo "🧩 Actualizando paquetes..."
sudo apt update -y && sudo apt upgrade -y


# 2️. Instalar dependencias base
echo "📦 Instalando utilidades básicas..."
sudo apt install -y curl wget git build-essential software-properties-common

# 3️. Instalar Python 3 + pip + venv
echo "🐍 Instalando Python y pip..."
sudo apt install -y python3 python3-pip python3-venv

# 4️. Crear entorno virtual y activarlo
echo "🔧 Creando entorno virtual..."
mkdir -p ~/etl_project
cd ~/etl_project
python3 -m venv venv
source venv/bin/activate

# 5️. Instalar librerías Python necesarias
echo "📚 Instalando librerías Python..."
pip install --upgrade pip
pip install requests psycopg2-binary

# 6️. Instalar PostgreSQL y extensión UUID
echo "🐘 Instalando PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# 7️. Configurar PostgreSQL
echo "⚙️ Configurando PostgreSQL..."
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Crear usuario y base de datos (solo si no existen)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='postgres';" | grep -q 1 || sudo -u postgres createuser postgres
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='user_management';" | grep -q 1 || sudo -u postgres createdb user_management -O postgres

# Cambiar contraseña del usuario postgres
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'tu_password';"

# Activar extensión de UUID
sudo -u postgres psql -d user_management -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# 8️. Verificar instalación
echo "🔍 Verificando instalación..."
psql --version
python3 --version
pip list | grep psycopg2

# 9️. Mensaje final
echo "✅ Instalación completada con éxito."
echo "-------------------------------------"
echo "📂 Proyecto ETL en: ~/etl_project"
echo "💾 Base de datos: user_management"
echo "👤 Usuario PostgreSQL: postgres"
echo "🔑 Password: tu_password"
echo "-------------------------------------"
echo "Ahora puedes ejecutar tu script ETL con:"
echo "  source ~/etl_project/venv/bin/activate"
echo "  python3 tu_script_etl.py"
