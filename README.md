# Strands Agent

![Strands](strands.png)

An AI agent development project leveraging Amazon Bedrock and the Strands Agents SDK.

## Project Overview

This project demonstrates how to build various AI agents using the Strands Agents SDK. You can create simple yet powerful agents centered around three core components: a model, tools, and a prompt.

## Key Features

### Included Utilities

- **advanced_rag_utils.py**: Advanced RAG (Retrieval-Augmented Generation) capabilities using AWS Bedrock
  - Knowledge Base retrieval and generation
  - Metadata filtering
  - Bedrock client configuration

- **llm_cost_utils.py**: LLM usage monitoring and cost calculation
  - Bedrock token count tracking
  - CloudWatch metrics integration
  - Cost analysis

### Use Cases

The Strands.ipynb notebook includes 10 practical use cases:

1. **Web Scraping**: Extract article titles and links from Hacker News
2. **Stock Price Analysis**: Moving averages, volatility, return rate analysis with visualizations
3. **Insurance Claims Inspection**: Weather data validation and DynamoDB storage
4. **Knowledge Base + Internet Search**: 10K document retrieval and news aggregation
5. **Custom Python Tools**: LLM usage calculator
6. **DataFrame Manipulation**: Data processing with pandas
7. **PySpark Data Processing**: Large-scale data transformation and storage
8. **Machine Learning Pipeline**: Customer churn prediction model
9. **Multi-Agent System**: Financial advisory agent orchestration
10. **MCP Integration**: AWS documentation querying and architecture diagram generation

## Installation

### Prerequisites

```bash
pip install strands-agents strands-agents-tools strands-agents-builder nest_asyncio uv
```

### Optional Libraries

```bash
# For financial analysis
pip install yfinance matplotlib

# For web scraping
pip install beautifulsoup4 pandas requests

# For machine learning
pip install scikit-learn joblib seaborn
```

## Usage

### Basic Agent Creation

```python
from strands import Agent

agent = Agent()
agent("Explain Amazon Bedrock Agents?")
```

### Extended Thinking (Reasoning Model)

**Extended Thinking** (also called "interleaved thinking" in Claude 4) enables Claude to think more deeply when solving complex problems, providing transparent reasoning processes alongside final answers.


#### For Claude 4 Sonnet (with Interleaved Thinking):

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14"],
        "thinking": {"type": "enabled", "budget_tokens": 8000}
    }
)

agent = Agent(model=model)
response = agent("What are the benefits of reasoning models?")
```

The reasoning process is accessible via `reasoningContent` in the response blocks.

### Agent with Tools

```python
from strands_tools import python_repl, file_write
from strands import Agent
import os

os.environ["BYPASS_TOOL_CONSENT"] = "true"

agent = Agent(tools=[python_repl, file_write])
response = agent("Scrape data from a web page and save it as CSV")
```

### Defining Custom Tools

```python
from strands import tool, Agent

@tool
def my_custom_tool(query: str) -> str:
    """Custom tool description"""
    # Tool logic
    return result

agent = Agent(tools=[my_custom_tool])
```

## Configuration

Create a `variables.json` file in the project root to configure AWS settings:

```json
{
  "kbSemanticChunk": "your-knowledge-base-id",
  "region": "us-west-2",
  "account_number": "your-aws-account-number"
}
```

## Supported Models

- Amazon Bedrock models (Nova, Claude, Titan, etc.)
- Anthropic Claude model family
- Ollama (for local development)
- Other providers via LiteLLM

## File Structure

```
.
├── Strands.ipynb                      # Main demo notebook
├── research_agent_kb_internet.ipynb   # Research agent example
├── advanced_rag_utils.py              # RAG utility functions
├── llm_cost_utils.py                  # Cost calculation tools
├── kb_id.txt                          # Knowledge Base ID
├── strands.png                        # Project image
├── README.md                          # This file (English)
└── README-kr.md                       # Korean version
```

## Key Highlights

- **Model-Driven Approach**: Easy integration with various LLM models
- **Rich Tool Ecosystem**: 20+ pre-built tools and MCP server support
- **Simple API**: Build powerful agents with just a few lines of code
- **Scalable**: From local development to production deployment
- **AWS Integration**: Native integration with Bedrock, DynamoDB, CloudWatch, and more

## Managed Knowledge Bases

The Knowledge Base examples in this cookbook support both **Managed Knowledge Bases** (recommended) and traditional vector search KBs.

### managed_kb_retrieval_example.py

A dedicated example demonstrating managed knowledge base retrieval with the Strands SDK:

```python
import os
os.environ["KNOWLEDGE_BASE_ID"] = "ABCDEFGHIJ"
os.environ["KNOWLEDGE_BASE_TYPE"] = "MANAGED"

from strands import Agent
from strands_tools import retrieve

agent = Agent(tools=[retrieve])
response = agent("Summarize the key findings from our research documents")
```

Managed KBs:
- Eliminate the need for an external vector store (Bedrock handles embedding, storage, and retrieval)
- Support agentic retrieval with intelligent query decomposition and managed reranking
- Use `managedSearchConfiguration` instead of `vectorSearchConfiguration`

Set environment variables to configure behavior:
```bash
export KNOWLEDGE_BASE_ID="your-managed-kb-id"
export KNOWLEDGE_BASE_TYPE="MANAGED"
export USE_AGENTIC_RETRIEVAL="true"   # Enable agentic retrieval (default)
export GENERATE_RESPONSE="false"      # Disable response generation (default)
```

> **SDK requirements:** `boto3 >= 1.43` for managed search and agentic retrieval.

## Resources

- [Strands Agents Official Documentation](https://docs.strands.ai)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents Announcement Blog](https://aws.amazon.com/blogs/)
- [Advanced RAG using Bedrock and SageMaker - AWS Samples](https://github.com/aws-samples/sample-advanced-rag-using-bedrock-and-sagemaker/tree/main)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome!
