FROM node:20-alpine

# Arguments pour les permissions
ARG MY_UID=1000
ARG MY_GID=1000

# Créer un utilisateur non-root
RUN addgroup -g ${MY_GID} -S nodegroup && \
    adduser -u ${MY_UID} -S nodeuser -G nodegroup

# Définir le répertoire de travail
WORKDIR /home/node/app

# Copier les fichiers de dépendances
COPY --chown=nodeuser:nodegroup package*.json ./

# Installer les dépendances
RUN npm ci --only=production=false && \
    npm cache clean --force

# Copier le reste de l'application
COPY --chown=nodeuser:nodegroup . .

# Installer Angular CLI globalement
RUN npm install -g @angular/cli@17

# Donner les permissions au script d'initialisation
RUN chmod +x init-angular.sh || true

# Changer vers l'utilisateur non-root
USER nodeuser

# Exposer le port
EXPOSE 4200

# Commande par défaut
CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]