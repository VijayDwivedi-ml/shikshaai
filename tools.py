import google.generativeai as genai
import asyncio
import re
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
import logging

from config import settings
from logger import logger

class RateLimiter:
    """Async rate limiter for Gemini API"""
    
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.request_count = 0
        self.last_reset = datetime.now()
        
    async def acquire(self):
        """Acquire semaphore for API call"""
        async with self.semaphore:
            self.request_count += 1
            # Simple rate tracking (could be enhanced)
            if (datetime.now() - self.last_reset).seconds > 60:
                self.request_count = 1
                self.last_reset = datetime.now()
            return self

class GeminiAsyncTools:
    """Async tools for Gemini API calls"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize models
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Rate limiter to prevent hitting API limits
        self.rate_limiter = RateLimiter(settings.MAX_CONCURRENT_TASKS)
        
        # Cache for requests (simple in-memory)
        self._cache = {}
        logger.info(f"Gemini tools initialized with {settings.MAX_CONCURRENT_TASKS} max concurrent tasks")
    
    async def generate_resource_ideas(
        self, 
        topic: str, 
        grade: str, 
        constraints: List[str] = None
    ) -> List[str]:
        """
        Async tool 1: Generate teaching resource ideas
        Returns list of resource descriptions
        """
        cache_key = f"ideas_{topic}_{grade}_{'_'.join(constraints or [])}"
        
        # Check cache
        if settings.USE_CACHE and cache_key in self._cache:
            logger.info(f"Cache hit for ideas: {topic}")
            return self._cache[cache_key]
        
        # Acquire rate limiter
        await self.rate_limiter.acquire()
        
        # Create prompt
        constraints_text = f" with constraints: {', '.join(constraints)}" if constraints else ""
        prompt = f"""
        As an expert teacher for grade {grade}, generate 5 creative teaching resource ideas 
        for the topic: "{topic}"{constraints_text}.
        
        Requirements:
        1. Age-appropriate for grade {grade}
        2. Practical to implement in a classroom
        3. Aligned with educational standards
        4. Include at least one hands-on activity
        
        Format: Return only bullet points starting with "-"
        """
        
        try:
            # Async call to Gemini
            start_time = datetime.now()
            response = await self.model.generate_content_async(prompt)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse response
            ideas = self._parse_bullet_points(response.text)
            
            # Log and cache
            logger.info(
                f"Generated {len(ideas)} ideas for {topic}",
                extra={
                    "agent": "gemini_tools",
                    "topic": topic,
                    "grade": grade,
                    "duration_ms": duration,
                    "ideas_count": len(ideas)
                }
            )
            
            if settings.USE_CACHE:
                self._cache[cache_key] = ideas
            
            return ideas
            
        except Exception as e:
            logger.error(f"Error generating ideas: {str(e)}", exc_info=True)
            # Fallback ideas
            return [
                f"Interactive discussion about {topic}",
                f"Group activity exploring {topic}",
                f"Visual presentation on {topic}",
                f"Hands-on experiment related to {topic}",
                f"Research project on {topic}"
            ]
    
    async def evaluate_resource(
        self, 
        resource: str, 
        topic: str, 
        grade: str
    ) -> Dict[str, Any]:
        """
        Async tool 2: Evaluate a single resource
        Returns evaluation dictionary with score and reasoning
        """
        cache_key = f"eval_{resource}_{topic}_{grade}"
        
        # Check cache
        if settings.USE_CACHE and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Acquire rate limiter
        await self.rate_limiter.acquire()
        
        # Create evaluation prompt
        prompt = f"""
        Evaluate this teaching resource for grade {grade} students learning about {topic}:
        
        Resource: "{resource}"
        
        Please evaluate on:
        1. Suitability for grade {grade} (0-1 score)
        2. Estimated implementation time
        3. Cost level (low/medium/high)
        4. Required materials
        5. Educational effectiveness reasoning
        
        Format your response as JSON:
        {{
            "suitability_score": 0.85,
            "time_estimate": "45 minutes",
            "cost_level": "low",
            "materials_needed": ["item1", "item2"],
            "reasoning": "Clear explanation here"
        }}
        """
        
        try:
            # Async evaluation call
            start_time = datetime.now()
            response = await self.model.generate_content_async(prompt)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse JSON response
            evaluation = self._parse_evaluation_json(response.text)
            
            # Add resource to evaluation
            evaluation["resource"] = resource
            
            # Log
            logger.debug(
                f"Evaluated resource: {resource[:50]}...",
                extra={
                    "agent": "gemini_tools",
                    "resource": resource[:100],
                    "score": evaluation.get("suitability_score", 0),
                    "duration_ms": duration
                }
            )
            
            if settings.USE_CACHE:
                self._cache[cache_key] = evaluation
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating resource: {str(e)}", exc_info=True)
            # Return default evaluation
            return {
                "resource": resource,
                "suitability_score": 0.5,
                "time_estimate": "30-45 minutes",
                "cost_level": "medium",
                "materials_needed": ["Basic classroom supplies"],
                "reasoning": "Default evaluation due to error"
            }
    
    async def evaluate_resources_batch(
        self, 
        resources: List[str], 
        topic: str, 
        grade: str
    ) -> List[Dict[str, Any]]:
        """
        Async tool 3: Batch evaluate multiple resources in parallel
        Uses asyncio.gather for concurrent API calls
        """
        # Create tasks for all resources
        tasks = [
            self.evaluate_resource(resource, topic, grade)
            for resource in resources
        ]
        
        # Execute all evaluations concurrently
        start_time = datetime.now()
        evaluations = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # Handle any exceptions
        valid_evaluations = []
        for i, eval_result in enumerate(evaluations):
            if isinstance(eval_result, Exception):
                logger.error(f"Batch evaluation failed for resource {i}: {eval_result}")
                # Add fallback evaluation
                valid_evaluations.append({
                    "resource": resources[i],
                    "suitability_score": 0.5,
                    "time_estimate": "30 minutes",
                    "cost_level": "medium",
                    "materials_needed": ["Classroom supplies"],
                    "reasoning": "Evaluation failed, using default"
                })
            else:
                valid_evaluations.append(eval_result)
        
        logger.info(
            f"Batch evaluated {len(resources)} resources",
            extra={
                "agent": "gemini_tools",
                "batch_size": len(resources),
                "duration_ms": duration,
                "duration_per_resource": duration / len(resources) if resources else 0
            }
        )
        
        return valid_evaluations
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """Parse bullet points from Gemini response"""
        if not text:
            return []
        
        # Extract lines starting with bullet points
        lines = [line.strip() for line in text.split('\n')]
        bullets = []
        
        for line in lines:
            # Match various bullet formats
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                # Remove bullet and clean
                cleaned = line[1:].strip()
                if cleaned:
                    bullets.append(cleaned)
            elif re.match(r'^\d+[\.\)]', line):
                # Numbered list
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', line)
                if cleaned:
                    bullets.append(cleaned)
        
        return bullets[:10]  # Limit to 10 ideas
    
    def _parse_evaluation_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON evaluation from Gemini response"""
        try:
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                import json as json_lib
                return json_lib.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return {
            "suitability_score": 0.7,
            "time_estimate": self._extract_time_estimate(text),
            "cost_level": self._extract_cost_level(text),
            "materials_needed": self._extract_materials(text),
            "reasoning": text[:200] if text else "No evaluation provided"
        }
    
    def _extract_time_estimate(self, text: str) -> str:
        """Extract time estimate from text"""
        time_patterns = [
            r'(\d+-\d+\s*minutes?)',
            r'(\d+\s*minutes?)',
            r'(\d+-\d+\s*hours?)',
            r'(\d+\s*hours?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "30-45 minutes"
    
    def _extract_cost_level(self, text: str) -> str:
        """Extract cost level from text"""
        text_lower = text.lower()
        if 'low cost' in text_lower or 'inexpensive' in text_lower:
            return "low"
        elif 'high cost' in text_lower or 'expensive' in text_lower:
            return "high"
        else:
            return "medium"
    
    def _extract_materials(self, text: str) -> List[str]:
        """Extract materials from text"""
        materials = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'material' in line_lower or 'supply' in line_lower or 'need' in line_lower:
                # Try to extract items
                items = re.findall(r'[-•*]\s*([^.,;]+)', line)
                materials.extend([item.strip() for item in items if item.strip()])
        
        return materials[:5] if materials else ["Classroom supplies"]