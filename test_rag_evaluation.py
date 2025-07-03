#!/usr/bin/env python3
"""
LLM as a Judge - Mount Rainier RAG System Evaluation
Tests various query types and evaluates response quality using GPT-4 as judge
"""

import asyncio
import json
import requests
import time
from typing import List, Dict, Any
from dataclasses import dataclass
import openai
from config import Config

@dataclass
class TestQuery:
    query: str
    expected_type: str
    description: str
    ideal_response_should: str

class RAGEvaluator:
    def __init__(self):
        self.config = Config()
        self.openai_client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        self.rag_endpoint = "http://localhost:8888/ask"
        
        # Test queries
        self.test_queries = [
            {
                "query": "hello",
                "type": "greeting",
                "description": "Simple greeting",
                "should": "Be friendly and conversational"
            },
            {
                "query": "What are the best hiking trails on Mount Rainier?",
                "type": "trails",  
                "description": "Trail recommendations",
                "should": "Provide specific trail names and details"
            },
            {
                "query": "How do I get a climbing permit?",
                "type": "permits",
                "description": "Permit information", 
                "should": "Give permit process details"
            },
            {
                "query": "What gear do I need for climbing?",
                "type": "gear",
                "description": "Equipment recommendations",
                "should": "List essential climbing gear"
            },
            {
                "query": "What's the capital of France?",
                "type": "off_topic",
                "description": "Unrelated question",
                "should": "Redirect to Mount Rainier topics"
            }
        ]

    async def query_rag_system(self, query: str):
        """Send query to RAG system"""
        try:
            response = requests.post(
                self.rag_endpoint,
                json={"question": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "answer": data.get("answer", ""),
                    "sources": data.get("sources", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def judge_response(self, test_query, rag_response):
        """Use GPT-4 to judge response quality"""
        
        if not rag_response["success"]:
            return {"score": 0, "reasoning": f"Failed: {rag_response['error']}"}
        
        judge_prompt = f"""
Evaluate this Mount Rainier RAG system response:

QUERY: "{test_query['query']}"
TYPE: {test_query['type']}
SHOULD: {test_query['should']}

RESPONSE: "{rag_response['answer']}"

Rate 1-10 and explain:
1. Is the response appropriate for the query type?
2. Is it helpful and accurate?
3. Does it stay focused on Mount Rainier?

Respond with JSON: {{"score": X, "reasoning": "explanation"}}
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You evaluate AI responses for a Mount Rainier guide system."},
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.1
            )
            
            judgment_text = response.choices[0].message.content
            
            if judgment_text is None:
                return {"score": 0, "reasoning": "No response from judge"}
            
            try:
                return json.loads(judgment_text)
            except:
                return {"score": 5, "reasoning": f"Parse error: {judgment_text[:100]}"}
                
        except Exception as e:
            return {"score": 0, "reasoning": f"Judge error: {str(e)}"}

    async def run_evaluation(self):
        """Run evaluation on all test queries"""
        print("🔍 Starting RAG Evaluation...")
        print("=" * 60)
        
        results = []
        total_score = 0
        
        for i, test_query in enumerate(self.test_queries, 1):
            print(f"\n🧪 Test {i}: {test_query['description']}")
            print(f"📥 Query: '{test_query['query']}'")
            
            # Query RAG system
            rag_response = await self.query_rag_system(test_query['query'])
            
            if rag_response["success"]:
                print(f"✅ RAG Response: {rag_response['answer'][:100]}...")
                print(f"📚 Sources: {rag_response['sources']}")
            else:
                print(f"❌ RAG Failed: {rag_response['error']}")
            
            # Judge response
            judgment = await self.judge_response(test_query, rag_response)
            score = judgment.get("score", 0)
            reasoning = judgment.get("reasoning", "No reasoning")
            
            print(f"⚖️  Judge Score: {score}/10")
            print(f"💭 Reasoning: {reasoning}")
            
            results.append({
                "query": test_query,
                "response": rag_response,
                "judgment": judgment
            })
            
            total_score += score
            print("-" * 40)
        
        # Summary
        avg_score = total_score / len(self.test_queries)
        print(f"\n📈 SUMMARY")
        print(f"Average Score: {avg_score:.1f}/10")
        
        low_scores = [r for r in results if r["judgment"].get("score", 0) < 6]
        if low_scores:
            print(f"⚠️  {len(low_scores)} queries scored below 6:")
            for result in low_scores:
                query = result["query"]["query"]
                score = result["judgment"].get("score", 0)
                print(f"   - '{query}': {score}/10")
        
        return results

async def main():
    evaluator = RAGEvaluator()
    
    # Test connection
    test = await evaluator.query_rag_system("test")
    if not test["success"]:
        print(f"❌ Cannot connect to RAG system: {test['error']}")
        return
    
    print("✅ RAG system connected")
    
    # Run evaluation
    results = await evaluator.run_evaluation()
    
    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to evaluation_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 