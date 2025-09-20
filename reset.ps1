# Reset.ps1 - Reset Django DB, migrations, superuser & roles for SIS

Write-Host "🚀 Resetting Django project..." -ForegroundColor Cyan

# Delete database
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "Deleted db.sqlite3" -ForegroundColor Yellow
}

# Delete migration files except __init__.py
Get-ChildItem -Recurse -Filter "migrations" | ForEach-Object {
    Get-ChildItem $_.FullName -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
    Write-Host "Deleted migration files in $($_.FullName)" -ForegroundColor Yellow
}

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
$pythonCommand = @"
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

"@

python -c $pythonCommand
