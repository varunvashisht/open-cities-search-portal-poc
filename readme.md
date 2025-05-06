# Open Cities Search Portal

The **Open Cities Search Portal** is a proof-of-concept application that integrates advanced semantic search and conversational AI capabilities to help users explore city-related information. It combines AWS Kendra, Bedrock with Claude 3.7 Sonnet, Firecrawl for web scraping, and custom PDF/Parquet generation workflows.

## 🔍 Key Features

- **Semantic Search with Amazon Kendra**: Retrieve relevant data using natural language queries.
- **Conversational AI with Claude 3.7 Sonnet via Bedrock**: Engage with data using a chatbot interface powered by Anthropic's Claude.
- **Web Scraping & Crawling with Firecrawl**:
  - Scrape Main Content
  - Scrape Full Page
  - Crawl and Scrape
- **Streamlit UI**: User-friendly interface for search and interaction.
- **PDF & Parquet Generation**: Export search or scrape results as PDFs or Parquet files.
- **Dremio Integration**: Parquet files are shared with a Dremio instance for enhanced querying and semantic analysis.

## 🛠 Tech Stack

- **Backend**: Python, Flask (`app.py`)
- **Frontend**: Streamlit for Scraping and Kendra Search (`search.py`) ; Streamlit for chatbot (`bedrock_ui.py`)
- **AI & Search**:
  - Amazon Kendra for semantic document search
  - Amazon Bedrock with Claude 3.7 Sonnet for conversational interface
- **Scraping**: Firecrawl API
- **Data Formats**: PDF, Parquet
- **Cloud**: AWS (Kendra, Bedrock, S3, EC2)

## 📦 Installation

### Prerequisites

- Python 3.9+
- AWS credentials with access to Bedrock and Kendra
- API key for Firecrawl
- Dremio instance (for Parquet querying)

### Steps

1. **Clone the repo**

```bash
git clone https://github.com/varunvashisht/open-cities-search-portal-poc.git
cd open-cities-search-portal-poc
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. Set up environment variables
   Create a .env file with your configuration (Kendra index, Bedrock model ID, Firecrawl API key, etc.).

4. **Running the Application**
   - Start the backend
     ```bash
     python3 app.py
     ```
   - Start the Scraping and Kendra Search File
     ```bash
     streamlit run search.py
     ```
   - Start the chatbot
     ```bash
     streamlit run bedrock_ui.py
     ```
  Access the respective UI's through the links provided

  ## 📂 Project Structure
```plaintext
  ├── app.py               # Entry point for all services (Flask)
  ├── search.py            # Kendra and Scraping UI
  ├── awsHelper.py         # AWS S3 upload utility function
  ├── firecrawlHelper.py   # Firecrawl scraping utility functions
  ├── pdfHelper.py         # PDF and Parquet generation
  ├── bedrock_ui.py        # Claude-based chatbot UI
  ├── requirements.txt     # Dependencies
  ├── .env.example         # Environment variable template
  └── readme.md            # Documentation
```

 ## 📊 Outputs
 - **PDF:** Cleanly formatted documents from scraped data in S3. (`websites_pdfs`)
 - **Parquet:** Structured data shared with a Dremio instance for advanced querying and semantic access S3. (`websites_data`)

