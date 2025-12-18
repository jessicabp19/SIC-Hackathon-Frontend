"""
Frontend Streamlit - Portfolio Optimizer
Samsung Innovation Campus 2025

Este archivo consume el backend desplegado en Railway.
Cada sección está comentada para entender qué hace.
"""
import streamlit as st
import requests
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURACIÓN
# ============================================================
# URL del backend en Railway (cambiar si es diferente)
API_URL = "https://sic-hackathon-backend-production.up.railway.app"

# Configuración de la página de Streamlit
# - page_title: título que aparece en la pestaña del navegador
# - page_icon: emoji o imagen para la pestaña
# - layout: "wide" usa todo el ancho de la pantalla
st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="📈",
    layout="wide"
)


st.markdown("""
<style>
/* Fondo general */
.stApp {
    background-color: #f8fafc; /* gris muy claro */
    color: #000000;            /* texto negro global */
}

/* Cajas principales */
.box {
    background-color: #ffffff; /* blanco */
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    color: #000000;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

/* Contenedor del chat */
.chat-container {
    background-color: #f1f5f9; /* gris claro */
    border-radius: 12px;
    padding: 15px;
    height: 400px;
    overflow-y: auto;
    color: #000000;
    border: 1px solid #cbd5e1;
}

/* Mensajes */
.chat-message {
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
    color: #000000;
    font-size: 14px;
}

/* Mensaje del usuario */
.user-message {
    background-color: #dbeafe; /* azul claro */
    color: #000000;
    text-align: right;
}

/* Mensaje del bot */
.bot-message {
    background-color: #e5e7eb; /* gris claro */
    color: #000000;
}

/* Inputs */
input, textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #94a3b8 !important;
}

/* Placeholder */
::placeholder {
    color: #64748b;
}

/* Scrollbar suave */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #94a3b8;
    border-radius: 10px;
}

/* Ocultar branding Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE (Estado de la aplicación)
# ============================================================
# En Streamlit, cada vez que interactúas con algo, la página se recarga.
# session_state permite guardar datos entre recargas (como useState en React)

# Inicializar el historial del chat si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Inicializar resultados del optimizador
if "optimization_result" not in st.session_state:
    st.session_state.optimization_result = None

# Estado del login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ============================================================
# FUNCIONES PARA LLAMAR AL BACKEND
# ============================================================

def llamar_chatbot(mensaje: str) -> dict:
    """
    Envía un mensaje al chatbot del backend.

    Args:
        mensaje: Texto del usuario

    Returns:
        Diccionario con 'response' y 'categoria'
    """
    try:
        # requests.post() hace una petición POST al backend
        # json={} envía el body como JSON
        # timeout=30 espera máximo 30 segundos
        response = requests.post(
            f"{API_URL}/api/chatbot/message",
            json={"message": mensaje},
            timeout=30
        )
        # .json() convierte la respuesta a diccionario de Python
        return response.json()
    except Exception as e:
        return {"response": f"Error de conexión: {str(e)}", "categoria": "error"}


def obtener_sugerencias() -> list:
    """
    Obtiene las preguntas sugeridas del chatbot.
    """
    try:
        response = requests.get(
            f"{API_URL}/api/chatbot/suggestions",
            timeout=10
        )
        return response.json()
    except:
        return ["¿Qué es invertir?", "¿Qué es el riesgo?"]


def buscar_empresas(query: str) -> list:
    """
    Busca empresas por nombre en el S&P 500.
    """
    try:
        response = requests.get(
            f"{API_URL}/api/portfolio/search",
            params={"query": query},  # params={} agrega ?query=... a la URL
            timeout=10
        )
        data = response.json()
        return data.get("matches", [])
    except:
        return []


def analizar_portafolio(tickers: list) -> dict:
    """
    Llama al optimizador del backend.

    Args:
        tickers: Lista de símbolos (ej: ["AAPL", "MSFT"])

    Returns:
        Resultado del análisis con pesos óptimos
    """
    try:
        response = requests.post(
            f"{API_URL}/api/portfolio/analyze",
            json={"tickers": tickers},
            timeout=180  # 3 minutos porque el LSTM puede tardar
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# PÁGINA DE LOGIN
# ============================================================
# Esta es una autenticación simple (no segura para producción)

if not st.session_state.logged_in:
    # Centrar el formulario de login
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🔐 Portfolio Optimizer")
        st.markdown("**Samsung Innovation Campus 2025**")
        st.markdown("---")

        # st.text_input() crea un campo de texto
        # El valor se guarda en la variable 'usuario'
        usuario = st.text_input("Usuario", placeholder="admin")

        # type="password" oculta los caracteres
        password = st.text_input("Contraseña", type="password", placeholder="admin")

        # st.button() retorna True cuando se hace click
        if st.button("Ingresar", type="primary", use_container_width=True):
            if usuario == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.rerun()  # Recarga la página para mostrar el dashboard
            else:
                # st.error() muestra un mensaje de error en rojo
                st.error("Usuario o contraseña incorrectos")

        st.markdown("---")
        st.caption("Credenciales de prueba: admin / admin")

# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
else:
    # ========== SIDEBAR (Menú lateral) ==========
    with st.sidebar:
        st.title("📊 Portfolio Optimizer")
        st.markdown("---")

        # Menú de navegación
        # st.radio() crea botones de opción (como radio buttons en HTML)
        pagina = st.radio(
            "Navegación",
            ["💬 Chatbot", "📈 Optimizador", "🔍 Buscar Empresas"],
            label_visibility="collapsed"  # Oculta el label "Navegación"
        )

        st.markdown("---")

        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.chat_history = []
            st.rerun()

        st.markdown("---")
        st.caption("Samsung Innovation Campus 2025")
        st.caption("Herramienta educativa")

    # ========== PÁGINA: CHATBOT ==========
    if pagina == "💬 Chatbot":
        st.title("💬 Asistente de Inversión")
        st.markdown("Pregúntame sobre conceptos de inversión, riesgo, diversificación y más.")

        # Crear dos columnas: chat (izq) y sugerencias (der)
        col_chat, col_sugerencias = st.columns([3, 1])

        with col_chat:
            # Contenedor del historial de chat
            chat_container = st.container()

            with chat_container:
                # Mostrar historial de mensajes
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>Tú:</strong> {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <strong>🤖 Asistente:</strong> {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)

            # Input para nuevo mensaje
            # key= es un identificador único para el componente
            mensaje = st.text_input(
                "Escribe tu pregunta:",
                key="chat_input",
                placeholder="Ej: ¿Qué es el riesgo?"
            )

            if st.button("Enviar", type="primary"):
                if mensaje:
                    # Agregar mensaje del usuario al historial
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": mensaje
                    })

                    # Llamar al backend
                    respuesta = llamar_chatbot(mensaje)

                    # Agregar respuesta al historial
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": respuesta.get("response", "Sin respuesta")
                    })

                    st.rerun()  # Recargar para mostrar nuevos mensajes

        with col_sugerencias:
            st.markdown("### 💡 Sugerencias")

            # Obtener y mostrar sugerencias
            sugerencias = obtener_sugerencias()

            for sugerencia in sugerencias:
                # Cada sugerencia es un botón que envía ese mensaje
                if st.button(sugerencia, key=f"sug_{sugerencia}", use_container_width=True):
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": sugerencia
                    })
                    respuesta = llamar_chatbot(sugerencia)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": respuesta.get("response", "Sin respuesta")
                    })
                    st.rerun()

    # ========== PÁGINA: OPTIMIZADOR ==========
    elif pagina == "📈 Optimizador":
        st.title("📈 Optimizador de Portafolio")
        st.markdown("Ingresa los tickers de las empresas que quieres analizar (mínimo 2).")

        # Input para tickers
        tickers_input = st.text_input(
            "Tickers (separados por coma):",
            value="AAPL, MSFT, TSLA",
            placeholder="Ej: AAPL, MSFT, GOOGL, TSLA"
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            # Botón para analizar
            if st.button("🚀 Analizar", type="primary", use_container_width=True):
                # Convertir string a lista de tickers
                tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

                if len(tickers) < 2:
                    st.error("Ingresa al menos 2 tickers")
                else:
                    # st.spinner() muestra un indicador de carga
                    with st.spinner("Analizando... (puede tardar 1-2 minutos)"):
                        resultado = analizar_portafolio(tickers)
                        st.session_state.optimization_result = resultado

        # Mostrar resultados si existen
        if st.session_state.optimization_result:
            resultado = st.session_state.optimization_result

            if resultado.get("success"):
                # ========== REPORTE DE ESTRATEGIA QUANT ==========
                pesos = resultado["pesos_optimos"]
                var_95 = resultado.get("var_95", 0)
                tiempo = resultado["tiempo_ejecucion"]
                sharpe = resultado["sharpe_ratio"]
                metricas = resultado["metricas_validacion"]

                # Título del reporte
                st.header("REPORTE DE ESTRATEGIA QUANT")
                st.caption(f"Tiempo de proceso: {tiempo:.2f} segundos")

                st.markdown("---")

                # ===== SECCIÓN 1: MÉTRICAS PRINCIPALES =====
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        label="Sharpe Ratio",
                        value=f"{sharpe:.4f}",
                        help="Rendimiento ajustado al riesgo. Mayor = mejor."
                    )

                with col2:
                    st.metric(
                        label="VaR 95%",
                        value=f"{var_95*100:.2f}%",
                        help="Pérdida máxima esperada con 95% de confianza en 30 días."
                    )

                with col3:
                    st.metric(
                        label="vs Buy & Hold",
                        value=f"{metricas['ganancia_vs_buy_hold']:.2f}%",
                        help="Ganancia del portafolio optimizado vs comprar igual de todo."
                    )

                # Explicación del VaR
                st.info(f"Existe un 5% de probabilidad de perder más del {abs(var_95*100):.2f}% en 30 días.")

                st.markdown("---")

                # ===== SECCIÓN 2: DISTRIBUCIÓN RECOMENDADA =====
                st.subheader("Distribución Recomendada")

                # Gráfica de barras
                fig, ax = plt.subplots(figsize=(10, 5))
                colores = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
                bars = ax.bar(
                    pesos.keys(),
                    [v * 100 for v in pesos.values()],
                    color=colores[:len(pesos)]
                )
                ax.set_ylabel("Porcentaje (%)")
                ax.set_title("Asignación de Capital")
                ax.set_ylim(0, max([v * 100 for v in pesos.values()]) + 10)

                for bar, valor in zip(bars, pesos.values()):
                    ax.text(
                        bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 1,
                        f"{valor*100:.1f}%",
                        ha='center',
                        fontsize=11,
                        fontweight='bold'
                    )

                st.pyplot(fig)

                # Tabla de distribución
                st.markdown("**Detalle de asignación:**")
                for ticker, peso in pesos.items():
                    st.write(f"- **{ticker}**: {peso*100:.2f}%")

                st.markdown("---")

                # ===== SECCIÓN 3: PARÁMETROS PROYECTADOS =====
                st.subheader("Parámetros Proyectados (Anualizados)")

                # Explicación expandible
                with st.expander("¿Qué significan estos parámetros?"):
                    st.markdown("""
                    - **Drift (μ)**: Rendimiento esperado anualizado. Es la "tendencia" que predice la IA.
                    - **Volatilidad (σ)**: Qué tanto fluctúa el precio. Mayor volatilidad = mayor riesgo.
                    """)

                # Tabla con los parámetros
                params_data = []
                for p in resultado["parametros_proyectados"]:
                    params_data.append({
                        "Ticker": p["ticker"],
                        "Drift (μ)": f"{p['drift_anual']:.2f}%",
                        "Volatilidad (σ)": f"{p['volatilidad_anual']:.2f}%"
                    })
                st.table(params_data)

                st.markdown("---")

                # ===== SECCIÓN 4: VALIDACIÓN DEL MODELO =====
                st.subheader("Validación del Modelo LSTM")

                with st.expander("¿Qué significan estas métricas?"):
                    st.markdown("""
                    - **RMSE Modelo**: Error de predicción de la red neuronal. Más bajo = mejor.
                    - **RMSE Baseline**: Error si predijéramos "sin cambio". Sirve de referencia.
                    - **vs Buy & Hold**: Compara el portafolio optimizado vs comprar igual de todo y esperar.
                    """)

                col1, col2 = st.columns(2)
                col1.metric("RMSE Modelo", f"{metricas['rmse_modelo']:.6f}")
                col2.metric("RMSE Baseline", f"{metricas['rmse_baseline']:.6f}")

            else:
                st.error(f"❌ Error: {resultado.get('detail', resultado.get('error', 'Error desconocido'))}")

    # ========== PÁGINA: BUSCAR EMPRESAS ==========
    elif pagina == "🔍 Buscar Empresas":
        st.title("🔍 Buscar Empresas del S&P 500")
        st.markdown("Busca empresas por nombre para encontrar su ticker.")

        query = st.text_input(
            "Nombre de la empresa:",
            placeholder="Ej: Apple, Tesla, Microsoft..."
        )

        if query and len(query) >= 2:
            with st.spinner("Buscando..."):
                resultados = buscar_empresas(query)

            if resultados:
                st.markdown("### Resultados:")

                for empresa in resultados:
                    # st.columns dentro de un loop para crear una "tabla"
                    col1, col2 = st.columns([3, 1])
                    col1.write(empresa["nombre"])
                    col2.code(empresa["ticker"])  # st.code() muestra texto con estilo de código
            else:
                st.info("No se encontraron resultados")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    <p>⚠️ Esta herramienta es educativa y no constituye asesoría financiera.</p>
    <p>Samsung Innovation Campus 2025 - Hackathon</p>
</div>
""", unsafe_allow_html=True)
