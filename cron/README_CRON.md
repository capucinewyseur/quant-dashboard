# Configuration du Cron Job pour les Rapports Quotidiens

## Installation Automatique 

Pour installer automatiquement le cron job qui génère un rapport tous les jours à 20h :

```bash
cd /path/to/quant-dashboard
./cron/install_cron.sh
```

Le script va :
- Détecter automatiquement les chemins (projet, Python)
- Créer le dossier `reports/` si nécessaire
- Configurer le cron job pour 20h chaque jour
- Vérifier que tout fonctionne

## Installation Manuelle

Configuration manuelle du cron job :

1. **Éditer le crontab** :
```bash
crontab -e
```

2. **Ajouter cette ligne** (ajustez les chemins) :
```bash
0 20 * * * cd /Users/capucinewyseur/Downloads/projet/quant-dashboard && /usr/bin/python3 cron/generate_report.py >> cron/cron.log 2>&1
```

3. **Vérifier l'installation** :
```bash
crontab -l
```

## Format du Cron Job

```
0 20 * * * [commande]
│ │ │ │ │
│ │ │ │ └─── Jour de la semaine (0-7, 0 et 7 = dimanche)
│ │ │ └───── Mois (1-12)
│ │ └─────── Jour du mois (1-31)
│ └───────── Heure (0-23)
└─────────── Minute (0-59)
```

Dans notre cas : `0 20 * * *` = Tous les jours à 20h00 (8 PM)

## Vérification

### Voir les cron jobs installés :
```bash
crontab -l
```

### Voir les logs :
```bash
tail -f cron/cron.log
```

### Tester manuellement :
```bash
python3 cron/generate_report.py AAPL
```

## Désinstallation

Pour supprimer le cron job :

```bash
crontab -l | grep -v "generate_report.py" | crontab -
```

## Emplacement des Rapports

Les rapports sont sauvegardés dans :
```
quant-dashboard/reports/YYYY-MM-DD.txt
```

Exemple : `reports/2025-11-20.txt`

## Personnalisation

### Changer l'heure d'exécution

Modifiez le premier nombre dans le cron job :
- `0 20 * * *` = 20h00 (8 PM)
- `0 9 * * *` = 9h00 (9 AM)
- `30 18 * * *` = 18h30 (6:30 PM)

### Changer le ticker par défaut

Modifiez `cron/generate_report.py` ligne 171 :
```python
ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"  # Changez "AAPL"
```

Ou modifiez la ligne cron pour passer un argument :
```bash
0 20 * * * cd /path/to/quant-dashboard && python3 cron/generate_report.py MSFT >> cron/cron.log 2>&1
```

## Dépannage

### Le cron job ne s'exécute pas

1. Vérifiez que cron est actif :
```bash
sudo systemctl status cron  # Linux
```

2. Vérifiez les logs système :
```bash
grep CRON /var/log/syslog  # Linux
```

3. Vérifiez les permissions :
```bash
chmod +x cron/generate_report.py
```

4. Testez manuellement :
```bash
python3 cron/generate_report.py
```

### Les rapports ne sont pas générés

1. Vérifiez que le dossier `reports/` existe et est accessible
2. Vérifiez les logs : `cat cron/cron.log`
3. Vérifiez que Python peut importer les modules

