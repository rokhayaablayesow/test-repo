from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from database import (init_db, get_db_connection, calculate_category_level, 
                     update_product_counts, get_category_parentage, 
                     check_circular_reference, create_sample_data)
from models import Category, Product

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Récupérer toutes les catégories avec leurs informations calculées
    categories = conn.execute('''
        SELECT c.*, 
               CASE 
                   WHEN c.parent_id IS NULL THEN c.name
                   ELSE (SELECT name FROM categories p WHERE p.id = c.parent_id) || ' > ' || c.name
               END as parentage_simple
        FROM categories c 
        ORDER BY c.level, c.name
    ''').fetchall()
    
    # Enrichir avec la parenté complète
    categories_enriched = []
    for cat in categories:
        cat_dict = dict(cat)
        cat_dict['parentage'] = get_category_parentage(cat['id'])
        categories_enriched.append(cat_dict)
    
    conn.close()
    return render_template('index.html', categories=categories_enriched)

@app.route('/api/category', methods=['POST'])
def create_category():
    """API unique pour créer catégorie, sous-catégorie ou sous-sous-catégorie"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        parent_id = data.get('parent_id')
        
        if not name:
            return jsonify({'error': 'Le nom est requis'}), 400
        
        conn = get_db_connection()
        
        # Vérifier les références circulaires si parent_id est fourni
        if parent_id:
            # Vérifier que le parent existe
            parent = conn.execute('SELECT id FROM categories WHERE id = ?', (parent_id,)).fetchone()
            if not parent:
                conn.close()
                return jsonify({'error': 'Catégorie parent introuvable'}), 400
            
            # Calculer le niveau
            level = calculate_category_level(parent_id, conn) + 1
            
            # Vérifier le niveau maximum (3 niveaux max)
            if level > 3:
                conn.close()
                return jsonify({'error': 'Maximum 3 niveaux de catégories autorisés'}), 400
        else:
            level = 1
        
        # Insérer la nouvelle catégorie
        cursor = conn.execute(
            'INSERT INTO categories (name, description, parent_id, level) VALUES (?, ?, ?, ?)',
            (name, description, parent_id, level)
        )
        
        category_id = cursor.lastrowid
        conn.commit()
        
        # Récupérer la catégorie créée
        category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
        conn.close()
        
        # Mettre à jour les compteurs
        update_product_counts()
        
        return jsonify({
            'success': True,
            'category': dict(category),
            'parentage': get_category_parentage(category_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product', methods=['POST'])
def create_product():
    """API unique pour créer un produit"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        price = data.get('price')
        category_id = data.get('category_id')
        
        if not name or not price or not category_id:
            return jsonify({'error': 'Nom, prix et catégorie sont requis'}), 400
        
        try:
            price = float(price)
        except ValueError:
            return jsonify({'error': 'Prix invalide'}), 400
        
        conn = get_db_connection()
        
        # Vérifier que la catégorie existe
        category = conn.execute('SELECT id FROM categories WHERE id = ?', (category_id,)).fetchone()
        if not category:
            conn.close()
            return jsonify({'error': 'Catégorie introuvable'}), 400
        
        # Insérer le nouveau produit
        cursor = conn.execute(
            'INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)',
            (name, description, price, category_id)
        )
        
        product_id = cursor.lastrowid
        conn.commit()
        
        # Récupérer le produit créé
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        
        # Mettre à jour les compteurs de produits
        update_product_counts()
        
        return jsonify({
            'success': True,
            'product': dict(product)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Récupérer toutes les catégories avec leurs informations"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY level, name').fetchall()
    conn.close()
    
    categories_list = []
    for cat in categories:
        cat_dict = dict(cat)
        cat_dict['parentage'] = get_category_parentage(cat['id'])
        categories_list.append(cat_dict)
    
    return jsonify(categories_list)

@app.route('/api/categories/parents/<int:category_id>')
def get_available_parents(category_id):
    """Récupérer les parents disponibles pour éviter les boucles infinies"""
    conn = get_db_connection()
    
    # Récupérer toutes les catégories sauf la catégorie elle-même et ses descendants
    all_categories = conn.execute('SELECT * FROM categories WHERE id != ?', (category_id,)).fetchall()
    
    available_parents = []
    for cat in all_categories:
        # Vérifier qu'il n'y a pas de référence circulaire
        if not check_circular_reference(category_id, cat['id']):
            # Vérifier que le niveau ne dépasse pas 3
            if cat['level'] < 3:
                available_parents.append(dict(cat))
    
    conn.close()
    return jsonify(available_parents)

@app.route('/api/products')
def get_products():
    """Récupérer tous les produits avec leurs catégories"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.name
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(product) for product in products])

@app.route('/category/<int:category_id>')
def view_category(category_id):
    """Afficher une catégorie spécifique avec ses produits"""
    conn = get_db_connection()
    
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    if not category:
        conn.close()
        flash('Catégorie introuvable')
        return redirect(url_for('index'))
    
    # Récupérer les produits de cette catégorie
    products = conn.execute(
        'SELECT * FROM products WHERE category_id = ? ORDER BY name',
        (category_id,)
    ).fetchall()
    
    # Récupérer les sous-catégories
    subcategories = conn.execute(
        'SELECT * FROM categories WHERE parent_id = ? ORDER BY name',
        (category_id,)
    ).fetchall()
    
    conn.close()
    
    category_dict = dict(category)
    category_dict['parentage'] = get_category_parentage(category_id)
    
    return render_template('category.html', 
                         category=category_dict,
                         products=[dict(p) for p in products],
                         subcategories=[dict(s) for s in subcategories])

@app.route('/delete/category/<int:id>')
def delete_category(id):
    """Supprimer une catégorie"""
    conn = get_db_connection()
    
    # Vérifier s'il y a des sous-catégories
    subcategories = conn.execute('SELECT COUNT(*) FROM categories WHERE parent_id = ?', (id,)).fetchone()[0]
    if subcategories > 0:
        conn.close()
        flash('Impossible de supprimer: cette catégorie a des sous-catégories')
        return redirect(url_for('index'))
    
    # Vérifier s'il y a des produits
    products = conn.execute('SELECT COUNT(*) FROM products WHERE category_id = ?', (id,)).fetchone()[0]
    if products > 0:
        conn.close()
        flash('Impossible de supprimer: cette catégorie a des produits')
        return redirect(url_for('index'))
    
    # Supprimer la catégorie
    conn.execute('DELETE FROM categories WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    update_product_counts()
    flash('Catégorie supprimée avec succès')
    return redirect(url_for('index'))

@app.route('/delete/product/<int:id>')
def delete_product(id):
    """Supprimer un produit"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    update_product_counts()
    flash('Produit supprimé avec succès')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Page d'inscription"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not first_name or not email or not password:
            flash('Tous les champs sont requis')
            return render_template('signup.html')
        
        # Here you would typically:
        # 1. Hash the password
        # 2. Save user to database
        # 3. Send confirmation email
        # For demo purposes, we'll just flash a success message
        
        flash(f'Compte créé avec succès pour {first_name}! Vérifiez votre email.')
        return redirect(url_for('index'))
    
    return render_template('signup.html')

@app.route('/login')
def login():
    """Page de connexion (placeholder)"""
    flash('Page de connexion - À implémenter')
    return redirect(url_for('signup'))

if __name__ == '__main__':
    init_db()
    create_sample_data()
    update_product_counts()
    app.run(debug=True, host='0.0.0.0', port=5000)