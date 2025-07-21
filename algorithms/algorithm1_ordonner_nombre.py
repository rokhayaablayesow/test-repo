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

# Test de l'algorithme
if __name__ == "__main__":
    print("=== ALGORITHME 1: Ordonner les chiffres d'un nombre par ordre décroissant ===")
    print(f"Input: 212345")
    print(f"Output: {ordonner_nombre_decroissant(212345)}")