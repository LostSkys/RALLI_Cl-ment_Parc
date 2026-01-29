ALORS 
- On peux pas se connecter
- Il a fallut modifier le Dockerfile de parc pour faire fonctionner le build
    -> ERREUR  : ERROR [web 4/7] RUN groupadd -g 0 customgroup
    -> Changement : les lignes 8 à 10 se sont vu remplacer par celles-ci :
        RUN if [ "$MY_GID" != "0" ]; then \
            groupadd -g "$MY_GID" customgroup && \
            useradd -l -u "$MY_UID" -g "$MY_GID" node; \
            else \
            echo "Using existing root group"; \
            fi
- On ne peux pas ajouter de parc