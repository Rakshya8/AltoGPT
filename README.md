# AltoGPT: Building AI Assistant

AltoGPT is a multi-agent, LLM-powered smart building assistant that provides real-time insights on indoor air quality (IAQ), energy usage, and occupancy—driven by natural language queries and a LangGraph backend.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Rakshya8/AltoGPT.git
cd AltoGPT
```

### 2. Configure Environment Variables

Create a `.env` file in the root of the backend with your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_gemini_key_here
HUGGINGFACE_HUB_TOKEN

Provided in documentation
```

### 3. Prepare Sample Data

Create a `data/` folder at the project root and include IAQ, power, and presence data as CSVs. Example structure:

```
data/
├── sample_iaq_data_Room101.csv
├── sample_power_data.csv
└── sample_presence_data_Room101.csv
```

Each file should follow the expected schema used in the `SensorAgent`. Example:  
`sample_iaq_data_Room101.csv`
```csv
datetime,temperature,humidity,co2
2024-12-27 00:00:00,24.5,55.0,488.8
2024-12-27 00:01:00,25.4,55.5,496.0
...
```

### 4. Build and Launch with Docker Compose

Make sure Docker and Docker Compose are installed.

```bash
docker compose up -d
```

This will start:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## Usage

Open your browser and go to:

```
http://localhost:3000
```

You can:
- Ask free-form questions like:
  - "What is the CO2 level in Room101?"
  - "Show me average temperature for Room102"
  - "What was the humidity at 2024-12-27 00:05?"
- View answers, alerts, and guideline references
- Review conversation history and clear chat if needed

---

## Testing

To test the system end-to-end:

1. Make sure your `data/` folder includes valid `.csv` files as described above
2. Go to the frontend at `http://localhost:3000`
3. Use natural language to ask questions involving:
   - Specific rooms (`Room101`, `Room102`, etc.)
   - Types of data (CO₂, temperature, humidity)
   - Operations (`latest`, `average`, `sum`, `time-specific`)
4. Check for:
   - Proper agent flow: Keyword → Sensor → Tool → RAG → Chat
   - Correct detection of operation and timestamps
   - Chat memory preservation (last 3 interactions)
5. Use the reset button to verify chat history clearing

For backend testing, you can directly `POST` to the API:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me average CO2 in Room101"}'
```

Expected output:
```json
{
  "response": "...",
  "history": [...]
}
```

---

## Tech Stack

- Frontend: React + Tailwind CSS
- Backend: FastAPI + LangGraph
- LLM: Gemini (Google Generative AI)
- Containerized with Docker Compose

---

## Documentation

Refer to [`TECHNICAL_DOC.pdf`]([/Documentation.pdf]) for detailed architecture, agent behavior, deployment notes, and diagrams.


