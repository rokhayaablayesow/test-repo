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

# Test de l'algorithme
if __name__ == "__main__":
    print("=== ALGORITHME 2: Deux éléments dont la somme est proche de zéro ===")
    arr = [1, 60, -10, 70, -80, 85]
    print(f"Input: {arr}")
    resultat = deux_elements_proche_zero(arr)
    print(f"Output: {resultat[0]} et {resultat[1]}")