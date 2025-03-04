from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import threading
import uuid
import os
import ast

app = Flask(__name__)
auth = HTTPBasicAuth()
lock = threading.Lock()
processo_ativo = False

# Store task information
tasks = {}

users = {
    "usuario": generate_password_hash("senha")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def executar_script(task_id, mu, cov, target):
    global processo_ativo
    try:
        # Criar um nome de arquivo de log único para esta tarefa
        log_file = f"logs\\logs_{task_id}.log"
        
        # Executar o script com logs direcionados para um arquivo específico
        # Flatten the covariance matrix to pass as a list of strings
        flattened_cov = []
        for sublist in cov:
            if isinstance(sublist, list):
                flattened_cov.extend(map(str, sublist))
            else:  # Caso já esteja achatado (fallback)
                flattened_cov.append(str(sublist))
        
        # Monta o comando corretamente
        command = [
            "python", "portfolio_opt.py",
            "--mu", *map(str, mu),
            "--cov", *flattened_cov,
            "--target", str(target)
        ]
        
        # Executa o processo
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        exec_result = ast.literal_eval(result.stdout.replace(" ", ","))   

        # Processar o log
        with open(log_file, 'w') as f:
            f.write("LOGS DE EXECUCAO:\n")
            f.write(result.stderr)
        
        # Atualizar status da tarefa
        with lock:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['result'] = exec_result
            
    except Exception as e:
        with lock:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = str(e)
    finally:
        with lock:
            tasks[task_id]['active'] = False
            processo_ativo = False

@app.route("/executar-modelo", methods=["POST"])
@auth.login_required
def executar_modelo():
    global processo_ativo

    with lock:
        if processo_ativo:
            return jsonify({"error": "Já existe um processo em execução"}), 429
    
        processo_ativo = True
    # Gerar um ID único para a tarefa
    task_id = str(uuid.uuid4())
    
    data = request.get_json()
    
    # Validação básica
    required_fields = ['mu', 'cov', 'target']
    for field in required_fields:
        if field not in data:
            with lock:
                processo_ativo = False
            return jsonify({"error": f"Campo obrigatório faltando: {field}"}), 400
    
    # Registrar a tarefa
    tasks[task_id] = {
        'status': 'running',
        'active': True,
        'mu': data['mu'],
        'cov': data['cov'],
        'target': data['target']
    }
    
    # Inicia a execução em thread separada
    threading.Thread(
        target=executar_script,
        args=(task_id, data['mu'], data['cov'], data['target'])
    ).start()
    
    return jsonify({"task_id": task_id, "status": "Processo iniciado"}), 202

@app.route("/tasks/<task_id>", methods=["GET"])
@auth.login_required
def get_task_status(task_id):
    # Verificar se a tarefa existe
    if task_id not in tasks:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    
    # Retornar informações da tarefa
    task_info = tasks[task_id].copy()
    
    # Se a tarefa estiver concluída, tentar ler os logs
    if task_info['status'] in ['completed', 'failed']:
        try:
            log_file = f"logs\\logs_{task_id}.log"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    # Dividir logs em linhas para criar array
                    task_info['logs'] = f.read().splitlines()
            
            # Limpar informações sensíveis antes de retornar
            task_info.pop('mu', None)
            task_info.pop('cov', None)
            task_info.pop('target', None)
        except Exception as e:
            task_info['log_error'] = str(e)
    
    return jsonify(task_info)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)