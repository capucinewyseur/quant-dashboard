Quant Dashboard
Présentation du projet

Ce projet consiste en le développement d’un dashboard de finance quantitative en Python, basé sur Streamlit, permettant l’analyse de données financières, le backtesting de stratégies de trading et la génération automatisée de rapports.

L’objectif est de mettre en œuvre une architecture modulaire reproduisant un workflow quantitatif complet : extraction de données, traitement, indicateurs, stratégies, évaluation des performances et restitution visuelle.

Environnement et outils

Langage : Python

Interface : Streamlit

Gestion de version : Git / GitHub

Déploiement : AWS (machine virtuelle Linux)

Planification : Cron

Sources de données : API financière (Alpha Vantage / Yahoo Finance)

Un environnement virtuel Python a été utilisé afin d’isoler les dépendances du projet.

Architecture du projet
quant-dashboard/
├── app.py                  # Application Streamlit principale
├── modules/
│   ├── data.py             # Chargement et nettoyage des données
│   ├── indicators.py       # Indicateurs techniques
│   ├── strategies.py       # Stratégies de trading
│   ├── backtesting.py      # Backtesting et métriques
│   ├── prediction.py       # Modèle de prédiction
│   ├── single_asset.py     # Module Quant A
│   └── portfolio.py        # Module Quant B
├── cron/                   # Génération automatique de rapports
├── reports/                # Rapports journaliers
└── requirements.txt

Quant A — Analyse mono-actif

Le module Quant A est dédié à l’analyse d’un actif financier unique (Apple – AAPL).

Fonctionnalités principales :

Récupération automatique des données de marché (mise à jour toutes les 5 minutes)

Visualisation du prix et des rendements

Implémentation de stratégies quantitatives :

Buy & Hold

Momentum

RSI

Calcul des métriques de performance :

Rendement annualisé

Volatilité

Sharpe Ratio

Max Drawdown

Affichage des indicateurs techniques (RSI, moyennes mobiles)

Module de prédiction par régression linéaire simple, intégré au dashboard à titre illustratif

Quant B — Analyse multi-actifs

Le module Quant B étend l’analyse à un portefeuille composé de plusieurs actifs.

Fonctionnalités principales :

Suivi en temps réel des prix de plusieurs actifs

Construction de portefeuilles :

Équipondéré

Pondérations personnalisées

Simulation de la valeur du portefeuille dans le temps

Backtesting du portefeuille global

Calcul automatique des métriques de performance :

Rendement annualisé

Volatilité

Sharpe Ratio

Max Drawdown

Analyse de la diversification via une matrice de corrélation

Génération automatique de rapports journaliers (scripts planifiés sur la VM AWS)

Déploiement et automatisation

L’application a été déployée sur une infrastructure cloud AWS, permettant un accès distant au dashboard Streamlit.
Un système de cron jobs a été configuré afin de générer automatiquement des rapports quotidiens en format texte, sans intervention manuelle.

Travail collaboratif

Le développement a été réalisé de manière collaborative à l’aide de Git :

Branche main : version stable

Branches de développement :

emile (Quant A)

ptAcapucine (Quant B)

Les fusions ont été effectuées après validation des fonctionnalités.
