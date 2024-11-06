
result=$(eval "$1" 2>&1)

# Essayer d'écrire dans le pipe avec une attente en cas d'échec
echo "$result"