#!/bin/bash
# Script d'installation automatique du cron job pour les rapports quotidiens
# Ce script configure le cron job pour générer un rapport tous les jours à 20h

echo "=========================================="
echo "Installation du cron job pour les rapports quotidiens"
echo "=========================================="

# Obtenir le chemin absolu du projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Dossier du projet: $PROJECT_DIR"

# Trouver Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=$(which python3)
elif command -v python &> /dev/null; then
    PYTHON_CMD=$(which python)
else
    echo "❌ Erreur: Python n'est pas trouvé"
    exit 1
fi

echo "🐍 Python trouvé: $PYTHON_CMD"

# Chemin du script de génération de rapport
REPORT_SCRIPT="$PROJECT_DIR/cron/generate_report.py"
LOG_FILE="$PROJECT_DIR/cron/cron.log"

echo "📝 Script de rapport: $REPORT_SCRIPT"
echo "📋 Fichier de log: $LOG_FILE"

# Vérifier que le script existe
if [ ! -f "$REPORT_SCRIPT" ]; then
    echo "❌ Erreur: Le script generate_report.py n'existe pas"
    exit 1
fi

# Créer le dossier reports s'il n'existe pas
mkdir -p "$PROJECT_DIR/reports"
echo "✅ Dossier reports créé/vérifié"

# Ligne cron à ajouter (20h = 20:00 chaque jour)
CRON_LINE="0 20 * * * cd $PROJECT_DIR && $PYTHON_CMD $REPORT_SCRIPT >> $LOG_FILE 2>&1"

echo ""
echo "📅 Configuration du cron job (exécution tous les jours à 20h)..."
echo ""

# Vérifier si le cron job existe déjà
if crontab -l 2>/dev/null | grep -q "$REPORT_SCRIPT"; then
    echo "⚠️  Le cron job existe déjà. Voulez-vous le remplacer? (o/n)"
    read -r response
    if [[ "$response" =~ ^[Oo]$ ]]; then
        # Supprimer l'ancien cron job
        crontab -l 2>/dev/null | grep -v "$REPORT_SCRIPT" | crontab -
        echo "🗑️  Ancien cron job supprimé"
    else
        echo "❌ Installation annulée"
        exit 0
    fi
fi

# Ajouter le nouveau cron job
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job installé avec succès!"
    echo ""
    echo "📋 Cron job configuré:"
    echo "   $CRON_LINE"
    echo ""
    echo "🔍 Pour vérifier: crontab -l"
    echo "📊 Pour voir les logs: tail -f $LOG_FILE"
    echo "🧪 Pour tester maintenant: $PYTHON_CMD $REPORT_SCRIPT"
    echo ""
    echo "✨ Le rapport sera généré automatiquement tous les jours à 20h dans:"
    echo "   $PROJECT_DIR/reports/"
else
    echo "❌ Erreur lors de l'installation du cron job"
    exit 1
fi

