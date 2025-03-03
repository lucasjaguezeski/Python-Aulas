import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.animation as animation

# Parâmetros da simulação
nx, ny, nz = 50, 50, 50  # Grid 3D
dx, dy, dz = 0.1, 0.1, 0.1  # Passos espaciais
dt = 0.001  # Passo temporal
alpha = 0.5  # Difusividade térmica
timesteps = 500  # Número de iterações

# Inicialização do grid 3D
u = np.zeros((nx, ny, nz))

# Condição inicial: fonte de calor no centro
u[nx//2-5:nx//2+5, ny//2-5:ny//2+5, nz//2-5:nz//2+5] = 100.0

# Função para resolver a equação do calor e salvar o histórico
def solve_heat_equation(u):
    u_hist = []
    for _ in range(timesteps):
        un = u.copy()
        u[1:-1, 1:-1, 1:-1] = un[1:-1, 1:-1, 1:-1] + alpha * dt * (
            (un[2:, 1:-1, 1:-1] - 2*un[1:-1, 1:-1, 1:-1] + un[:-2, 1:-1, 1:-1])/dx**2 +
            (un[1:-1, 2:, 1:-1] - 2*un[1:-1, 1:-1, 1:-1] + un[1:-1, :-2, 1:-1])/dy**2 +
            (un[1:-1, 1:-1, 2:] - 2*un[1:-1, 1:-1, 1:-1] + un[1:-1, 1:-1, :-2])/dz**2)
        u_hist.append(u.copy())
    return u, u_hist

# Executar simulação e capturar o histórico
u_final, u_hist = solve_heat_equation(u)

# Visualização 3D
def plot_3d(data, title):
    x = np.linspace(0, nx*dx, nx)
    y = np.linspace(0, ny*dy, ny)
    z = np.linspace(0, nz*dz, nz)
    X, Y, Z = np.meshgrid(x, y, z)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(X, Y, Z, c=data.flatten(), cmap=cm.viridis)
    plt.title(title)
    plt.colorbar(scatter)
    plt.show()

plot_3d(u, "Condição Inicial")
plot_3d(u_final, "Estado Final")

# Animação da propagação
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
X, Y, Z = np.mgrid[0:nx*dx:dx, 0:ny*dy:dy, 0:nz*dz:dz]

def update(frame):
    ax.clear()
    ax.set_title(f"Propagação do Calor - Passo {frame}")
    scatter = ax.scatter(X, Y, Z, c=u_hist[frame].flatten(), cmap=cm.viridis)
    return scatter,

ani = animation.FuncAnimation(fig, update, frames=len(u_hist), interval=50)
plt.show()
