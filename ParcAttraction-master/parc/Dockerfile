FROM node:20-alpine

# On n'a plus besoin de créer l'utilisateur, il existe déjà
# Définir le répertoire de travail
WORKDIR /home/node/app

# Copier les fichiers en s'assurant que l'utilisateur 'node' est propriétaire
COPY --chown=node:node package*.json ./

# Installer les dépendances
RUN npm install --legacy-peer-deps && npm cache clean --force

# Copier le reste
COPY --chown=node:node . .

# Installer Angular CLI globalement
RUN npm install -g @angular/cli@17

# Permissions
RUN chmod +x init-angular.sh || true

# Utiliser l'utilisateur node existant (UID 1000)
USER node

EXPOSE 4200
CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]