FROM node:20-alpine

# Créer le répertoire de travail
WORKDIR /home/node/app

# Copier les fichiers package
COPY package*.json ./

# Installer les dépendances
RUN npm install --legacy-peer-deps

# Copier le reste de l'application
COPY . .

# Installer Angular CLI globalement
RUN npm install -g @angular/cli@17

# Exposer le port
EXPOSE 4200

# Commande par défaut (sera override par docker-compose)
CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000", "--disable-host-check"]