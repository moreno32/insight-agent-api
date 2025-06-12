# Amplify AI 🚀

### Tu copiloto de IA para crear contenido de marca y campañas de marketing impactantes.

![Amplify AI Demo GIF](https://your-image-placeholder.com/amplify-ai-demo.gif)
*Nota: Reemplaza esta URL con un GIF de tu aplicación en acción una vez que tengas el MVP.*

---

## 📝 Descripción General

**Amplify AI** es un proyecto capstone end-to-end que demuestra el ciclo de vida completo de un producto de IA. La plataforma actúa como un asistente de marketing inteligente para PYMES, permitiéndoles generar contenido para redes sociales de forma rápida, sencilla y consistente con su identidad de marca.

El sistema se basa en un **agente multimodal avanzado construido con LangChain**. A través de una interfaz de Streamlit, el usuario rellena un **formulario estructurado** que incluye su idea, un manual de marca en formato Markdown y sus imágenes de estilo. Este input controlado garantiza un procesamiento de alta calidad, que el agente utiliza para orquestar un pipeline de RAG sofisticado y producir contenido único.

Este proyecto integra **IA Generativa**, **Machine Learning clásico** y prácticas modernas de **MLOps/DevOps**, demostrando una competencia integral en la ingeniería de IA.

## 🌟 Características Principales

*   **Agente Inteligente con LangChain:** El núcleo del sistema es un agente que orquesta de manera autónoma todo el flujo de trabajo.
*   **Input Estructurado y Controlado:** El usuario rellena un formulario, garantizando que el `brand_guide.md` siempre tenga un formato consistente para un chunking y procesamiento óptimos.
*   **Comprensión Multimodal del Contexto:** Procesa tanto texto como imágenes para un entendimiento profundo de la identidad de la marca.
*   **Pipeline de RAG Avanzado:** Utiliza técnicas de retrieval sofisticadas (`MultiQueryRetriever`, `MMR`) y una estrategia de LLM de dos niveles para maximizar la calidad y eficiencia.
*   **Interfaz Interactiva:** Una aplicación web amigable construida con **Streamlit**.
*   **Arquitectura Lista para Producción:** Utiliza **Ollama** para el servicio de LLMs, una solución contenerizable y escalable.

## 🛠️ Arquitectura y Stack Tecnológico

Amplify AI está construido sobre un stack moderno y open-source, con un fuerte enfoque en el control local de los modelos y la modularidad a través de LangChain.

![Architecture Diagram](https://your-image-placeholder.com/architecture-diagram.png)
*Nota: Crea un diagrama simple (con tools como diagrams.net o Excalidraw) que muestre el flujo completo.*

### **Componentes Principales:**

*   **Frontend:** **Streamlit**
*   **Backend:** **API con FastAPI**
*   **Orquestación del Agente:** **LangChain**
*   **Modelo de Clasificación (Intención):** **Scikit-learn**
*   **Modelo de Difusión (Imágenes):** **Stable Diffusion**

### **El Pipeline de RAG con LangChain**

#### 1. LLM (Large Language Model) - Estrategia de Dos Niveles
*   **Plataforma:** **Ollama** sirve los LLMs localmente. Es una solución robusta, rápida y desplegable, ideal para un entorno de producción.
*   **LLM Principal (Generación):** Se utiliza **`qwen3:8b`** para la generación final de texto. Su tamaño ofrece un excelente equilibrio entre creatividad, calidad de razonamiento y velocidad.
*   **LLM Secundario (Retrieval):** Para la tarea de generar variantes de consulta en el `MultiQueryRetriever`, se usa un modelo más pequeño y rápido como **`qwen3:4b`** para minimizar la latencia y optimizar el uso de recursos.

#### 2. Carga y División de Documentos (Loaders & Splitters)
*   **Tecnología:** `UnstructuredMarkdownLoader` → `MarkdownHeaderTextSplitter`.
*   **Estrategia:** El sistema se basa en un input de Markdown estructurado a través de un formulario en el frontend. Esto **garantiza un chunking de alta calidad**, ya que la estructura de encabezados (`#`, `##`) es siempre consistente, preservando la jerarquía del documento en los metadatos de cada chunk.

#### 3. Embeddings (Vectorización)
*   **Tecnología:** `langchain_community.embeddings.HuggingFaceEmbeddings`.
*   **Modelo:** Se utiliza **`paraphrase-multilingual-mpnet-base-v2`** para asegurar una comprensión semántica de alta calidad tanto en inglés como en español, lo cual es crucial para el caso de uso.

#### 4. Almacén de Vectores (Vector Store)
*   **Tecnología:** `langchain_community.vectorstores.Chroma`.
*   **Estrategia:** Se configura para **persistir en disco** (`persist_directory='db/chroma'`), optimizando el rendimiento al evitar la re-indexación en cada ejecución.

#### 5. Recuperación de Información (Retrievers)
*   **`MultiQueryRetriever`:** Utiliza el LLM secundario (`qwen3:4b`) para reescribir la consulta del usuario en múltiples variantes, mejorando significativamente el recall de la información.
*   **Búsqueda MMR (`Maximal Marginal Relevance`):** Se usa para seleccionar el conjunto final de documentos, asegurando un balance óptimo entre relevancia y diversidad para evitar pasar contexto redundante al LLM principal.

## 🚀 Cómo Empezar (Desarrollo Local)

### **Prerrequisitos**

*   Python 3.9+
*   Docker y Docker Compose
*   Git
*   **Ollama instalado y en ejecución:**
    1.  Descarga e instala [Ollama](https://ollama.com/).
    2.  Ejecuta los siguientes comandos en tu terminal para descargar los modelos necesarios:
        ```bash
        ollama pull qwen3:8b
        ollama pull qwen3:4b
        ```

### **Instalación y Ejecución**

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/moreno32/amplify-ai.git
    cd amplify-ai
    ```

2.  **Configura las variables de entorno:**
    Crea un archivo `.env` a partir de `env.example`. Las URLs de Ollama ya deberían estar configuradas por defecto para un entorno local.
    ```bash
    cp .env.example .env
    ```

3.  **Construye y levanta los contenedores:**
    ```bash
    docker-compose up --build
    ```

4.  **Accede a la aplicación:**
    *   **Frontend (Streamlit):** `http://localhost:8501`
    *   **Backend Docs (FastAPI):** `http://localhost:8000/docs`

## 🗺️ Roadmap del Proyecto

*   [✅] **Fase 1: MVP Funcional con Pipeline de RAG Avanzado**
*   [⬜️] **Fase 2: Contenerización y Despliegue en la Nube**
*   [⬜️] **Fase 3: Integración Multimodal Completa (Análisis de Imágenes)**
*   [⬜️] **Fase 4: Implementación de Nodos de Agente Avanzados (Guardrails, Tools)**
*   [⬜️] **Fase 5: Framework de Evaluación y Monitorización**

## 🧑‍💻 Sobre Mí

¡Hola! Soy **Daniel Moreno**, un AI Engineer / Data Scientist apasionado por construir productos de IA que resuelven problemas del mundo real. Este proyecto es una demostración de mis habilidades en todo el espectro del desarrollo de soluciones de Machine Learning, desde la concepción hasta la producción.

**Conéctate conmigo:**
*   **Email:** [danielmoreno3291@gmail.com](mailto:danielmoreno3291@gmail.com)
*   **Teléfono:** `+34 673 145 358`
*   **Ubicación:** Barcelona, España
*   **LinkedIn:** [https://www.linkedin.com/in/dmoreno-ai](https://www.linkedin.com/in/dmoreno-ai)
*   **GitHub:** [https://github.com/moreno32](https://github.com/moreno32)
*   **Medium (Blog):** [https://medium.com/@dmoreno-ai](https://medium.com/@dmoreno-ai)
*   **Portafolio:** [https://danielmoreno-ai.netlify.app/](https://danielmoreno-ai.netlify.app/)