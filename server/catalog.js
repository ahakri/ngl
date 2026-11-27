// The watchlist: which projects Uptake tracks, how they are grouped into
// competitive categories, and where each one's adoption data comes from.
//
// p(slug, name, vendor, { pypi, npm, hn })
//   pypi / npm : package name in that registry (omit if none)
//   hn         : Hacker News search phrase (omit when the name is too generic
//                to search without false positives)
const p = (slug, name, vendor, src = {}) => ({ slug, name, vendor, ...src });

export const CATEGORIES = [
  {
    slug: 'model-sdks',
    name: 'Model provider SDKs',
    blurb: 'Official client libraries for hosted model APIs — the closest public proxy for which providers developers are building on.',
    projects: [
      p('openai', 'OpenAI SDK', 'OpenAI', { pypi: 'openai', npm: 'openai', hn: 'OpenAI API' }),
      p('anthropic', 'Anthropic SDK', 'Anthropic', { pypi: 'anthropic', npm: '@anthropic-ai/sdk', hn: 'Anthropic API' }),
      p('google-genai', 'Google Gen AI SDK', 'Google', { pypi: 'google-genai', npm: '@google/genai', hn: 'Gemini API' }),
      p('google-generativeai', 'Google Generative AI (legacy)', 'Google', { pypi: 'google-generativeai', npm: '@google/generative-ai' }),
      p('mistralai', 'Mistral SDK', 'Mistral AI', { pypi: 'mistralai', npm: '@mistralai/mistralai', hn: 'Mistral API' }),
      p('cohere', 'Cohere SDK', 'Cohere', { pypi: 'cohere', npm: 'cohere-ai', hn: 'Cohere' }),
      p('groq', 'Groq SDK', 'Groq', { pypi: 'groq', npm: 'groq-sdk', hn: 'Groq' }),
      p('together', 'Together SDK', 'Together AI', { pypi: 'together', npm: 'together-ai', hn: 'Together AI' }),
      p('replicate', 'Replicate SDK', 'Replicate', { pypi: 'replicate', npm: 'replicate' }),
      p('fireworks-ai', 'Fireworks SDK', 'Fireworks AI', { pypi: 'fireworks-ai', hn: 'Fireworks AI' }),
      p('cerebras', 'Cerebras SDK', 'Cerebras', { pypi: 'cerebras-cloud-sdk', npm: '@cerebras/cerebras_cloud_sdk', hn: 'Cerebras' }),
      p('xai-sdk', 'xAI SDK', 'xAI', { pypi: 'xai-sdk', hn: 'Grok API' }),
      p('huggingface-hub', 'Hugging Face Hub client', 'Hugging Face', { pypi: 'huggingface-hub', npm: '@huggingface/inference' }),
    ],
  },
  {
    slug: 'agent-frameworks',
    name: 'Agent & orchestration frameworks',
    blurb: 'Libraries for building LLM applications and agents. The most contested layer of the stack.',
    projects: [
      p('langchain', 'LangChain', 'LangChain', { pypi: 'langchain', npm: 'langchain', hn: 'LangChain' }),
      p('langgraph', 'LangGraph', 'LangChain', { pypi: 'langgraph', npm: '@langchain/langgraph', hn: 'LangGraph' }),
      p('llamaindex', 'LlamaIndex', 'LlamaIndex', { pypi: 'llama-index', npm: 'llamaindex', hn: 'LlamaIndex' }),
      p('vercel-ai-sdk', 'Vercel AI SDK', 'Vercel', { npm: 'ai', hn: 'Vercel AI SDK' }),
      p('openai-agents', 'OpenAI Agents SDK', 'OpenAI', { pypi: 'openai-agents', npm: '@openai/agents', hn: 'OpenAI Agents SDK' }),
      p('claude-agent-sdk', 'Claude Agent SDK', 'Anthropic', { pypi: 'claude-agent-sdk', npm: '@anthropic-ai/claude-agent-sdk', hn: 'Claude Agent SDK' }),
      p('google-adk', 'Google ADK', 'Google', { pypi: 'google-adk', hn: 'Agent Development Kit' }),
      p('crewai', 'CrewAI', 'CrewAI', { pypi: 'crewai', hn: 'CrewAI' }),
      p('autogen', 'AutoGen', 'Microsoft', { pypi: 'autogen-agentchat', hn: 'AutoGen' }),
      p('semantic-kernel', 'Semantic Kernel', 'Microsoft', { pypi: 'semantic-kernel', hn: 'Semantic Kernel' }),
      p('pydantic-ai', 'Pydantic AI', 'Pydantic', { pypi: 'pydantic-ai', hn: 'Pydantic AI' }),
      p('smolagents', 'smolagents', 'Hugging Face', { pypi: 'smolagents', hn: 'smolagents' }),
      p('dspy', 'DSPy', 'Stanford NLP', { pypi: 'dspy', hn: 'DSPy' }),
      p('haystack', 'Haystack', 'deepset', { pypi: 'haystack-ai', hn: 'Haystack deepset' }),
      p('agno', 'Agno', 'Agno', { pypi: 'agno', hn: 'Agno' }),
      p('strands-agents', 'Strands Agents', 'AWS', { pypi: 'strands-agents', hn: 'Strands Agents' }),
      p('mastra', 'Mastra', 'Mastra', { npm: '@mastra/core', hn: 'Mastra' }),
    ],
  },
  {
    slug: 'mcp',
    name: 'Model Context Protocol',
    blurb: 'SDKs for building MCP servers and clients — a read on tool-use and agent integration activity.',
    projects: [
      p('mcp-sdk', 'MCP SDK (official)', 'Model Context Protocol', { pypi: 'mcp', npm: '@modelcontextprotocol/sdk', hn: 'Model Context Protocol' }),
      p('fastmcp', 'FastMCP', 'FastMCP', { pypi: 'fastmcp', npm: 'fastmcp', hn: 'FastMCP' }),
    ],
  },
  {
    slug: 'vector-databases',
    name: 'Vector databases',
    blurb: 'Client libraries for vector stores used in retrieval. Client pulls track active integration work.',
    projects: [
      p('pinecone', 'Pinecone', 'Pinecone', { pypi: 'pinecone', npm: '@pinecone-database/pinecone', hn: 'Pinecone' }),
      p('chroma', 'Chroma', 'Chroma', { pypi: 'chromadb', npm: 'chromadb', hn: 'ChromaDB' }),
      p('qdrant', 'Qdrant', 'Qdrant', { pypi: 'qdrant-client', npm: '@qdrant/js-client-rest', hn: 'Qdrant' }),
      p('weaviate', 'Weaviate', 'Weaviate', { pypi: 'weaviate-client', npm: 'weaviate-client', hn: 'Weaviate' }),
      p('milvus', 'Milvus', 'Zilliz', { pypi: 'pymilvus', npm: '@zilliz/milvus2-sdk-node', hn: 'Milvus' }),
      p('lancedb', 'LanceDB', 'LanceDB', { pypi: 'lancedb', npm: '@lancedb/lancedb', hn: 'LanceDB' }),
      p('pgvector', 'pgvector', 'pgvector', { pypi: 'pgvector', npm: 'pgvector', hn: 'pgvector' }),
      p('faiss', 'FAISS', 'Meta', { pypi: 'faiss-cpu', hn: 'FAISS' }),
      p('turbopuffer', 'turbopuffer', 'turbopuffer', { pypi: 'turbopuffer', npm: '@turbopuffer/turbopuffer', hn: 'turbopuffer' }),
    ],
  },
  {
    slug: 'inference',
    name: 'Inference & serving',
    blurb: 'Runtimes and servers for running models yourself — the open-weights side of the build-vs-buy decision.',
    projects: [
      p('transformers', 'Transformers', 'Hugging Face', { pypi: 'transformers', npm: '@huggingface/transformers' }),
      p('vllm', 'vLLM', 'vLLM', { pypi: 'vllm', hn: 'vLLM' }),
      p('ollama', 'Ollama client', 'Ollama', { pypi: 'ollama', npm: 'ollama', hn: 'Ollama' }),
      p('llama-cpp', 'llama.cpp bindings', 'llama.cpp', { pypi: 'llama-cpp-python', npm: 'node-llama-cpp', hn: 'llama.cpp' }),
      p('mlx-lm', 'MLX LM', 'Apple', { pypi: 'mlx-lm', hn: 'MLX' }),
      p('onnxruntime', 'ONNX Runtime', 'Microsoft', { pypi: 'onnxruntime', npm: 'onnxruntime-web', hn: 'ONNX Runtime' }),
      p('sentence-transformers', 'Sentence Transformers', 'Hugging Face', { pypi: 'sentence-transformers' }),
      p('ctranslate2', 'CTranslate2', 'OpenNMT', { pypi: 'ctranslate2' }),
      p('web-llm', 'WebLLM', 'MLC', { npm: '@mlc-ai/web-llm', hn: 'WebLLM' }),
      p('bentoml', 'BentoML', 'BentoML', { pypi: 'bentoml', hn: 'BentoML' }),
    ],
  },
  {
    slug: 'gateways',
    name: 'LLM gateways & routers',
    blurb: 'Abstraction layers that route between providers — a signal of multi-model strategies.',
    projects: [
      p('litellm', 'LiteLLM', 'BerriAI', { pypi: 'litellm', hn: 'LiteLLM' }),
      p('portkey', 'Portkey', 'Portkey', { pypi: 'portkey-ai', npm: 'portkey-ai', hn: 'Portkey' }),
      p('openrouter', 'OpenRouter SDK', 'OpenRouter', { pypi: 'openrouter', npm: '@openrouter/ai-sdk-provider', hn: 'OpenRouter' }),
    ],
  },
  {
    slug: 'training',
    name: 'Training & fine-tuning',
    blurb: 'Frameworks and fine-tuning toolkits. Fine-tuning libraries are a leading indicator of open-model customisation.',
    projects: [
      p('pytorch', 'PyTorch', 'PyTorch Foundation', { pypi: 'torch', hn: 'PyTorch' }),
      p('tensorflow', 'TensorFlow', 'Google', { pypi: 'tensorflow', npm: '@tensorflow/tfjs', hn: 'TensorFlow' }),
      p('jax', 'JAX', 'Google', { pypi: 'jax', hn: 'JAX' }),
      p('keras', 'Keras', 'Google', { pypi: 'keras', hn: 'Keras' }),
      p('lightning', 'Lightning', 'Lightning AI', { pypi: 'lightning', hn: 'PyTorch Lightning' }),
      p('peft', 'PEFT', 'Hugging Face', { pypi: 'peft' }),
      p('accelerate', 'Accelerate', 'Hugging Face', { pypi: 'accelerate' }),
      p('trl', 'TRL', 'Hugging Face', { pypi: 'trl' }),
      p('bitsandbytes', 'bitsandbytes', 'bitsandbytes', { pypi: 'bitsandbytes' }),
      p('unsloth', 'Unsloth', 'Unsloth', { pypi: 'unsloth', hn: 'Unsloth' }),
      p('diffusers', 'Diffusers', 'Hugging Face', { pypi: 'diffusers' }),
      p('hf-datasets', 'Datasets', 'Hugging Face', { pypi: 'datasets' }),
    ],
  },
  {
    slug: 'evals-observability',
    name: 'Evals & observability',
    blurb: 'Tracing, evaluation and experiment tracking — spend that follows applications into production.',
    projects: [
      p('langsmith', 'LangSmith', 'LangChain', { pypi: 'langsmith', npm: 'langsmith', hn: 'LangSmith' }),
      p('langfuse', 'Langfuse', 'Langfuse', { pypi: 'langfuse', npm: 'langfuse', hn: 'Langfuse' }),
      p('mlflow', 'MLflow', 'Databricks', { pypi: 'mlflow', hn: 'MLflow' }),
      p('wandb', 'Weights & Biases', 'CoreWeave', { pypi: 'wandb', hn: 'Weights & Biases' }),
      p('weave', 'W&B Weave', 'CoreWeave', { pypi: 'weave' }),
      p('arize-phoenix', 'Arize Phoenix', 'Arize', { pypi: 'arize-phoenix', hn: 'Arize Phoenix' }),
      p('opik', 'Opik', 'Comet', { pypi: 'opik', npm: 'opik', hn: 'Opik' }),
      p('braintrust', 'Braintrust', 'Braintrust', { pypi: 'braintrust', npm: 'braintrust', hn: 'Braintrust' }),
      p('ragas', 'Ragas', 'Ragas', { pypi: 'ragas', hn: 'Ragas' }),
      p('deepeval', 'DeepEval', 'Confident AI', { pypi: 'deepeval', hn: 'DeepEval' }),
      p('promptfoo', 'promptfoo', 'promptfoo', { npm: 'promptfoo', hn: 'promptfoo' }),
      p('inspect-ai', 'Inspect', 'UK AISI', { pypi: 'inspect-ai', hn: 'Inspect AI' }),
    ],
  },
  {
    slug: 'rag-data',
    name: 'RAG, search & data prep',
    blurb: 'Document parsing, web search and structured-output tooling that feeds model context.',
    projects: [
      p('unstructured', 'Unstructured', 'Unstructured', { pypi: 'unstructured', hn: 'Unstructured.io' }),
      p('docling', 'Docling', 'IBM', { pypi: 'docling', hn: 'Docling' }),
      p('markitdown', 'MarkItDown', 'Microsoft', { pypi: 'markitdown', hn: 'MarkItDown' }),
      p('firecrawl', 'Firecrawl', 'Firecrawl', { pypi: 'firecrawl-py', npm: '@mendable/firecrawl-js', hn: 'Firecrawl' }),
      p('tavily', 'Tavily', 'Tavily', { pypi: 'tavily-python', npm: '@tavily/core', hn: 'Tavily' }),
      p('exa', 'Exa', 'Exa', { pypi: 'exa-py', npm: 'exa-js', hn: 'Exa search' }),
      p('instructor', 'Instructor', 'Instructor', { pypi: 'instructor', npm: '@instructor-ai/instructor' }),
      p('outlines', 'Outlines', '.txt', { pypi: 'outlines', hn: 'Outlines dottxt' }),
      p('tiktoken', 'tiktoken', 'OpenAI', { pypi: 'tiktoken', npm: 'tiktoken' }),
    ],
  },
];

export const ECOSYSTEMS = ['pypi', 'npm'];

export const PROJECTS = CATEGORIES.flatMap((c) => c.projects.map((x) => ({ ...x, category: c.slug })));
export const projectBySlug = new Map(PROJECTS.map((x) => [x.slug, x]));
export const categoryBySlug = new Map(CATEGORIES.map((c) => [c.slug, c]));

if (projectBySlug.size !== PROJECTS.length) throw new Error('catalog: duplicate project slug');
