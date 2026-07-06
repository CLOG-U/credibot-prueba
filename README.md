## Story Mapping - CrediBot

El siguiente mapa visualiza el recorrido del usuario (User Journey) de izquierda a derecha, y desglosa las historias de usuario de arriba hacia abajo según la prioridad de las entregas (Releases).

| Actividad Principal | 1. Iniciar Conversación | 2. Entregar Información | 3. Mantener Contexto | 4. Recibir Evaluación | 5. Asistencia y Cierre |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tareas del Usuario / Sistema** | Escribir, recibir saludo y elegir intención. | Ingresar datos (nombre, monto, plazo, ingresos). | Continuar flujo sin mezclar datos. | Esperar cálculo y resultado. | Pedir asesor y registrar solicitud. |
| **MVP (Release 1)** | **HU-01** Saludo inicial<br>**HU-02** Identificar intención | **HU-05** Captura nombre<br>**HU-06** Captura monto<br>**HU-07** Captura plazo<br>**HU-08** Captura ingreso | **HU-13** Estado por usuario | **HU-10** Evaluar reglas<br>**HU-11** Resultado claro | **HU-16** Derivación humana<br>**HU-19** Registro<br>**HU-22** Confirmación |
| **Release 2** | **HU-04** Respuestas inválidas | **HU-09** Producto de interés | **HU-14** Continuar solicitud<br>**HU-15** Cerrar inactivos | **HU-12** Modificar reglas | **HU-17** Resumen a asesor<br>**HU-20** Consultar panel<br>**HU-23** Plantillas |
