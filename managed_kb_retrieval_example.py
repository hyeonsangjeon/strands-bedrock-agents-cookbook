"""
Managed Knowledge Base Retrieval with Strands Agents

This example demonstrates how to use Amazon Bedrock Managed Knowledge Bases
with Strands agents. Managed KBs eliminate the need to provision and manage
your own vector store (OpenSearch, Pinecone, etc.) - Amazon Bedrock handles
the vector storage infrastructure automatically.

Prerequisites:
    pip install strands-agents strands-agents-tools boto3

Usage:
    1. Replace MANAGED_KB_ID with your actual Managed Knowledge Base ID
    2. Run this script: python managed_kb_retrieval_example.py
"""

import boto3
from botocore.config import Config
import json
from strands import Agent, tool
from strands.models.bedrock import BedrockModel


# Configuration
MANAGED_KB_ID = ""  # Replace with your Managed Knowledge Base ID
REGION = "us-west-2"


# ==============================================================================
# Approach 1: Custom tool using boto3 with managedSearchConfiguration
# ==============================================================================

@tool
def search_managed_kb(query: str, num_results: int = 5) -> str:
    """Search an Amazon Bedrock Managed Knowledge Base for relevant documents.

    Uses the retrieve() API with managedSearchConfiguration, which is specific
    to Managed Knowledge Bases (where Bedrock handles the vector store).

    Args:
        query (str): The search query to find relevant documents.
        num_results (int): Number of results to return (default: 5).

    Returns:
        str: Formatted string containing the top retrieval results with scores.
    """
    client = boto3.client(
        'bedrock-agent-runtime',
        region_name=REGION,
        config=Config(user_agent_extra='strands-cookbook/bedrock-kb'),
    )

    # Toggle: USE_AGENTIC_RETRIEVAL=false to disable, GENERATE_RESPONSE=true for answer generation
    import os
    use_agentic = os.environ.get('USE_AGENTIC_RETRIEVAL', 'true').lower() == 'true'
    generate_response = os.environ.get('GENERATE_RESPONSE', 'false').lower() == 'true'

    # Primary: AgenticRetrieveStream (query decomposition + managed reranking)
    if use_agentic:
      try:
        response = client.agentic_retrieve_stream(
            messages=[{"content": {"text": query}, "role": "user"}],
            retrievers=[{
                "configuration": {
                    "knowledgeBase": {
                        "knowledgeBaseId": MANAGED_KB_ID,
                        "retrievalOverrides": {"maxNumberOfResults": num_results},
                    }
                }
            }],
            agenticRetrieveConfiguration={
                "foundationModelType": "MANAGED",
                "rerankingModelType": "MANAGED",
            },
            generateResponse=generate_response,
        )

        results = []
        for event in response.get("stream", []):
            if "result" in event:
                results = event["result"].get("results", [])

        if results:
            formatted_results = []
            for idx, result in enumerate(results, 1):
                score = result.get('score', 'N/A')
                content = result.get('content', {}).get('text', 'No content available')
                location = result.get('location', {})
                source = "Unknown"
                if 's3Location' in location:
                    source = location['s3Location'].get('uri', 'Unknown')

                formatted_results.append(
                    f"[Result {idx}] (Score: {score})\n"
                    f"Source: {source}\n"
                    f"Content: {content}\n"
                )
            return "\n".join(formatted_results)

      except Exception as e:
        print(f"AgenticRetrieveStream unavailable ({e}), falling back to Retrieve")

    # Fallback: standard Retrieve with managedSearchConfiguration
    try:
        response = client.retrieve(
            knowledgeBaseId=MANAGED_KB_ID,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'managedSearchConfiguration': {
                    'numberOfResults': num_results
                }
            }
        )

        results = response.get('retrievalResults', [])
        if not results:
            return "No results found for the given query."

        # Format results for the agent
        formatted_results = []
        for idx, result in enumerate(results, 1):
            score = result.get('score', 'N/A')
            content = result.get('content', {}).get('text', 'No content available')
            location = result.get('location', {})
            source = "Unknown"
            if 's3Location' in location:
                source = location['s3Location'].get('uri', 'Unknown')

            formatted_results.append(
                f"[Result {idx}] (Score: {score})\n"
                f"Source: {source}\n"
                f"Content: {content}\n"
            )

        return "\n---\n".join(formatted_results)

    except Exception as e:
        return f"Error searching managed knowledge base: {str(e)}"


@tool
def search_managed_kb_with_filter(query: str, metadata_filter: str, num_results: int = 5) -> str:
    """Search a Managed Knowledge Base with metadata filtering.

    Args:
        query (str): The search query.
        metadata_filter (str): JSON string of the metadata filter configuration.
            Example: '{"equals": {"key": "category", "value": "finance"}}'
        num_results (int): Number of results to return.

    Returns:
        str: Formatted retrieval results.
    """
    client = boto3.client(
        'bedrock-agent-runtime',
        region_name=REGION,
        config=Config(user_agent_extra='strands-cookbook/bedrock-kb'),
    )

    try:
        filter_config = json.loads(metadata_filter)
    except json.JSONDecodeError:
        return "Error: metadata_filter must be a valid JSON string."

    try:
        response = client.retrieve(
            knowledgeBaseId=MANAGED_KB_ID,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'managedSearchConfiguration': {
                    'numberOfResults': num_results,
                    'filter': filter_config
                }
            }
        )

        results = response.get('retrievalResults', [])
        if not results:
            return "No results found matching the query and filter criteria."

        formatted_results = []
        for idx, result in enumerate(results, 1):
            score = result.get('score', 'N/A')
            content = result.get('content', {}).get('text', 'No content')
            formatted_results.append(
                f"[Result {idx}] (Score: {score})\n{content}\n"
            )

        return "\n---\n".join(formatted_results)

    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# Approach 2: Using the built-in retrieve tool from strands_tools
# ==============================================================================

def create_agent_with_builtin_retrieve():
    """
    Create an agent using the built-in `retrieve` tool from strands_tools.

    The built-in retrieve tool works with any Bedrock Knowledge Base,
    including Managed KBs. You just need to provide the KB ID in your
    prompt or system instructions.

    Note: The built-in retrieve tool uses vectorSearchConfiguration by default.
    For managed KBs, you may want to use the custom tool above if you need
    managedSearchConfiguration specifically.
    """
    from strands_tools import retrieve

    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name=REGION,
        temperature=0.2,
    )

    system_prompt = f"""
    You are a research assistant with access to a knowledge base.
    When answering questions, use the retrieve tool with knowledge base ID: {MANAGED_KB_ID}
    Always cite your sources and indicate confidence based on retrieval scores.
    If you cannot find relevant information, say so clearly.
    """

    agent = Agent(
        model=bedrock_model,
        tools=[retrieve],
        system_prompt=system_prompt
    )

    return agent


# ==============================================================================
# Approach 3: Agent with custom managed KB tool
# ==============================================================================

def create_managed_kb_agent():
    """Create a Strands agent that uses the custom managed KB search tool."""

    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name=REGION,
        temperature=0.2,
    )

    system_prompt = """
    You are a helpful research assistant. Use the search_managed_kb tool to find
    relevant information from the knowledge base before answering questions.

    Guidelines:
    - Always search the knowledge base first before answering
    - Cite retrieval scores to indicate confidence
    - If results are not relevant (low scores), acknowledge limitations
    - Synthesize information from multiple results when possible
    - Use search_managed_kb_with_filter when the user specifies categories or metadata
    """

    agent = Agent(
        model=bedrock_model,
        tools=[search_managed_kb, search_managed_kb_with_filter],
        system_prompt=system_prompt
    )

    return agent


# ==============================================================================
# Main: Demonstrate usage
# ==============================================================================

if __name__ == "__main__":
    if not MANAGED_KB_ID:
        print("=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("\nPlease set MANAGED_KB_ID at the top of this file.")
        print("\nTo create a Managed Knowledge Base:")
        print("  1. Go to Amazon Bedrock Console > Knowledge Bases")
        print("  2. Click 'Create knowledge base'")
        print("  3. Under Vector store, select 'Quick create a new vector store'")
        print("     (this creates a Managed KB)")
        print("  4. Add an S3 data source with your documents")
        print("  5. Sync the data source")
        print("  6. Copy the Knowledge Base ID and paste it above")
        print("\nManaged KBs are the simplest option - no OpenSearch or")
        print("external vector database setup required!")
        exit(1)

    print("=" * 60)
    print("Managed Knowledge Base + Strands Agent Example")
    print("=" * 60)

    # Create the agent with custom managed KB tools
    agent = create_managed_kb_agent()

    # Example query
    query = "What are the main features and benefits discussed in the documents?"
    print(f"\nQuery: {query}\n")

    # Invoke the agent
    response = agent(query)

    print("\n" + "=" * 60)
    print("Agent Response:")
    print("=" * 60)
    print(response)

    # Show metrics if available
    if hasattr(response, 'metrics'):
        print(f"\nMetrics:")
        print(f"  Cycles: {response.metrics.cycle_count}")
        print(f"  Total Tokens: {response.metrics.accumulated_usage.get('totalTokens', 'N/A')}")
