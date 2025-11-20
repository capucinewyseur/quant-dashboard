#!/bin/bash
# Automatic cron job installer for daily reports
# Configures cron job to generate report daily at 20:00

echo "=========================================="
echo "Installation du cron job pour les rapports quotidiens"
echo "=========================================="

# Get absolute project path
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Dossier du projet: $PROJECT_DIR"

# Find Python executable
if command -v python3 &> /dev/null; then
    PYTHON_CMD=$(which python3)
elif command -v python &> /dev/null; then
    PYTHON_CMD=$(which python)
else
    echo "Erreur: Python n'est pas trouvé"
    exit 1
fi

echo "Python trouvé: $PYTHON_CMD"

# Report generation script path
REPORT_SCRIPT="$PROJECT_DIR/cron/generate_report.py"
LOG_FILE="$PROJECT_DIR/cron/cron.log"

echo "Script de rapport: $REPORT_SCRIPT"
echo "Fichier de log: $LOG_FILE"

# Verify script exists
if [ ! -f "$REPORT_SCRIPT" ]; then
    echo "Erreur: Le script generate_report.py n'existe pas"
    exit 1
fi

# Create reports directory if missing
mkdir -p "$PROJECT_DIR/reports"
echo "Dossier reports créé/vérifié"

# Cron line to add (20:00 daily)
CRON_LINE="0 20 * * * cd $PROJECT_DIR && $PYTHON_CMD $REPORT_SCRIPT >> $LOG_FILE 2>&1"

echo ""
echo "Configuration du cron job (exécution tous les jours à 20h)..."
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$REPORT_SCRIPT"; then
    echo "Le cron job existe déjà. Voulez-vous le remplacer? (o/n)"
    read -r response
    if [[ "$response" =~ ^[Oo]$ ]]; then
        # Remove existing cron job
        crontab -l 2>/dev/null | grep -v "$REPORT_SCRIPT" | crontab -
        echo "Ancien cron job supprimé"
    else
        echo "Installation annulée"
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

if [ $? -eq 0 ]; then
    echo "Cron job installé avec succès!"
    echo ""
    echo "Cron job configuré:"
    echo "   $CRON_LINE"
    echo ""
    echo "Pour vérifier: crontab -l"
    echo "Pour voir les logs: tail -f $LOG_FILE"
    echo "Pour tester maintenant: $PYTHON_CMD $REPORT_SCRIPT"
    echo ""
    echo "Le rapport sera généré automatiquement tous les jours à 20h dans:"
    echo "   $PROJECT_DIR/reports/"
else
    echo "Erreur lors de l'installation du cron job"
    exit 1
fi

