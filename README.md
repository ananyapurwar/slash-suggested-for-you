# Slash Suggested For You

This project is an AI-powered experience recommendation system that suggests personalized experiences to users based on their wishlist and viewing history. It uses Groq's LLM to analyze user preferences and find semantically similar experiences, providing intelligent recommendations through a FastAPI server.

## Features

- **AI-Powered Recommendations**: Uses Groq's LLM to analyze user preferences and find semantically similar experiences
- **Personalized Suggestions**: Provides experience recommendations based on user's wishlist and viewing history
- **Smart Tag Matching**: Uses LLM to find semantically similar tags and categories
- **FastAPI Server**: Exposes the recommendation functionality through a RESTful API
- **Supabase Integration**: Connects to Supabase database for user data and experience information
- **Session Management**: Supports multiple users with individual recommendation tracking

## How It Works

1. **User History Analysis**: Analyzes the user's wishlisted and viewed experiences
2. **Tag Extraction**: Extracts relevant tags and categories from user's experience history
3. **Semantic Matching**: Uses Groq LLM to find semantically similar tags and experiences
4. **Intelligent Ranking**: Ranks experiences by relevance to user preferences using AI
5. **Personalized Results**: Returns top-k most relevant experiences, excluding already seen ones

## Getting Started

### Prerequisites

- Python 3.10+
- Pip
- Virtualenv (recommended)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ananyapurwar/slash-suggested-for-you.git
   cd slash-suggested-for-you
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv slash
   source slash/bin/activate  # On Windows: slash\Scripts\activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root of the project and add the following variables:

   ```
   GROQ_API_KEY="your_groq_api_key"
   SUPABASE_URL="your_supabase_url"
   SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_role_key"
   ```

## Usage

### Running the API Server

To start the FastAPI server, run the following command:

```bash
uvicorn api_server:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### API Endpoints

- `GET /`: Root endpoint with API information
- `GET /suggested?user_id={user_id}&k={k}`: Get personalized experience recommendations
  - `user_id`: The user's UUID (required)
  - `k`: Number of recommendations (1-20, default 5)
- `GET /health`: Health check endpoint
- `GET /docs`: Interactive API documentation (Swagger UI)

### Example API Usage

```bash
# Get 5 recommendations for a user
curl "http://localhost:8000/suggested?user_id=123e4567-e89b-12d3-a456-426614174000&k=5"

# Get 10 recommendations for a user
curl "http://localhost:8000/suggested?user_id=123e4567-e89b-12d3-a456-426614174000&k=10"
```

### Running the CLI

You can also interact with the recommendation system through the command line:

```bash
python main.py
```

This will prompt you for a user_id and display recommended experiences.

## Project Structure

```
.
├── api_server.py         # FastAPI application with recommendation endpoints
├── main.py               # Core recommendation logic using Groq LLM
├── tools.py              # Helper functions for Groq API integration
├── perplexity_llm.py     # LangChain wrapper for Groq LLM
├── requirements.txt      # Project dependencies
├── render.yaml          # Render deployment configuration
└── slash/               # Virtual environment
```

## Dependencies

The main dependencies are listed in `requirements.txt` and include:

- `fastapi`: For the web server
- `uvicorn`: For running the FastAPI server
- `supabase`: For database interactions
- `python-dotenv`: For managing environment variables
- `groq`: For accessing the Groq API
- `requests`: For HTTP requests
- `langchain-core`: For LLM integration

## Deployment

The project includes a `render.yaml` file for easy deployment on Render. The service is configured to run on port 10000.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
