import streamlit as st
import random
import time
import pandas as pd


if 'login_code' not in st.session_state:
    st.session_state.login_code = None
if 'current_item' not in st.session_state:
    st.session_state.current_item = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'test_items' not in st.session_state:
    
    colors = ['Rojo', 'Verde', 'Azul', 'Amarillo']
    words = colors.copy()
    test_items = []
    for _ in range(20):
        word = random.choice(words)
        if random.choice([True, False]):
            color = word  
            correct_answer = 'Correcto'
        else:
            color = random.choice([c for c in colors if c != word])  
            correct_answer = 'Incorrecto'
        test_items.append({
            'word': word,
            'color': color,
            'correct_answer': correct_answer
        })
    st.session_state.test_items = test_items


color_mapping = {
    'Rojo': 'red',
    'Verde': 'green',
    'Azul': 'blue',
    'Amarillo': 'yellow'
}


if st.session_state.login_code is None:
    st.title("Inicio de Sesión - Test de Stroop")
    login_code = st.text_input("Ingresa tu código de acceso:")
    if st.button("Iniciar"):
        if login_code.strip():
            st.session_state.login_code = login_code.strip()
            st.rerun()
        else:
            st.error("Por favor, ingresa un código de acceso válido.")
else:
    
    if st.session_state.current_item < 20:
        item = st.session_state.test_items[st.session_state.current_item]
        st.write(f"Ítem {st.session_state.current_item + 1} de 20")
        css_color = color_mapping[item['color']]
        st.markdown(
            f"<h1 style='color: {css_color}; text-align: center;'>{item['word']}</h1>",
            unsafe_allow_html=True
        )
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        col1, col2 = st.columns(2)
        if col1.button("Correcto"):
            response_time = time.time() - st.session_state.start_time
            is_correct = item['correct_answer'] == 'Correcto'
            st.session_state.responses.append({
                'Ítem': st.session_state.current_item + 1,
                'Respuesta': 'Correcto',
                'EsCorrecto': is_correct,
                'TiempoRespuesta': response_time
            })
            st.session_state.current_item += 1
            st.session_state.start_time = None
            st.rerun()
        if col2.button("Incorrecto"):
            response_time = time.time() - st.session_state.start_time
            is_correct = item['correct_answer'] == 'Incorrecto'
            st.session_state.responses.append({
                'Ítem': st.session_state.current_item + 1,
                'Respuesta': 'Incorrecto',
                'EsCorrecto': is_correct,
                'TiempoRespuesta': response_time
            })
            st.session_state.current_item += 1
            st.session_state.start_time = None
            st.rerun()
    else:
        
        st.title("¡Muchas gracias por completar la prueba!")

        
        if len(st.session_state.responses) == 20:
            
            participant_data = {'Código': st.session_state.login_code}

            
            for response in st.session_state.responses:
                item_number = response['Ítem']
                time_response = response['TiempoRespuesta']
                participant_data[f'Item{item_number}'] = time_response

            
            for i in range(1, 21):
                if f'Item{i}' not in participant_data:
                    participant_data[f'Item{i}'] = None  

            
            total_correctas = sum(1 for resp in st.session_state.responses if resp['EsCorrecto'])
            total_incorrectas = 20 - total_correctas

            participant_data['Total Correctas'] = total_correctas
            participant_data['Total Incorrectas'] = total_incorrectas

            
            columns = ['Código'] + [f'Item{i}' for i in range(1, 21)] + ['Total Correctas', 'Total Incorrectas']

            
            resumen_df = pd.DataFrame([participant_data], columns=columns)

            
            try:
                existing_df = pd.read_excel('resultados_stroop.xlsx')

                if st.session_state.login_code in existing_df['Código'].astype(str).values:
                    st.error("Este código ya ha sido utilizado. Los resultados no se han guardado.")
                else:
                    
                    for col in columns:
                        if col not in existing_df.columns:
                            existing_df[col] = None
                    existing_df = existing_df[columns]

                    resultado_df = pd.concat([existing_df, resumen_df], ignore_index=True)
                    resultado_df.to_excel('resultados_stroop.xlsx', index=False)
                    st.success("Tus respuestas han sido guardadas correctamente.")
            except FileNotFoundError:
                
                resumen_df.to_excel('resultados_stroop.xlsx', index=False)
                st.success("Tus respuestas han sido guardadas correctamente.")
            except Exception as e:
                st.error(f"Ocurrió un error al guardar los resultados: {e}")
        else:
            st.error("La prueba no se completó correctamente. Los resultados no se han guardado.")
