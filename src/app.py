# ...

from flask import Flask, request, jsonify
from scraper import fetch_all_products 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ...

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_products():
    """
    Endpoint da API para buscar produtos.
    Aceita um parâmetro de query 'term'.
    Ex: /search?term=cafe
    """
    
    search_term = request.args.get('term') # termo da busca na url

    # term fornecido?
    if not search_term:
        app.logger.warning("Requisição recebida sem o parâmetro 'term'.")
        return jsonify({"success": False, "error": "Parâmetro 'term' é obrigatório."}), 400

    app.logger.info(f"Requisição recebida para buscar por: '{search_term}'")

    try:
        result = fetch_all_products(search_term)

        if result['success']:
            app.logger.info(f"Busca por '{search_term}' bem-sucedida. Retornando {result['total_found']} produtos.")
            
            # dados em JSON com status 200 
            return jsonify({
                "success": True,
                "term": search_term,
                "total_found": result['total_found'],
                "products": result['products']
            }), 200
        
        else:
            app.logger.error(f"Erro durante a busca por '{search_term}': {result['error']}")
            return jsonify({"success": False, "error": result['error']}), 500

    except Exception as e:
        app.logger.exception(f"Erro inesperado na API ao processar busca por '{search_term}': {e}")
        return jsonify({"success": False, "error": f"Erro interno no servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)