# ===============================================
# ALGORITHME 1: Ordonner les chiffres d'un nombre par ordre décroissant
# ===============================================

def ordonner_nombre_decroissant(n):
    """
    Ordonne les chiffres d'un nombre par ordre décroissant
    Input: nombre entier
    Output: string avec chiffres séparés par des virgules
    """
    # Convertir en string pour accéder aux chiffres individuels
    chiffres = list(str(n))
    
    # Trier par ordre décroissant
    chiffres.sort(reverse=True)
    
    # Joindre avec des virgules
    return ','.join(chiffres)

# ===============================================
# ALGORITHME 2: Deux éléments dont la somme est proche de zéro
# ===============================================

def deux_elements_proche_zero(arr):
    """
    Trouve deux éléments dont la somme est la plus proche de zéro
    Input: tableau d'entiers
    Output: tuple des deux éléments
    """
    n = len(arr)
    if n < 2:
        return None
    
    # Trier le tableau pour optimiser la recherche
    arr.sort()
    
    left = 0
    right = n - 1
    min_sum = float('inf')
    result = (arr[0], arr[1])
    
    while left < right:
        current_sum = arr[left] + arr[right]
        
        # Si la somme absolue est plus petite, on met à jour le résultat
        if abs(current_sum) < abs(min_sum):
            min_sum = current_sum
            result = (arr[left], arr[right])
        
        # Si la somme est négative, on augmente left
        if current_sum < 0:
            left += 1
        # Si la somme est positive, on diminue right
        else:
            right -= 1
    
    return result

# ===============================================
# ALGORITHME 3: Plus petit nombre supérieur avec même ensemble de chiffres
# ===============================================

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

# Test de l'algorithme 1
print("=== ALGORITHME 1 ===")
print(f"Input: 212345")
print(f"Output: {ordonner_nombre_decroissant(212345)}")
print()

# Test de l'algorithme 2
print("=== ALGORITHME 2 ===")
arr = [1, 60, -10, 70, -80, 85]
print(f"Input: {arr}")
resultat = deux_elements_proche_zero(arr)
print(f"Output: {resultat[0]} et {resultat[1]}")
print()

# Tests de l'algorithme 3
print("=== ALGORITHME 3 ===")
test_cases = ["218765", "1234", "4321", "534976"]
for test in test_cases:
    print(f"Input: {test}")
    print(f"Output: {prochain_nombre_superieur(test)}")
print()

# ===============================================
# ALGORITHME 4: Plus grand nombre possible avec les chiffres donnés
# ===============================================

def plus_grand_nombre_possible(arr):
    """
    Génère le plus grand nombre possible avec les chiffres donnés
    Input: tableau de chiffres (0-9)
    Output: string représentant le plus grand nombre
    """
    # Convertir tous les éléments en string pour la comparaison personnalisée
    str_arr = [str(x) for x in arr]
    
    # Trier avec une comparaison personnalisée
    # Pour deux nombres a et b, on compare a+b avec b+a
    # Si a+b > b+a, alors a doit venir avant b
    from functools import cmp_to_key
    
    def comparer(x, y):
        if x + y > y + x:
            return -1  # x avant y
        elif x + y < y + x:
            return 1   # y avant x
        else:
            return 0   # égaux
    
    # Trier selon notre comparateur personnalisé
    str_arr.sort(key=cmp_to_key(comparer))
    
    # Joindre tous les chiffres
    resultat = ''.join(str_arr)
    
    # Gérer le cas où tous les chiffres sont 0
    if resultat[0] == '0':
        return '0'
    
    return resultat

# Tests de l'algorithme 4
print("=== ALGORITHME 4 ===")
test_cases = [
    [4, 7, 9, 2, 3],
    [8, 6, 0, 4, 6, 4, 2, 7]
]

for test in test_cases:
    print(f"Input: {test}")
    print(f"Output: Largest number: {plus_grand_nombre_possible(test)}")

print()
print("=== TESTS SUPPLÉMENTAIRES ===")
# Test avec des cas particuliers
print("Test algorithme 4 avec [0, 0, 0]:")
print(f"Output: {plus_grand_nombre_possible([0, 0, 0])}")

print("Test algorithme 4 avec [5, 50, 56]:")
print(f"Output: {plus_grand_nombre_possible([5, 50, 56])}")