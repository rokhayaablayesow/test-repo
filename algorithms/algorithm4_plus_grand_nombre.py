from functools import cmp_to_key

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

# Tests de l'algorithme
if __name__ == "__main__":
    print("=== ALGORITHME 4: Plus grand nombre possible avec les chiffres donnés ===")
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