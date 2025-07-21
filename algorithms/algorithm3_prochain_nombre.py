def prochain_nombre_superieur(n):
    """
    Trouve le plus petit nombre supérieur avec le même ensemble de chiffres
    Input: string représentant un nombre
    Output: string du nombre suivant ou "Not Possible"
    """
    digits = list(n)
    length = len(digits)
    
    # Étape 1: Trouver le pivot (chiffre à partir de la droite qui peut être augmenté)
    i = length - 2
    while i >= 0 and digits[i] >= digits[i + 1]:
        i -= 1
    
    # Si aucun pivot trouvé, pas de nombre supérieur possible
    if i == -1:
        return "Not Possible"
    
    # Étape 2: Trouver le plus petit chiffre à droite du pivot qui est plus grand que le pivot
    j = length - 1
    while digits[j] <= digits[i]:
        j -= 1
    
    # Étape 3: Échanger le pivot avec ce chiffre
    digits[i], digits[j] = digits[j], digits[i]
    
    # Étape 4: Trier les chiffres à droite du pivot par ordre croissant
    digits[i + 1:] = sorted(digits[i + 1:])
    
    return ''.join(digits)

# Tests de l'algorithme
if __name__ == "__main__":
    print("=== ALGORITHME 3: Plus petit nombre supérieur avec même ensemble de chiffres ===")
    test_cases = ["218765", "1234", "4321", "534976"]
    for test in test_cases:
        print(f"Input: {test}")
        print(f"Output: {prochain_nombre_superieur(test)}")