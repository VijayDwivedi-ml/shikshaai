import asyncio
import time
import uuid
from typing import List, Dict, Any
from datetime import datetime

from tools import GeminiAsyncTools
from schemas import TeachingRequest, AgentResponse, ResourceRecommendation
from config import settings
from logger import logger

class TeachingResourceAgent:
    """
    Async ADK-style agent with Plan-Act-Reflect pattern
    Uses Gemini API tools for autonomous teaching resource discovery
    """
    
    def __init__(self):
        self.name = "TeachingResourceFinder"
        self.version = "1.0.0"
        self.tools = GeminiAsyncTools()
        
        logger.info(f"Initialized agent: {self.name} v{self.version}")
    
    async def run(self, request: TeachingRequest) -> AgentResponse:
        """
        Main async agent execution flow with Plan-Act-Reflect pattern
        """
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.perf_counter()
        
        logger.info(
            f"Starting agent execution",
            extra={
                "agent": self.name,
                "request_id": request_id,
                "topic": request.topic,
                "grade": request.grade,
                "constraints": request.constraints
            }
        )
        
        try:
            # ===== PLAN Phase =====
            plan_start = time.perf_counter()
            plan = await self._create_plan(request)
            plan_duration = (time.perf_counter() - plan_start) * 1000
            
            logger.debug(
                f"Planning complete",
                extra={
                    "agent": self.name,
                    "phase": "plan",
                    "duration_ms": plan_duration,
                    "plan": plan[:100] + "..." if len(plan) > 100 else plan
                }
            )
            
            # ===== ACT Phase =====
            act_start = time.perf_counter()
            
            # Generate ideas (async)
            ideas = await self.tools.generate_resource_ideas(
                request.topic, 
                request.grade, 
                request.constraints
            )
            
            # Batch evaluate ideas in parallel (async)
            evaluations = await self.tools.evaluate_resources_batch(
                ideas[:8],  # Limit to 8 for performance
                request.topic,
                request.grade
            )
            
            act_duration = (time.perf_counter() - act_start) * 1000
            
            logger.debug(
                f"Action phase complete",
                extra={
                    "agent": self.name,
                    "phase": "act",
                    "duration_ms": act_duration,
                    "ideas_generated": len(ideas),
                    "resources_evaluated": len(evaluations)
                }
            )
            
            # ===== REFLECT Phase =====
            reflect_start = time.perf_counter()
            
            # Filter and sort
            suitable_resources = [
                eval_result for eval_result in evaluations
                if eval_result.get("suitability_score", 0) > 0.6
            ]
            
            # Sort by score
            suitable_resources.sort(
                key=lambda x: x.get("suitability_score", 0), 
                reverse=True
            )
            
            # Take top N
            top_resources = suitable_resources[:request.max_resources]
            
            # Format as Pydantic models
            recommendations = [
                ResourceRecommendation(
                    resource=r["resource"],
                    suitability_score=r["suitability_score"],
                    reasoning=r["reasoning"],
                    time_estimate=r["time_estimate"],
                    cost_level=r["cost_level"],
                    materials_needed=r["materials_needed"]
                )
                for r in top_resources
            ]
            
            reflect_duration = (time.perf_counter() - reflect_start) * 1000
            
            # ===== Prepare Response =====
            total_duration = (time.perf_counter() - start_time) * 1000
            
            agent_notes = (
                f"PLAN: {plan}\n"
                f"Generated {len(ideas)} ideas, evaluated {len(evaluations)} resources. "
                f"Found {len(suitable_resources)} suitable resources, returning top {len(recommendations)}. "
                f"Phases: Plan({plan_duration:.1f}ms), Act({act_duration:.1f}ms), Reflect({reflect_duration:.1f}ms)"
            )
            
            response = AgentResponse(
                request_id=request_id,
                recommendations=recommendations,
                agent_notes=agent_notes,
                processing_time_ms=total_duration,
                agent_version=self.version
            )
            
            logger.info(
                f"Agent execution successful",
                extra={
                    "agent": self.name,
                    "request_id": request_id,
                    "total_duration_ms": total_duration,
                    "recommendations_count": len(recommendations),
                    "top_score": recommendations[0].suitability_score if recommendations else 0
                }
            )
            
            return response
            
        except Exception as e:
            total_duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Agent execution failed",
                extra={
                    "agent": self.name,
                    "request_id": request_id,
                    "error": str(e),
                    "duration_ms": total_duration
                },
                exc_info=True
            )
            
            # Return error response
            return AgentResponse(
                request_id=request_id,
                recommendations=[],
                agent_notes=f"Agent error: {str(e)}",
                processing_time_ms=total_duration,
                agent_version=self.version
            )
    
    async def _create_plan(self, request: TeachingRequest) -> str:
        """
        Async planning phase: Determine strategy based on constraints
        """
        plan_elements = []
        
        # Analyze constraints
        constraints = request.constraints or []
        
        if "hands-on" in constraints:
            plan_elements.append("Prioritize hands-on, experiential learning activities")
        
        if "digital" in constraints:
            plan_elements.append("Include technology-enhanced resources")
        
        if "low-cost" in constraints:
            plan_elements.append("Focus on low-cost or no-cost materials")
        
        if "group" in constraints:
            plan_elements.append("Design for collaborative group work")
        
        # Add grade-specific considerations
        grade_num = int(request.grade) if request.grade.isdigit() else 0
        if grade_num <= 5:
            plan_elements.append("Use concrete, visual examples appropriate for elementary")
        elif grade_num <= 8:
            plan_elements.append("Balance concrete and abstract thinking for middle school")
        else:
            plan_elements.append("Incorporate abstract concepts and critical thinking for high school")
        
        # Default plan elements
        if not plan_elements:
            plan_elements = [
                "Find diverse resource types (activities, discussions, projects)",
                "Ensure age-appropriate content",
                "Include assessment considerations"
            ]
        
        return f"Teaching strategy for grade {request.grade}: {'; '.join(plan_elements)}"
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Async health check for the agent
        """
        try:
            # Test Gemini connection with a simple async call
            test_start = time.perf_counter()
            test_ideas = await self.tools.generate_resource_ideas("test", "5", ["quick"])
            test_duration = (time.perf_counter() - test_start) * 1000
            
            return {
                "status": "healthy",
                "agent": self.name,
                "version": self.version,
                "gemini_connected": len(test_ideas) > 0,
                "test_duration_ms": test_duration,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "agent": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }