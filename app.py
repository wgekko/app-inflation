import streamlit as st
import random
import time
import datetime
#from datetime import datetime


# --- CONFIGURACIÓN INICIAL DE LA PÁGINA Y ESTADO ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Ocultar el sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Inicializamos el 'session_state' para el control de flujo
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'animation_finished' not in st.session_state:
    st.session_state.animation_finished = False

# --- ESTILOS CSS ---
def set_theme(theme='dark'):
    """Función para cambiar entre el tema oscuro (Matrix) y el claro (página en blanco)."""
    if theme == 'dark':
        st.markdown("""
            <style>
            /* --- CONFIGURACIÓN GENERAL --- */
            header, footer, #MainMenu { visibility: hidden; }
            .stApp {
                background-color: black;
                color: #00FF41;
                font-family: 'monospace', courier;
            }
            /* --- AJUSTE PARA QUITAR RECUADROS --- */
            /* Contenedor del texto final */
            .terminal-container {
                background-color: transparent !important;
                border: none !important;
            }
            /* Campo de texto */
            .stTextInput > div > div > input {
                font-family: 'monospace', courier !important;
                background-color: transparent;
                color: #00FF41;
                border: none; /* Se quita el borde completo */
                border-bottom: 2px solid #00FF41; /* Se deja solo un subrayado */
            }
            /* texto de formulario */
            .custom-label {
                color: #00FF41;
                font-weight: bold;
                font-size: 16px;
            }
            /* Botón de conexión */
            .stButton > button {
                font-family: 'monospace', courier !important;
                background-color: transparent;
                color: #00FF41;
                border: 1px solid #00FF41; /* Se mantiene el borde para que parezca un botón */
            }
            .stButton > button:hover {
                border-color: #C8FFC8;
                color: #C8FFC8;
            }
            </style>
            """, unsafe_allow_html=True)
    else: # Tema 'light' o en blanco
        st.markdown("""
            <style>
            header, footer, #MainMenu { visibility: hidden; }
            .stApp { background-color: white; }
            </style>
            """, unsafe_allow_html=True)

# --- FASE 1: LLUVIA DIGITAL ---
def run_digital_rain(duration_seconds):
    # (Esta función no necesita cambios)
    CHARS = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789"
    FONT_SIZE, NUM_COLUMNS, TAIL_LENGTH = 16, 90, 25
    placeholder = st.empty()
    drops = [1] * NUM_COLUMNS
    start_time = datetime.datetime.now()
    while (datetime.datetime.now() - start_time).total_seconds() < duration_seconds:
        html_content = '<div style="position: fixed; top: 0; left: 15%; width: 70%; height: 100%; overflow: hidden; font-family: monospace;">'
        for i in range(NUM_COLUMNS):
            head_char = random.choice(CHARS)
            head_x, head_y = i * FONT_SIZE, drops[i] * FONT_SIZE
            html_content += f'<span style="position: absolute; left: {head_x}px; top: {head_y}px; color: #C8FFC8;">{head_char}</span>'
            for j in range(1, TAIL_LENGTH):
                tail_y = head_y - (j * FONT_SIZE)
                if tail_y < 0: continue
                opacity = 1.0 - (j / TAIL_LENGTH)
                color = f'rgba(0, 255, 65, {opacity})'
                html_content += f'<span style="position: absolute; left: {head_x}px; top: {tail_y}px; color: {color};">{random.choice(CHARS)}</span>'
            drops[i] += 1
            if drops[i] * FONT_SIZE > 1000 and random.random() > 0.975: drops[i] = 0
        html_content += '</div>'
        placeholder.markdown(html_content, unsafe_allow_html=True)
        time.sleep(0.05)
    placeholder.empty()

# --- FASE 2: CURSOR PARPADEANTE ---
def run_blinking_cursor(duration_seconds):
    # (Esta función no necesita cambios)
    placeholder, cursor_char = st.empty(), "█"
    start_time = datetime.datetime.now()
    visible = True
    while (datetime.datetime.now() - start_time).total_seconds() < duration_seconds:
        content = f'<div class="terminal-container">{cursor_char if visible else "&nbsp;"}</div>'
        placeholder.markdown(content, unsafe_allow_html=True)
        visible = not visible
        time.sleep(0.5)
    placeholder.empty()

# --- FASE 3 Y 4: ESCRITURA SIMULADA ---
def run_typing_simulation(lines_to_type):
    """MODIFICADA: Ahora devuelve el texto final en lugar de mostrarlo."""
    placeholder = st.empty()
    full_text = ""
    for line_info in lines_to_type:
        line_text, pause_after = line_info["text"], line_info.get("pause", 1.0)
        for i in range(len(line_text) + 1):
            current_typed = line_text[:i]
            cursor = "█" if int(time.time() * 2) % 2 == 0 else " "
            content = f'<div class="terminal-container" style="white-space: pre;">{full_text}{current_typed}{cursor}</div>'
            placeholder.markdown(content, unsafe_allow_html=True)
            time.sleep(random.uniform(0.05, 0.1))
        full_text += line_text + "\n"
        time.sleep(pause_after)
    placeholder.empty()
    return full_text

# --- SECUENCIA PRINCIPAL DE LA APLICACIÓN ---
if not st.session_state.access_granted:
    set_theme('dark')

    # La animación completa solo se ejecuta una vez.
    if not st.session_state.animation_finished:
        run_digital_rain(duration_seconds=9)
        time.sleep(3)
        run_blinking_cursor(duration_seconds=5)
        time.sleep(2)
        tsec = datetime.datetime.now()
        
        TEXT_SEQUENCE = [
            #{"text": "Call trans opt: received. 9-30-25 13:24:18 REC:Log>", "pause": 1.5},
            {"text": f"Call trans opt: received. {tsec.strftime('%m-%d-%y %H:%M:%S')} REC:Log>", "pause": 1.5},            
            {"text": "Trace program: running.....", "pause": 1.5},
            {"text": "Signal acquisition complete. Establishing link with node: [RED32|@shadowline].", "pause": 1.5},
            {"text": "Handshake confirmed. Decrypting source signature...", "pause": 1.5},
            {"text": "Entropy offset detected. Initiating noise isolation protocol.", "pause": 1.5},
            {"text": "Routing signal through secure relay... Awaiting identity match-probability: 92.4%.", "pause": 1.5},
            #{"text": "Uplink stabilized. Querying target metadata...", "pause": 1.5},
            {"text": "Response received: Origin obscured – masking layer: LVL3-GHOST", "pause": 1.5},
            #{"text": "Cross-referencing deep net indices... Match probability: 92.4%", "pause": 1.5},
            {"text": "Target confirmed.... User TRINITY - pass[AdminOne]", "pause": 1.5},
            {"text": "Location trace: TRI-SECTOR GRID 117/B", "pause": 1.5},
            {"text": "Contact node found  : (312)-555-0690.", "pause": 0}           
        ]
        # Guardamos el texto final para no tener que volver a generarlo.
        st.session_state.final_text = run_typing_simulation(TEXT_SEQUENCE)
        st.session_state.animation_finished = True

    # Muestra el texto final (que ya está guardado) y el formulario.
    

    st.markdown(f'<div class="terminal-container" style="white-space: pre;">{st.session_state.final_text}</div>', unsafe_allow_html=True)
    st.write("###")    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(key='access_form'):
            st.markdown('<div class="custom-label">ENTER TRACKING NUMBER TO ACCESS ENCRYPTED KEY LOGIN :</div>', unsafe_allow_html=True)
            code_input = st.text_input(label="-", placeholder="XXX-XXX-XXXX")
            submit_button = st.form_submit_button(label="CONNECT")

    if submit_button:
        if code_input == "312-555-0690":
            st.session_state.access_granted = True 
            st.rerun()
        else:
            st.error("TRACE FAILED. CONNECTION TERMINATED.")
            
else:
    st.switch_page("pages/passencript.py")
    time.sleep(3) 
    #st.success("Connection established.")    
    #time.sleep(3)    

