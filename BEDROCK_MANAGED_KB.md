# Bedrock Managed Knowledge Base Support

## Changes
- Added managed KB cookbook recipe for Strands agents with Bedrock
- New recipe demonstrates KB retrieval tool with `managedSearchConfiguration`
- Strands agent tool definition updated to support managed KB type detection
- Added `AgenticRetrieveStream` cookbook example for streaming agentic retrieval
- Existing VECTOR cookbook recipes preserved alongside new managed examples

## Design
- MANAGED is the default in new cookbook recipes; VECTOR recipes kept for reference
- Strands agent KB tool auto-selects search config based on KB type
- AgenticRetrieveStream shown as recommended pattern for Strands agent architectures
- Backward compatible: existing VECTOR recipes and agent configurations unchanged

## API Shapes
- KB Creation: `type: MANAGED` + `managedKnowledgeBaseConfiguration.embeddingModelType: MANAGED`
- Retrieval: `managedSearchConfiguration` (not `vectorSearchConfiguration`)
- Agentic: `AgenticRetrieveStream` with `foundationModelType: MANAGED`, `rerankingModelType: MANAGED`

## Configuration
| Variable | Description | Default |
|---|---|---|
| KNOWLEDGE_BASE_TYPE | MANAGED or VECTOR | MANAGED |
| USE_AGENTIC_RETRIEVAL | Enable agentic retrieval | true |
| KNOWLEDGE_BASE_ID | KB identifier | (required) |

## SDK Requirements
- boto3 >= 1.43 for managed search and agentic retrieval
- strands-agents >= 0.1.0

## Reranking Options
For managed search, these reranking modes are available:
- `MANAGED` (default) — automatic reranking by Bedrock
- `NONE` — disable reranking
- `CUSTOM` — your own Bedrock reranking model (e.g., Cohere Rerank v3.5)

## References
- [Build a Managed Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html)
- [Retrieve API](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html)
- [Agentic Retrieval](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic.html)

## Required IAM Permissions
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:Retrieve",
    "bedrock:AgenticRetrieveStream"
  ],
  "Resource": "arn:aws:bedrock:<region>:<account-id>:knowledge-base/<kb-id>"
}
```
