import argparse
import numpy as np
from scipy.optimize import minimize

def portfolio_optimization(mu, cov_matrix, target_return):
    n_assets = len(mu)
    
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
    
    # Otimização
    result = minimize(objective, initial_guess, 
                     method='SLSQP', bounds=bounds, constraints=constraints)
    
    return result.x

def main():
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
    cov_matrix = np.array(args.cov).reshape(n_assets, n_assets)
    
    # Validar entradas
    if cov_matrix.shape != (n_assets, n_assets):
        raise ValueError("Dimensões incompatíveis entre retornos e matriz de covariância")
    
    # Executar otimização
    weights = portfolio_optimization(mu, cov_matrix, args.target)
    
    # Formatar saída
    print("Alocação Ótima:")
    for i, w in enumerate(weights):
        print(f"Ativo {i+1}: {w*100:.2f}%")

if __name__ == "__main__":
    main()