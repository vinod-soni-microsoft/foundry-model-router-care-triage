"""
RAG Pipeline Module
Implements Retrieval-Augmented Generation for clinical queries using Azure AI Search.
"""
import os
from typing import List, Dict, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for clinical knowledge."""
    
    def __init__(self):
        """Initialize Azure AI Search client."""
        search_endpoint = os.getenv("SEARCH_ENDPOINT", "")
        search_key = os.getenv("SEARCH_KEY", "")
        search_index = os.getenv("SEARCH_INDEX_NAME", "medical-kb")
        
        if search_endpoint and search_key:
            self.search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=search_index,
                credential=AzureKeyCredential(search_key)
            )
            self.enabled = True
        else:
            self.search_client = None
            self.enabled = False
    
    def retrieve_documents(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant documents from medical knowledge base.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
        
        Returns:
            List of retrieved documents with content and metadata
        """
        if not self.enabled or not self.search_client:
            return []
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top_k,
                select=["content", "title", "source", "category"]
            )
            
            documents = []
            for result in results:
                documents.append({
                    "content": result.get("content", ""),
                    "title": result.get("title", ""),
                    "source": result.get("source", ""),
                    "category": result.get("category", ""),
                    "score": result.get("@search.score", 0.0)
                })
            
            return documents
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def build_rag_prompt(
        self,
        user_query: str,
        documents: List[Dict]
    ) -> str:
        """
        Build augmented prompt with retrieved documents.
        
        Args:
            user_query: Original user query
            documents: Retrieved documents
        
        Returns:
            Augmented prompt with context and instructions
        """
        if not documents:
            return self._build_fallback_prompt(user_query)
        
        # Build context from documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Source {i}: {doc['title']}]\n{doc['content']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Build augmented prompt
        prompt = f"""You are a helpful healthcare assistant. Answer the following question based on the provided medical knowledge base sources.

IMPORTANT GUIDELINES:
1. Base your answer on the provided sources
2. Include citations in the format [Source N] where N is the source number
3. If the sources don't contain sufficient information, clearly state this
4. Always include a disclaimer that this is for educational purposes only
5. Never provide diagnostic conclusions or specific medical advice
6. Encourage users to consult healthcare professionals

MEDICAL KNOWLEDGE BASE SOURCES:
{context}

USER QUESTION:
{user_query}

Please provide a helpful, well-cited response with appropriate medical disclaimers."""
        
        return prompt
    
    def _build_fallback_prompt(self, user_query: str) -> str:
        """Build prompt when RAG is unavailable."""
        return f"""You are a helpful healthcare assistant. Answer the following question to the best of your ability.

IMPORTANT GUIDELINES:
1. Provide general, educational information only
2. Never provide diagnostic conclusions or specific medical advice
3. Always encourage users to consult healthcare professionals
4. Include appropriate medical disclaimers

USER QUESTION:
{user_query}

Please provide a helpful response with appropriate medical disclaimers."""
    
    def extract_citations(self, response: str, documents: List[Dict]) -> Dict:
        """
        Extract and format citations from response.
        
        Args:
            response: Generated response with [Source N] citations
            documents: Original retrieved documents
        
        Returns:
            Dict with formatted citations
        """
        import re
        
        # Find all [Source N] citations in response
        citations = re.findall(r'\[Source (\d+)\]', response)
        
        formatted_citations = {}
        for citation_num in set(citations):
            idx = int(citation_num) - 1
            if 0 <= idx < len(documents):
                doc = documents[idx]
                formatted_citations[citation_num] = {
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "category": doc.get("category", "")
                }
        
        return formatted_citations
