# Projet de Collecte et Analyse des Cyber-Menaces

## Résumé

Le projet vise à développer un service interopérable avec un système d'information, capable de déclencher des alertes en lien avec les technologies du SI touchées par les actualités relatives aux tendances des cyber-menaces et aux vulnérabilités critiques.

## Déroulement du projet (Milestones)

### Partie 1: Collecte de données
1. **Mise en place d'un script de Web Scraping**
   - Utilisation de BeautifulSoup pour extraire des informations des sites sources.
   - Scripts dédiés (nvd_scrapping.py et certfr_scrapping.py) pour la collecte des données depuis le site NIST et CERT-FR.

2. **Application de tests d'évasion**
   - Vérification de la capacité du robot à éviter la détection lors de la collecte de données.

### Partie 2: Persistence des données et fonctionnalités de recherche
1. **Création d'une base de données avec SQLAlquemy**
   - Utilisation de SQLAlquemy pour créer et gérer une base de données relationnelle pour stocker les données collectées.

2. **Mise en place d'un moteur de recherche**
   - Implémentation d'un moteur de recherche pour faciliter l'exploration des données stockées dans la base de données.

## Requirements
Les librairies et bibliothèques nécessaires sont mentionnées dans le fichier `requirements.txt`.
