# Handover - Partie B: Portfolio Analysis Module

## 📋 Informations de Transition

Ce document contient toutes les informations nécessaires pour que le binôme puisse continuer le projet et implémenter la **Partie B: Portfolio Analysis Module**.

---

## 🔑 Accès et Identifiants

### 1. Repository GitHub
- **URL**: `https://github.com/capucinewyseur/quant-dashboard.git`
- **Branche actuelle**: `ptAcapucine`
- **Branche principale**: `main` (ou `master`)
- **Status**: Le code de la Partie A est complet et fonctionnel

### 2. Accès AWS (si nécessaire)
- **Clé SSH**: Enregistrée dans `~/Documents/api/` (ou chemin spécifique)
- **Nom du fichier clé**: `capucine.keyperm` (ou nom exact)
- **Chemin complet**: À vérifier dans `~/Documents/api/`
- **Instructions SSH**: 
  ```bash
  ssh -i ~/Documents/api/capucine.keyperm user@aws-instance-ip
  ```

### 3. Structure du Projet
```
quant-dashboard/
├── app.py                      # Application principale Streamlit
├── modules/
│   ├── data.py                # Chargement des données (Yahoo Finance)
│   ├── indicators.py          # Indicateurs techniques (RSI, MACD, SMA)
│   ├── strategies.py          # Stratégies de trading (Buy & Hold, RSI, Momentum)
│   ├── backtesting.py         # Moteur de backtesting et métriques
│   ├── prediction.py         # Modèle prédictif (Régression linéaire)
│   ├── single_asset.py        # Module Partie A (COMPLET)
│   └── portfolio.py           # Module Partie B (À IMPLÉMENTER)
├── cron/
│   ├── generate_report.py     # Générateur de rapports quotidiens
│   ├── install_cron.sh        # Installation automatique du cron
│   └── README_CRON.md         # Documentation cron
├── reports/                   # Rapports générés (auto-créé)
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation principale
├── VALIDATION_QUANT_A.md      # Validation Partie A
└── HANDOVER_PARTIE_B.md       # Ce document
```

---

## 🚀 Configuration Initiale pour le Binôme

### Étape 1: Cloner le Repository
```bash
git clone https://github.com/capucinewyseur/quant-dashboard.git
cd quant-dashboard
```

### Étape 2: Créer un Environnement Virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### Étape 3: Installer les Dépendances
```bash
pip install -r requirements.txt
```

### Étape 4: Vérifier que l'Application Fonctionne
```bash
streamlit run app.py
```

L'application devrait s'ouvrir sur `http://localhost:8501`

---

## 📝 Partie A: Ce qui est Déjà Fait

### ✅ Module Single Asset (COMPLET)
- Analyse d'un actif à la fois
- 3 stratégies de backtesting (Buy & Hold, RSI, Momentum)
- Métriques de performance (Sharpe, Max Drawdown, Volatility, CAGR, Total Return)
- Contrôles interactifs (périodicité, paramètres de stratégie)
- Graphique principal avec prix brut + valeur cumulée stratégie
- Bonus: Modèle prédictif (Régression linéaire)

**Fichiers clés**:
- `app.py`: Application principale (lignes 63-347 pour Single Asset)
- `modules/single_asset.py`: Module détaillé Single Asset
- `modules/strategies.py`: 3 stratégies implémentées
- `modules/backtesting.py`: Toutes les fonctions de backtesting

### ✅ Fonctionnalités Transverses
- Chargement de données depuis Yahoo Finance (`modules/data.py`)
- Indicateurs techniques (RSI, MACD, SMA) (`modules/indicators.py`)
- Auto-refresh toutes les 5 minutes
- Rapports quotidiens via cron (`cron/generate_report.py`)

---

## 🎯 Partie B: À Implémenter

### Objectif: Portfolio Analysis Module

Le binôme doit implémenter le module **Portfolio** qui permet d'analyser plusieurs actifs simultanément.

### Exigences Attendues (selon le sujet)

1. **Multi-Asset Analysis**
   - Analyser plusieurs actifs en même temps (portfolio)
   - Gestion de poids/allocations par actif
   - Calcul des rendements du portfolio

2. **Portfolio Strategies**
   - Stratégies de rééquilibrage (rebalancing)
   - Stratégies d'allocation (equal weight, market cap, etc.)
   - Comparaison de différents portfolios

3. **Portfolio Metrics**
   - Rendement du portfolio
   - Volatilité du portfolio
   - Sharpe Ratio du portfolio
   - Corrélations entre actifs
   - Diversification metrics

4. **Visualizations**
   - Graphiques de performance du portfolio
   - Graphiques de corrélations
   - Graphiques d'allocation (pie charts)
   - Comparaison portfolio vs benchmark

5. **Interactive Controls**
   - Sélection de plusieurs tickers
   - Ajustement des poids/allocations
   - Sélection de stratégie de rééquilibrage

### Fichier à Modifier/Créer

**`modules/portfolio.py`** (actuellement un placeholder):
```python
import streamlit as st

def display_portfolio_module():
    st.subheader("Portfolio Module (Quant B)")
    st.write("Here will come multi-asset portfolio simulations.")
```

**À remplacer par** une implémentation complète du module portfolio.

### Intégration dans `app.py`

Le module portfolio est déjà intégré dans la navigation:
```python
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])
```

Quand `page == "Portfolio"`, la fonction `display_portfolio_module()` est appelée (ligne 348).

---

## 🔧 Fonctions Utiles Déjà Disponibles

Le binôme peut réutiliser les fonctions existantes:

### Chargement de Données
```python
from modules.data import load_asset

# Charger un actif
df = load_asset("AAPL", start="2018-01-01", interval="1d")
```

### Calculs de Métriques
```python
from modules.backtesting import (
    compute_returns,
    compute_volatility,
    compute_sharpe_ratio,
    compute_max_drawdown,
    compute_cagr,
    compute_total_return
)
```

### Indicateurs Techniques
```python
from modules.indicators import add_rsi, add_macd, add_sma
```

---

## 📚 Ressources et Documentation

### Documentation du Projet
- **README.md**: Documentation principale du projet
- **VALIDATION_QUANT_A.md**: Validation de la Partie A
- **cron/README_CRON.md**: Documentation des rapports quotidiens

### Bibliothèques Utilisées
- **Streamlit**: Framework dashboard
- **yfinance**: Données financières
- **pandas**: Manipulation de données
- **numpy**: Calculs numériques
- **plotly**: Graphiques interactifs

### Exemples de Code à Consulter
- **Single Asset Module**: `modules/single_asset.py` (exemple d'implémentation complète)
- **Backtesting**: `modules/backtesting.py` (fonctions réutilisables)
- **App Principal**: `app.py` (structure et intégration)

---

## 🔄 Workflow Git Recommandé

### Pour le Binôme

1. **Créer une nouvelle branche pour la Partie B**:
   ```bash
   git checkout -b partie-b-portfolio
   ```

2. **Travailler sur le module portfolio**:
   - Modifier `modules/portfolio.py`
   - Ajouter de nouvelles fonctions si nécessaire
   - Tester localement avec `streamlit run app.py`

3. **Commits réguliers**:
   ```bash
   git add modules/portfolio.py
   git commit -m "Implement portfolio module - multi-asset analysis"
   git push origin partie-b-portfolio
   ```

4. **Merge dans la branche principale** (après validation):
   ```bash
   git checkout ptAcapucine  # ou main
   git merge partie-b-portfolio
   ```

---

## 🐛 Dépannage

### Problèmes Courants

1. **Module non trouvé**:
   ```bash
   # Vérifier que vous êtes dans le bon dossier
   pwd
   # Devrait être: /path/to/quant-dashboard
   
   # Vérifier que venv est activé
   which python  # Devrait pointer vers venv/bin/python
   ```

2. **Dépendances manquantes**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Erreur de données Yahoo Finance**:
   - Vérifier la connexion internet
   - Vérifier que le ticker existe
   - Essayer un autre ticker (AAPL, MSFT, etc.)

---

## 📞 Contact et Support

### Informations de Contact
- **GitHub Repository**: https://github.com/capucinewyseur/quant-dashboard
- **Issues**: Utiliser GitHub Issues pour signaler des problèmes

### Points d'Attention

1. **Ne pas modifier la Partie A** sans coordination
2. **Tester l'intégration** avec la Partie A après chaque modification
3. **Respecter la structure** existante du projet
4. **Documenter le code** (commentaires neutres et techniques)

---

## ✅ Checklist pour le Binôme

Avant de commencer:
- [ ] Repository cloné
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Application fonctionne (`streamlit run app.py`)
- [ ] Module Single Asset testé et compris
- [ ] Structure du projet comprise

Pour implémenter la Partie B:
- [ ] Nouvelle branche Git créée
- [ ] `modules/portfolio.py` modifié
- [ ] Multi-asset analysis implémenté
- [ ] Stratégies de portfolio implémentées
- [ ] Métriques de portfolio calculées
- [ ] Visualisations créées
- [ ] Contrôles interactifs ajoutés
- [ ] Tests effectués
- [ ] Documentation mise à jour

---

## 🎓 Notes Finales

Le projet est bien structuré et la Partie A est complète. Le binôme peut se concentrer uniquement sur l'implémentation de la Partie B (Portfolio Module) en réutilisant les fonctions existantes.

**Bon courage pour la Partie B! 🚀**

