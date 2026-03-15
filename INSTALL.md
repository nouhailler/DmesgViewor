# 🚀 Installation de DMESGVIEWOR

## ✅ Méthode recommandée — Paquet Debian (.deb)

### 1. Télécharger le paquet

Depuis la page [Releases](https://github.com/nouhailler/DmesgViewor/releases) :

```bash
wget https://github.com/nouhailler/DmesgViewor/releases/download/v1.0.0/dmesgviewor_1.0.0.deb
```

### 2. Installer

```bash
sudo dpkg -i dmesgviewor_1.0.0.deb
```

Si des dépendances manquent, les installer automatiquement :

```bash
sudo apt-get install -f
```

### 3. Lancer l'application

Depuis le terminal :

```bash
dmesgviewor
```

Ou depuis le menu Applications de votre bureau (section **Utilitaires / Système**).

---

## 🔑 Configuration des droits dmesg

Sur **Debian 12+**, l'accès aux journaux noyau est restreint par défaut.

### Option A — Groupe `adm` *(recommandée, permanente)*

```bash
sudo usermod -aG adm $USER
```

> ⚠️ Déconnectez-vous puis reconnectez-vous pour que le changement soit actif.

### Option B — Mot de passe sudo à chaque lancement *(intégré)*

L'application détecte automatiquement le problème et affiche une fenêtre de
saisie du mot de passe sudo. Aucune configuration nécessaire.

---

## 🔧 Méthode alternative — Source

```bash
git clone https://github.com/nouhailler/DmesgViewor.git
cd DmesgViewor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 🗑️ Désinstallation

```bash
sudo dpkg -r dmesgviewor
```
