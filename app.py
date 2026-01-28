import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador de Lanzamiento Vertical", layout="wide")

st.title("🚀 Simulador de Lanzamiento: Control Temporal")
st.markdown("""
Usa el deslizador para recorrer la trayectoria segundo a segundo.
Observa cómo cambia la velocidad y la altura en cada instante.
""")

# --- 1. BASE DE DATOS Y BARRA LATERAL ---
GRAVEDAD_SISTEMA_SOLAR = {
    "Tierra (9.81 m/s²)": 9.81,
    "Luna (1.62 m/s²)": 1.62,
    "Marte (3.72 m/s²)": 3.72,
    "Júpiter (24.79 m/s²)": 24.79,
    "Saturno (10.44 m/s²)": 10.44,
    "Venus (8.87 m/s²)": 8.87,
    "Mercurio (3.7 m/s²)": 3.7,
    "Sol (274 m/s²)": 274.0,
    "Plutón (0.62 m/s²)": 0.62
}

with st.sidebar:
    st.header("1. Configuración")
    planeta = st.selectbox("Lugar:", list(GRAVEDAD_SISTEMA_SOLAR.keys()))
    g = GRAVEDAD_SISTEMA_SOLAR[planeta]
    
    st.divider()
    st.header("2. Condiciones Iniciales")
    d_i = st.number_input("Altura inicial (m)", value=50.0, min_value=0.0, step=1.0)
    v_i = st.number_input("Velocidad inicial (m/s)", value=15.0, step=1.0, help="Positivo=Arriba, Negativo=Abajo")

    st.divider()
    if os.path.exists("esquema.jpeg"):
        st.image("esquema.jpeg", caption="Referencia", use_container_width=True)

# --- 2. CÁLCULOS GLOBALES (Trayectoria completa) ---
# Calcular tiempo total de vuelo para configurar el límite del slider
a = -0.5 * g
b = v_i
c = d_i
discriminante = b**2 - 4*a*c

if discriminante >= 0:
    t_total = (-b - np.sqrt(discriminante)) / (2*a)
else:
    t_total = 0

# Altura máxima global
if v_i > 0:
    t_max_h = v_i / g
    h_max_global = d_i + (v_i * t_max_h) - (0.5 * g * t_max_h**2)
else:
    h_max_global = d_i

# --- 3. EL DESLIZADOR (LA MAGIA) ---
# Creamos columnas para poner el slider en el centro
col_slider, col_metrics = st.columns([2, 1])

with col_slider:
    st.subheader("⏱️ Línea de Tiempo")
    # El slider va de 0 a t_total
    t_actual = st.slider(
        "Mueve el punto para ver la caída:",
        min_value=0.0,
        max_value=float(t_total),
        value=0.0,
        step=0.05, # Pasos finos para animación suave
        format="%.2f s"
    )

# --- 4. CÁLCULOS INSTANTÁNEOS (En el tiempo t_actual) ---
y_actual = d_i + v_i * t_actual - 0.5 * g * t_actual**2
v_actual = v_i - g * t_actual
x_actual = (t_actual / t_total) * 5 # Truco visual para moverlo en X

# Mostrar métricas en tiempo real al lado del slider
with col_metrics:
    st.metric("Tiempo", f"{t_actual:.2f} s")
    st.metric("Altura Actual", f"{y_actual:.2f} m")
    st.metric("Velocidad Actual", f"{v_actual:.2f} m/s", delta_color="off")


# --- 5. GRÁFICA INTERACTIVA ---
fig, ax = plt.subplots(figsize=(10, 5))

# A. Elementos Estáticos (Fondo)
t_arr = np.linspace(0, t_total, 200)
y_arr = d_i + v_i * t_arr - 0.5 * g * t_arr**2
x_arr = np.linspace(0, 5, 200)

# Edificio
rect = plt.Rectangle((-2, 0), 2, d_i, color='gray', alpha=0.3)
ax.add_patch(rect)
ax.plot([-2, 0], [d_i, d_i], color='black') # Techo
ax.plot([0, 0.5], [d_i, d_i], color='black', linewidth=3) # Plataforma

# Trayectoria completa (Punteada gris)
ax.plot(x_arr, y_arr, linestyle='--', color='gray', alpha=0.5, label='Trayectoria')

# B. Elementos Dinámicos (Se mueven con el slider)
# 1. El Objeto (Punto rojo grande)
ax.scatter(x_actual, y_actual, color='red', s=100, zorder=5, edgecolors='black')

# 2. Vector Velocidad (Flecha dinámica)
# La flecha cambia de tamaño y dirección. Usamos un factor de escala para que no sea gigante.
scale_v = 0.5 
color_arrow = 'blue' if v_actual > 0 else 'red' # Azul si sube, Rojo si baja

ax.arrow(x_actual, y_actual, 0, v_actual * scale_v, 
         head_width=0.2, head_length=0.3, fc=color_arrow, ec=color_arrow, label='Velocidad')

# Texto de velocidad al lado de la bola
ax.text(x_actual + 0.3, y_actual, f"v = {v_actual:.1f} m/s", color=color_arrow, fontweight='bold')

# Configuración del gráfico
ax.set_ylim(-5, h_max_global * 1.2)
ax.set_xlim(-2.5, 6)
ax.axhline(0, color='black')
ax.set_ylabel("Altura (m)")
ax.set_xlabel("Distancia horizontal simulada")
ax.set_title(f"Instante t = {t_actual:.2f} s", fontweight='bold')
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# --- 6. ECUACIONES Y TABLA ---
with st.expander("Ver Ecuaciones y Datos"):
    st.latex(r"y(t) = y_0 + v_0 t - \frac{1}{2}gt^2")
    st.latex(r"v(t) = v_0 - gt")
    st.info(f"En este instante ({t_actual}s), el término de gravedad ha restado {g*t_actual:.2f} m/s a la velocidad inicial.")
