# ...

from flask import Flask, request, jsonify, render_template 
from scraper import fetch_all_products
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ...

app = Flask(__name__)

# rota com html
@app.route('/', methods=['GET'])
def index():
    search_term = request.args.get('term', None)
    return render_template('index.html', initial_search_term=search_term)

# rota para api 
@app.route('/api/search', methods=['GET'])
def api_search():
    search_term = request.args.get('term')
    if not search_term:
        app.logger.warning("API: Requisição recebida sem o parâmetro 'term'.")
        return jsonify({"success": False, "error": "Parâmetro 'term' é obrigatório."}), 400

    app.logger.info(f"API: Iniciando busca por: '{search_term}'")
    try:
        result = fetch_all_products(search_term)
        if result['success']:
            app.logger.info(f"API: Busca por '{search_term}' concluída. {result['total_found']} produtos.")
            return jsonify({
                "success": True,
                "term": search_term,
                "total_found": result['total_found'],
                "products": result['products']
            }), 200
        else:
            app.logger.error(f"API: Erro na busca por '{search_term}': {result['error']}")
            return jsonify({"success": False, "error": result['error']}), 500
    except Exception as e:
        app.logger.exception(f"API: Erro inesperado ao processar busca por '{search_term}': {e}")
        return jsonify({"success": False, "error": f"Erro interno no servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)