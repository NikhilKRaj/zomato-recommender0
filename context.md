# Project Context: AI-Powered Restaurant Recommendation System

## Problem Statement

Build an AI-powered restaurant recommendation service inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining structured data with a Large Language Model (LLM).

## Objective

Design and implement an application that:

- Takes user preferences (such as location, budget, cuisine, and ratings)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields such as restaurant name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect user preferences:

- **Location** (e.g., Delhi, Bangalore)
- **Budget** (low, medium, high)
- **Cuisine** (e.g., Italian, Chinese)
- **Minimum rating**
- **Any additional preferences** (e.g., family-friendly, quick service)

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output Display

Present top recommendations in a user-friendly format:

| Field | Description |
|-------|-------------|
| Restaurant Name | Name of the recommended restaurant |
| Cuisine | Type of cuisine offered |
| Rating | Restaurant rating |
| Estimated Cost | Expected cost for dining |
| AI-generated explanation | Why this restaurant was recommended |

## Data Source

- **Dataset**: Zomato Restaurant Recommendation
- **URL**: https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- **Key fields**: restaurant name, location, cuisine, cost, rating

## Key Technical Components

1. **Data pipeline** — Hugging Face dataset loading and preprocessing
2. **Preference filtering** — Match restaurants to user criteria before LLM processing
3. **LLM integration** — Prompt design for ranking, explanation, and summarization
4. **User interface** — Display recommendations with structured output fields
