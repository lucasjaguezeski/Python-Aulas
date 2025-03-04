import argparse
import numpy as np
from scipy.optimize import minimize
import json
import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def portfolio_optimization(mu, cov_matrix, target_return):
    n_assets = len(mu)
    logging.info(f"Otimizando portfólio com {n_assets} ativos")
    
    # Função objetivo: Variância do portfólio
    def objective(w):
        return w.T @ cov_matrix @ w
    
    # Restrições
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Soma dos pesos = 1
        {'type': 'eq', 'fun': lambda w: w.T @ mu - target_return}  # Retorno alvo
    ]
    
    # Limites (pesos não-negativos)
    bounds = [(0, None) for _ in range(n_assets)]
    
    # Chute inicial
    initial_guess = np.ones(n_assets) / n_assets
    logging.info(f"Chute inicial: {initial_guess}")
    
    # Otimização
    result = minimize(objective, initial_guess, 
                     method='SLSQP', bounds=bounds, constraints=constraints)
    
    return result.x

def load_from_json(file_path):
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data['mu'], data['cov'], data['target']
    except Exception as e:
        logging.error(f"Erro ao carregar arquivo JSON: {e}")
        raise ValueError("Erro ao carregar arquivo JSON")

def opt():
    if "--input" not in sys.argv:
        # Argumentos via terminal
        logging.info("Argumentos via terminal")
        parser = argparse.ArgumentParser(description='Otimização de Portfólio de Markowitz')
        
        # Parâmetros via terminal
        parser.add_argument('--mu', type=float, nargs='+', required=True,
                        help='Retornos esperados dos ativos (separados por espaços)')
        parser.add_argument('--cov', type=float, nargs='+', required=True,
                        help='Matriz de covariância (linha única, valores separados por espaços)')
        parser.add_argument('--target', type=float, required=True,
                        help='Retorno alvo do portfólio')
        
        args = parser.parse_args()
        
        # Processar entradas
        mu = np.array(args.mu)
        n_assets = len(mu)
        cov = args.cov
        cov_matrix = np.array(args.cov).reshape(n_assets, n_assets)
        target = args.target

    elif "--input" in sys.argv:
        # Argumentos via arquivo JSON
        logging.info("Argumentos via arquivo JSON")
        idx = sys.argv.index("--input")
        file_path = sys.argv[idx+1]
        mu, cov, target = load_from_json(file_path)

    # Se nenhum argumento foi passado
    else:
        logging.error("Nenhum argumento fornecido")
        raise ValueError("Nenhum argumento fornecido")
    
    mu = np.array(mu)
    logging.info(f"Retornos esperados: {mu}")
    n_assets = len(mu)
    logging.info(f"Número de ativos: {n_assets}")
    cov_matrix = np.array(cov).reshape(n_assets, n_assets)
    logging.info(f"Matriz de covariância: {cov_matrix}")

    # Para testes, vamos adicionar um tempo de espera
    # para simular um processo mais longo
    time.sleep(30)
    
    # Validar entradas
    if cov_matrix.shape != (n_assets, n_assets):
        logging.error("Dimensões incompatíveis entre retornos e matriz de covariância")
        raise ValueError("Dimensões incompatíveis entre retornos e matriz de covariância")
    
    # Executar otimização
    weights = portfolio_optimization(mu, cov_matrix, target)
    logging.info(f"Alocação Ótima: {weights}")
    
    # Formatar saída
    logging.info("Alocação Ótima:")
    for i, w in enumerate(weights):
        logging.info(f"Ativo {i+1}: {w*100:.2f}%")

    print(weights, end='')

if __name__ == "__main__":
    opt()
    logging.info("Fim da execução")
