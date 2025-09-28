"""
Pergola Analysis Chat Service with RAG Integration
"""
from typing import List, Dict, Any
from app.services.scraped_content_manager import ScrapedContentManager
from app.core.multi_llm_orchestrator import MultiLLMOrchestrator

class PergolaChatService:
    """Chat service for pergola analysis with RAG capabilities"""
    
    def __init__(self):
        self.scraped_content_manager = ScrapedContentManager()
        self.llm_orchestrator = MultiLLMOrchestrator()
    
    async def chat(self, message: str, segment: str = "general", 
                   conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process chat message with context-aware responses"""
        
        # Get relevant context from scraped content
        relevant_docs = self.scraped_content_manager.similarity_search(message, k=5)
        
        # Filter by segment if specified
        if segment != "general":
            relevant_docs = [
                doc for doc in relevant_docs 
                if self._is_relevant_to_segment(doc, segment)
            ]
        
        # Build context for LLM
        context = self._build_context(relevant_docs, segment)
        
        # Generate response
        response = await self._generate_response(
            message, context, conversation_history, segment
        )
        
        return {
            'response': response,
            'sources': [
                {
                    'id': doc.id,
                    'source': doc.source,
                    'snippet': doc.content[:200] + "...",
                    'metadata': doc.metadata
                }
                for doc in relevant_docs[:3]
            ],
            'segment': segment,
            'timestamp': self._get_timestamp()
        }
    
    def _is_relevant_to_segment(self, doc, segment: str) -> bool:
        """Check if document is relevant to specific segment"""
        segment_keywords = {
            'consumer': ['consumer', 'demographics', 'behavior', 'loyalty', 'adoption', 'customer'],
            'market': ['market', 'trends', 'growth', 'size', 'expansion', 'competitive'], 
            'product': ['product', 'quality', 'differentiation', 'innovation', 'technology'],
            'brand': ['brand', 'positioning', 'reputation', 'perception', 'marketing'],
            'business_case': ['pricing', 'financial', 'roi', 'margin', 'costs', 'economics'],
            'experience': ['experience', 'service', 'customer', 'journey', 'satisfaction']
        }
        
        keywords = segment_keywords.get(segment, [])
        doc_content = doc.content.lower()
        doc_metadata = str(doc.metadata).lower()
        
        return any(keyword in doc_content or keyword in doc_metadata for keyword in keywords)
    
    def _build_context(self, docs, segment: str) -> str:
        """Build context string from relevant documents"""
        context_parts = [
            f"PERGOLA ANALYSIS CONTEXT FOR {segment.upper()} SEGMENT:",
            ""
        ]
        
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"{i}. {doc.content}")
            context_parts.append(f"   Source: {doc.source}")
            context_parts.append(f"   Metadata: {doc.metadata}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, message: str, context: str, 
                               history: List[Dict], segment: str) -> str:
        """Generate contextual response using LLM"""
        
        # Build conversation history
        history_text = ""
        if history:
            history_text = "\n".join([
                f"User: {msg.get('message', '')}\nAssistant: {msg.get('response', '')}"
                for msg in history[-3:]  # Last 3 exchanges
            ])
        
        # Create prompt
        prompt = f"""
You are an expert strategic analyst specializing in the LAMARK pergola business case. 
Answer the user's question using the provided context and conversation history.

SEGMENT FOCUS: {segment.upper()}

CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

USER QUESTION: {message}

Provide a comprehensive, accurate response based on the analysis data. Include:
1. Direct answer to the question
2. Supporting evidence from the context
3. Strategic implications for LAMARK
4. Specific recommendations if applicable

Focus specifically on the {segment} segment perspective where relevant.
"""
        
        response = await self.llm_orchestrator.analyze_with_gemini(prompt)
        return response
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
