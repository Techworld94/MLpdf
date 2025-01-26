# Hivaani

Hivaani is an innovative web application that allows users to upload PDF documents and engage in interactive conversations about the content using LangChain and Google Generative AI. It simplifies document exploration, making it ideal for research, learning, or business use cases.

---

## Features

- **PDF Upload**: Users can easily upload one or multiple PDF documents.
- **Interactive Chat**: Engage in conversations about the uploaded content, powered by LangChain and Google Generative AI.
- **Contextual Understanding**: Provides accurate and context-aware answers to user queries, even if phrased differently.
- **Chat History**: Saves conversations to a database for retrieval on returning visits.
- **Dynamic Interface**: Responsive and user-friendly design with options for starting new chats and viewing previous sessions.

---

## Technologies Used

- **Backend**: Flask, LangChain, Google Generative AI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB for chat history and session management
- **PDF Processing**: PyMuPDF for extracting and chunking content
- **Vectorization**: FAISS index creation for fast querying
- **Integrations**:
  - LangChain for conversational AI
  - Google Generative AI embeddings for intelligent responses

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hivaani.git
   cd hivaani
