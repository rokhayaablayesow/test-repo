import sqlite3
import os

DATABASE = 'categories.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Table des catégories hiérarchiques
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            parent_id INTEGER,
            level INTEGER DEFAULT 1,
            product_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )
    ''')
    
    # Table des produits
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_category_level(category_id, conn):
    """Calcule le niveau d'une catégorie"""
    level = 1
    current_id = category_id
    
    while True:
        parent = conn.execute(
            'SELECT parent_id FROM categories WHERE id = ?', 
            (current_id,)
        ).fetchone()
        
        if parent is None or parent['parent_id'] is None:
            break
            
        level += 1
        current_id = parent['parent_id']
        
        # Protection contre les boucles infinies
        if level > 10:
            break
    
    return level

def update_product_counts():
    """Met à jour le nombre de produits pour chaque catégorie"""
    conn = get_db_connection()
    
    # Reset tous les compteurs
    conn.execute('UPDATE categories SET product_count = 0')
    
    # Compter les produits directs pour chaque catégorie
    conn.execute('''
        UPDATE categories 
        SET product_count = (
            SELECT COUNT(*) 
            FROM products 
            WHERE products.category_id = categories.id
        )
    ''')
    
    # Ajouter les produits des sous-catégories (récursif)
    categories = conn.execute('SELECT id FROM categories ORDER BY level DESC').fetchall()
    
    for category in categories:
        # Compter les produits dans les sous-catégories
        subcategory_products = conn.execute('''
            WITH RECURSIVE subcategories AS (
                SELECT id FROM categories WHERE parent_id = ?
                UNION ALL
                SELECT c.id FROM categories c
                INNER JOIN subcategories s ON c.parent_id = s.id
            )
            SELECT COUNT(*) as count
            FROM products p
            INNER JOIN subcategories s ON p.category_id = s.id
        ''', (category['id'],)).fetchone()
        
        if subcategory_products['count'] > 0:
            conn.execute('''
                UPDATE categories 
                SET product_count = product_count + ? 
                WHERE id = ?
            ''', (subcategory_products['count'], category['id']))
    
    conn.commit()
    conn.close()

def get_category_parentage(category_id):
    """Retourne le chemin hiérarchique d'une catégorie"""
    conn = get_db_connection()
    parentage = []
    current_id = category_id
    
    while current_id:
        category = conn.execute(
            'SELECT id, name, parent_id FROM categories WHERE id = ?',
            (current_id,)
        ).fetchone()
        
        if category:
            parentage.insert(0, category['name'])
            current_id = category['parent_id']
        else:
            break
    
    conn.close()
    return " > ".join(parentage)

def check_circular_reference(category_id, parent_id):
    """Vérifie s'il y a une référence circulaire"""
    if category_id == parent_id:
        return True
    
    conn = get_db_connection()
    current_id = parent_id
    
    while current_id:
        if current_id == category_id:
            conn.close()
            return True
            
        parent = conn.execute(
            'SELECT parent_id FROM categories WHERE id = ?',
            (current_id,)
        ).fetchone()
        
        if parent:
            current_id = parent['parent_id']
        else:
            break
    
    conn.close()
    return False

def create_sample_data():
    """Crée des données d'exemple"""
    conn = get_db_connection()
    
    # Vérifier si des données existent déjà
    existing = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    
    if existing == 0:
        # Catégories principales (niveau 1)
        categories = [
            ('Électronique', 'Appareils électroniques et gadgets', None),
            ('Vêtements', 'Articles de mode et habillement', None),
            ('Maison & Jardin', 'Décoration et mobilier', None),
        ]
        
        for name, desc, parent in categories:
            conn.execute(
                'INSERT INTO categories (name, description, parent_id, level) VALUES (?, ?, ?, 1)',
                (name, desc, parent)
            )
        
        # Sous-catégories (niveau 2)
        subcategories = [
            ('Smartphones', 'Téléphones intelligents', 1),
            ('Ordinateurs', 'PC et laptops', 1),
            ('Homme', 'Vêtements masculins', 2),
            ('Femme', 'Vêtements féminins', 2),
            ('Cuisine', 'Équipements de cuisine', 3),
        ]
        
        for name, desc, parent_id in subcategories:
            conn.execute(
                'INSERT INTO categories (name, description, parent_id, level) VALUES (?, ?, ?, 2)',
                (name, desc, parent_id)
            )
        
        # Sous-sous-catégories (niveau 3)
        subsubcategories = [
            ('iPhone', 'Smartphones Apple', 4),
            ('Android', 'Smartphones Android', 4),
            ('Chemises', 'Chemises homme', 6),
            ('Robes', 'Robes femme', 7),
        ]
        
        for name, desc, parent_id in subsubcategories:
            conn.execute(
                'INSERT INTO categories (name, description, parent_id, level) VALUES (?, ?, ?, 3)',
                (name, desc, parent_id)
            )
        
        # Produits d'exemple
        products = [
            ('iPhone 14', 'Dernier iPhone', 899.99, 8),
            ('Samsung Galaxy S23', 'Smartphone Samsung', 799.99, 9),
            ('MacBook Pro', 'Ordinateur portable Apple', 1299.99, 5),
            ('Chemise blanche', 'Chemise classique', 49.99, 10),
            ('Robe été', 'Robe légère pour été', 79.99, 11),
        ]
        
        for name, desc, price, cat_id in products:
            conn.execute(
                'INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)',
                (name, desc, price, cat_id)
            )
        
        conn.commit()
    
    conn.close()
    # Mettre à jour les compteurs de produits
    update_product_counts()