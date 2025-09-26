import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Disconnect", layout="wide")


st.markdown(
    """
    <style>
        html, body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100%;
        }
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# HTML, CSS, JS embebido
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Disconnect System</title>
    <style>
        :root { --green: #66ff66; }
        * { box-sizing: border-box; }
        body {
            background-color: #000;
            background: radial-gradient(#177317, #000);
            box-shadow: inset 0 0 30rem #000000;
            color: var(--green);
            padding: 1rem;
            margin: 0;
            font-size: 1.1rem;
            text-shadow: 0 0 5px #66ff66aa;
            font-family: "VT323", monospace;
            height: 100vh;
            overflow: hidden;
        }
        #terminal-history { margin: 0; padding: 0; list-style: none; }
        #caret {
            position: relative;
            display: inline-block;
            background-color: var(--green);
            width: 8px;
            height: 1.5rem;
        }
        #caret.blinking { animation: blink 1s steps(5, start) infinite; }
        @keyframes blink { to { visibility: hidden; } }
        #alert {
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate3d(-50%, -50%, 0);
            font-size: 6em;
            pointer-events: none;
            animation: blink 1s steps(5, start) infinite;
        }
        #alert.hidden { display: none; }
    </style>
</head>
<body>
    <ul id="terminal-history"></ul>

    <div id="terminal-input">
        <span id="terminal-text"></span><span id="caret" class="blinking"></span>
    </div>

    <div id="alert" class="hidden">compromised system...!!!!</div>

    <script>
        console.clear();

        // Seguridad: ejecutar después de que cargue todo el DOM
        window.addEventListener('load', () => {
            // String helper (no se usa en este snippet, pero lo dejo por compatibilidad)
            String.prototype.replaceAt = function(index, replacement) {
                return this.substring(0, index) + replacement + this.substring(index + replacement.length);
            }

            const historyEl = document.querySelector('ul#terminal-history');
            const terminalText = document.querySelector('#terminal-text');
            const delay = 400; // base en ms (ajusta si quieres más lento/rápido)
            let currentText = "";

            const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
            const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            const nums = '0123456789';
            const characters = `${latin}${nums}`;

            function getTimestamp() {
                const now = new Date();
                const utcNow = new Date(now.toUTCString());
                const month = String(utcNow.getMonth() + 1).padStart(2, '0');
                const day = String(utcNow.getDate()).padStart(2, '0');
                const year = String(utcNow.getFullYear()).slice(2);
                const hours = String(utcNow.getHours()).padStart(2, '0');
                const minutes = String(utcNow.getMinutes()).padStart(2, '0');
                const seconds = String(utcNow.getSeconds()).padStart(2, '0');
                return `Timestamp: ${month}-${day}-${year} ${hours}:${minutes}:${seconds} UTC`;
            }

            const initialMsgs = [
                "Terminating uplink... [OK]",
                "Flushing volatile memory... [OK]",
                "Closing encrypted channels... [OK]",
                "Anonymizing exit node... [IN PROGRESS]",
                "→ Proxy cascade initiated: NODE-RED32 → GATE-ECHO9 → NULLVECTOR",
                "→ Masking trail using decoy packets [Level 4 Obfuscation]",
                "Session fingerprint scrubbed... [OK]",
                "Quantum noise injection deployed.",
                "Identity residuals: NULL",
                "No forensic trace detectable.",
                "System log sealed under hash: 7A-E1F9-C9B2",
                "Integrity check: PASSED",
                // timestamp dinámico se insertará justo antes del siguiente mensaje
                "Operator TRINITY has safely disengaged from Shadowline Grid.",
                "<b>*** Session Terminated. Connection Closed. ***</b>",
                "<b>Whatever you do, don't type 'restore connection'</b>"
            ];

            // Inicializa secuencia
            function init() {
                delayMsg('*** Secure Session Termination Protocol Engaged ***', delay / 2);
                setTimeout(displayMsgs, delay);
            }

            // Muestra mensajes con un delay acumulado controlado
            function displayMsgs() {
                let cumulativeDelay = 0;
                for (let i = 0; i < initialMsgs.length; i++) {
                    const msg = initialMsgs[i];

                    // Si llegamos al mensaje del operador, insertamos timestamp justo antes
                    if (msg.includes("Operator TRINITY")) {
                        // timestamp
                        delayMsg(getTimestamp(), cumulativeDelay);
                        cumulativeDelay += 500; // pequeña pausa extra
                        // ahora el mensaje del operador
                        delayMsg(msg, cumulativeDelay);
                        cumulativeDelay += delay; // avanza el acumulador
                    } else {
                        delayMsg(msg, cumulativeDelay);
                        cumulativeDelay += delay;
                    }
                }
            }

            function delayMsg(msg, ms) {
                setTimeout(() => {
                    // append y scroll automático si el contenido excede
                    historyEl.insertAdjacentHTML("beforeend", `<li>${msg}</li>`);
                    // opcional: mantener la vista al final (solo si hay scroll)
                    historyEl.parentElement.scrollTop = historyEl.parentElement.scrollHeight;
                }, ms);
            }

            function updateTerminalText() {
                terminalText.textContent = currentText;
            }

            function inputTerminalText() {
                if (currentText.toLowerCase() === "restore connection") {
                    glitchOut();
                } else if (currentText.length > 0) {
                    historyEl.insertAdjacentHTML("beforeend", `<li>${currentText}</li>`);
                }
            }

            function glitchOut() {
                document.querySelector('#caret').classList.remove('blinking');
                document.querySelectorAll('ul#terminal-history > li').forEach((li, i) => {
                    const text = li.textContent;
                    setTimeout(() => {
                        let iLetter = 0;
                        const interval = setInterval(() => {
                            const randomChar = Math.floor(Math.random() * characters.length);
                            let characterSet = Math.random() < 0.9 ? characters : katakana;
                            let newChar = Math.random() > 0.3 ? characterSet[randomChar] : ' ';
                            newChar = Math.random() < 0.9 ? newChar : newChar + characterSet[Math.floor(Math.random() * characterSet.length)];
                            let newStr = li.textContent.replace(text[iLetter], newChar);
                            li.textContent = newStr;
                            iLetter++
                            if (iLetter >= text.length) {
                                if (i === 0) {
                                    displayAlert();
                                }
                                clearInterval(interval);
                            }
                        }, 60);
                    }, 300 + i * 120);
                });
            }

            function displayAlert() {
                document.querySelector('#alert').classList.remove('hidden');
            }

            window.addEventListener('keyup', e => {
                const key = e.key;
                if (key.toLowerCase() === "enter") {
                    inputTerminalText();
                    currentText = '';
                } else if (key.toLowerCase() === "backspace") {
                    currentText = currentText.length ? currentText.slice(0, -1) : currentText;
                } else if (`${latin + " "}`.toLowerCase().includes(key.toLowerCase())) {
                    if (currentText.toLowerCase() === "restore connection") {
                        return false;
                    } else {
                        currentText += key;
                    }
                }
                updateTerminalText();
            });

            // arrancamos
            init();
        }); // load listener
    </script>
</body>
</html>
"""


# Render in Streamlit
components.html(html_code, height=700, scrolling=False)
