#!/bin/bash

# Dossiers à surveiller

ERROR=$(tput setaf 1; echo -n "  [!]"; tput sgr0)
GOODTOGO=$(tput setaf 2; echo -n "  [✓]"; tput sgr0)
INFO=$(tput setaf 3; echo -n "  [-]"; tput sgr0)
USERINPUT=$(tput setaf 4; echo -n "  [?]"; tput sgr0)
INFOFILE=$(tput setaf 5; echo -n "  [#]"; tput sgr0)
MASTER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

DIR_RESULT="$MASTER_DIR/../../share/fifos/result/"
DIR_TO_WATCH="$MASTER_DIR/../../share/fifos/execute/"

# Fichiers temporaires pour stocker les listes des fichiers
TEMP_FILE="/tmp/previous_files.txt"
# Crée ou met à jour le fichier temporaire avec la liste initiale des fichiers
ls "$DIR_TO_WATCH" > "$TEMP_FILE"

# Define the PowerShell path
POWERSHELL_PATH="/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/"

# Check if PowerShell is in the PATH
if ! echo "$PATH" | grep -q "$POWERSHELL_PATH"; then
    (echo >&2 "${ERROR} PowerShell is not in the PATH. Adding it now.")
    export PATH="$PATH:$POWERSHELL_PATH"
else
    (echo >&2 "${GOODTOGO} PowerShell is already in the PATH.")
fi

(echo >&2 "${USERINPUT} Waiting for new command.")

# Boucle infinie pour surveiller le dossier
while true; do
    # Crée une liste actuelle des fichiers
    CURRENT_FILE_LIST=$(mktemp)
    ls "$DIR_TO_WATCH" > "$CURRENT_FILE_LIST"
    
    # Compare la liste actuelle avec la liste précédente
    NEW_FILES=$(diff "$TEMP_FILE" "$CURRENT_FILE_LIST" | grep '^>' | sed 's/^> //' )

    # Si des nouveaux fichiers sont trouvés, affiche leurs noms
    if [ ! -z "$NEW_FILES" ]; then
        # Crée les chemins pour les fichiers FIFO
        for NEW_FILE in $NEW_FILES; do
            COMMAND_FIFO="${DIR_TO_WATCH}${NEW_FILE}"
            RESULT_FIFO="${DIR_RESULT}${NEW_FILE}"
            
            (echo >&2 "${INFOFILE} New file ! Path: $COMMAND_FIFO")
            (echo >&2 "${INFOFILE} Result file! Path: $RESULT_FIFO")

            # Crée les fichiers FIFO s'ils n'existent pas
            if [ ! -p "$RESULT_FIFO" ]; then
                mkfifo "$RESULT_FIFO"
            fi
            # while true; do
            #     if read line; then
            #         eval $line
            #     fi
            # done <"$COMMAND_FIFO"
            
            # Boucle pour lire les commandes du FIFO et exécuter les commandes
            while true; do
                if read -r command < "$COMMAND_FIFO"; then
                    if [[ "$command" == "exit" ]]; then
                        # Vous pouvez mettre une sortie propre ici si besoin
                        break
                    fi
                    (echo >&2 "${INFO} Executing command : $command")

                    # Exécution de la commande et capture de la sortie
                    result=$(powershell.exe -Command "$command");
                    # result=$(eval "$command" 2>&1)
                    
                    (echo >&2 "${GOODTOGO} Result of the command : $result")

                    # Essayer d'écrire dans le pipe avec une attente en cas d'échec
                    if echo "$result" > "$RESULT_FIFO"; then
                        break
                    else
                        # echo "Échec de l'écriture dans $RESULT_FIFO"
                        sleep 1
                    fi
                fi
            done
            # Supprime le fichier FIFO après utilisation
            rm -f "$COMMAND_FIFO"  
        done
    fi

    # Met à jour la liste précédente avec la liste actuelle
    mv "$CURRENT_FILE_LIST" "$TEMP_FILE"

    # Pause avant de vérifier à nouveau (par exemple, toutes les 2 secondes)
    sleep 2
done
