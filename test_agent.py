import asyncio
import pytest
from schemas import TeachingRequest
from agent import TeachingResourceAgent

# Simple async test
async def test_agent_basic():
    """Test basic agent functionality"""
    agent = TeachingResourceAgent()
    
    # Test request
    request = TeachingRequest(
        topic="water cycle",
        grade="4",
        constraints=["hands-on"],
        max_resources=2
    )
    
    # Run agent
    response = await agent.run(request)
    
    # Assertions
    assert response.request_id is not None
    assert len(response.recommendations) <= 2
    assert response.processing_time_ms > 0
    
    print(f"✅ Test passed!")
    print(f"   Request ID: {response.request_id}")
    print(f"   Recommendations: {len(response.recommendations)}")
    print(f"   Processing time: {response.processing_time_ms:.0f}ms")
    
    return response

# Run tests
if __name__ == "__main__":
    print("🧪 Running agent tests...")
    result = asyncio.run(test_agent_basic())
    print("✅ All tests completed!")