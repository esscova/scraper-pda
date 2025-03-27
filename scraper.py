# ...

import requests
import json
import time
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ...

API_URL = "https://api.vendas.gpa.digital/pa/search/search"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Content-Type': 'application/json',
    'Origin': 'https://www.paodeacucar.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paodeacucar.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'TE': 'trailers'
}
DEFAULT_PAYLOAD_TEMPLATE = {
    # "terms": será definido pelo parâmetro da função
    "page": 1,
    "sortBy": "relevance",
    "resultsPerPage": 8, # o que a API usa para calcular totalPages
    "allowRedirect": True,
    "storeId": 461,      
    "department": "ecom",
    "customerPlus": True,
    "partner": "linx"
}
REQUEST_TIMEOUT = 20 # timeout da requisição
DELAY_BETWEEN_REQUESTS = 0.5 # pausa entre páginas

def fetch_all_products(search_term: str):
    """
    Busca todos os produtos para um determinado termo na API do GPA.

    Args:
        search_term: O termo a ser buscado (ex: "cafe").

    Returns:
        Um dicionário contendo:
        - 'success' (bool): True se a busca foi concluída (mesmo sem produtos), False se ocorreu erro.
        - 'total_found' (int): Número total de produtos encontrados (se sucesso).
        - 'products' (list): Lista de dicionários de produtos (se sucesso).
        - 'error' (str): Mensagem de erro (se success=False).
    """
    all_products = []
    total_pages = 1
    current_page = 1
    total_products_reported = 0

    logging.info(f"Iniciando busca por '{search_term}'...")

    while current_page <= total_pages:
        # payload para a página atual
        payload = DEFAULT_PAYLOAD_TEMPLATE.copy()
        payload['terms'] = search_term
        payload['page'] = current_page

        if current_page == 1 or current_page % 10 == 0 or current_page == total_pages:
             logging.info(f"Buscando página {current_page} de {total_pages} para '{search_term}'...")
        else:
             logging.debug(f"Buscando página {current_page} de {total_pages} para '{search_term}'...")


        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if current_page == 1:
                 total_pages = data.get('totalPages', 0)
                 total_products_reported = data.get('totalProducts', 0)

                 logging.info(f"API reportou {total_products_reported} produtos em {total_pages} páginas.")
                 if total_pages == 0:
                      logging.info("Nenhuma página/produto encontrado.")
                      break 

            products_on_page = data.get('products', [])
            if products_on_page:
                all_products.extend(products_on_page)
                logging.debug(f"  -> {len(products_on_page)} produtos adicionados da pag {current_page}. Total: {len(all_products)}")
            else:
                logging.warning(f"  -> Nenhum produto encontrado na página {current_page}, embora esperada.")

            current_page += 1

            if current_page <= total_pages:
                time.sleep(DELAY_BETWEEN_REQUESTS)

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout ao buscar página {current_page}. Tentando novamente em 5 segundos...")
            time.sleep(5)

        except requests.exceptions.HTTPError as e:
             logging.error(f"Erro HTTP {e.response.status_code} na página {current_page}: {e}")
             logging.error(f"Resposta do servidor: {e.response.text[:500]}") # Loga início da resposta
             return {'success': False, 'error': f"Erro HTTP {e.response.status_code} na página {current_page}"}

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de conexão/requisição na página {current_page}: {e}")
            return {'success': False, 'error': f"Erro de requisição na página {current_page}: {e}"}

        except json.JSONDecodeError:
            logging.error(f"Erro ao decodificar JSON da resposta da página {current_page}.")
            logging.error(f"Conteúdo recebido (início): {response.text[:500]}")
            return {'success': False, 'error': f"Resposta inválida (não JSON) na página {current_page}"}

        except Exception as e:
             logging.exception(f"Erro inesperado durante o processamento da página {current_page}: {e}")
             return {'success': False, 'error': f"Erro inesperado na página {current_page}: {e}"}

    # final do loop

    final_count = len(all_products)
    logging.info(f"Busca por '{search_term}' concluída. Total de {final_count} produtos coletados.")
    
    if final_count != total_products_reported and total_products_reported > 0 :
         logging.warning(f"Contagem final ({final_count}) difere do total reportado pela API ({total_products_reported}).")

    return {'success': True, 'total_found': final_count, 'products': all_products}

# testes 
if __name__ == "__main__":
    print("Executando scraper.py diretamente para teste...")
    # teste com 'cafe'
    results_cafe = fetch_all_products(search_term="cafe")
    if results_cafe['success']:
        print(f"\nTeste 'cafe': Sucesso! Encontrados {results_cafe['total_found']} produtos.")
        # print(json.dumps(results_cafe['products'][:2], indent=2, ensure_ascii=False)) # Mostra os 2 primeiros
    else:
        print(f"\nTeste 'cafe': Falhou! Erro: {results_cafe['error']}")

    # algo que não exista
    # results_nada = fetch_all_products(search_term="xyzqwertyproductonaoexiste")
    # if results_nada['success']:
    #     print(f"\nTeste 'xyz...': Sucesso! Encontrados {results_nada['total_found']} produtos.")
    # else:
    #     print(f"\nTeste 'xyz...': Falhou! Erro: {results_nada['error']}")