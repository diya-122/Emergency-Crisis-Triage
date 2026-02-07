# AI-Enhanced Resource Matching

## Overview

The Emergency Crisis Triage System now includes an **AI-Enhanced Resource Matching** feature that uses Large Language Models (LLMs) to provide explainable, transparent resource recommendations while maintaining strict human-in-the-loop control.

## Key Principles

### 🔒 Safety First
- **No Autonomous Dispatch**: The AI never dispatches resources automatically
- **Human-in-the-Loop**: All final decisions require human dispatcher confirmation
- **Verified Resources Only**: Only pre-verified resources are considered
- **Transparent Reasoning**: Every recommendation includes full explanation

### 🎯 Core Capabilities

1. **Intelligent Matching**: Uses LLM reasoning to match emergency requests with optimal resources
2. **Explainable Scoring**: Provides detailed breakdown of scoring factors:
   - Suitability (40%)
   - Availability (30%)
   - Capacity (15%)
   - Distance (15%)
3. **Trade-off Analysis**: Identifies and explains resource allocation trade-offs
4. **Fallback Safety**: Automatically falls back to rule-based matching if AI fails

## Backend System Prompt

The AI operates under a comprehensive system prompt that enforces:

### ✅ Required Behaviors
- Always explain reasoning
- Always defer to humans
- Maintain transparency
- Prioritize safety over speed
- Flag uncertainty explicitly

### ❌ Prohibited Actions
- No autonomous dispatch
- No unverified resources
- No opaque scoring
- No hidden reasoning

## Configuration

### Enabling AI Matching

In your `.env` file:

```bash
# Enable AI-enhanced matching
ENABLE_AI_MATCHING=true

# Minimum extraction confidence to use AI (0.0-1.0)
AI_MATCHING_MIN_CONFIDENCE=0.6

# LLM Provider (openai or anthropic)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview

# API Keys
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ENABLE_AI_MATCHING` | `false` | Enable/disable AI-enhanced matching |
| `AI_MATCHING_MIN_CONFIDENCE` | `0.6` | Minimum confidence threshold (0.0-1.0) |
| `LLM_PROVIDER` | `openai` | LLM provider: `openai` or `anthropic` |
| `LLM_MODEL` | `gpt-4-turbo-preview` | Model to use for matching |
| `LLM_TEMPERATURE` | `0.3` | Lower = more deterministic |
| `LLM_MAX_TOKENS` | `2000` | Maximum response length |

## How It Works

### 1. Request Analysis
The system receives a structured emergency request:
```json
{
  "request_id": "REQ_1023",
  "needs": [{"type": "medical", "confidence": 0.92}],
  "people_affected": 5,
  "location": {"address": "Zone C, near river"},
  "urgency_score": 0.92,
  "confidence": "high"
}
```

### 2. Resource Registry
Only verified resources are considered:
```json
{
  "resource_id": "AMB_021",
  "type": "ambulance",
  "services": ["medical", "transport"],
  "availability": "available",
  "capacity": 6,
  "verified": true
}
```

### 3. AI Analysis
The LLM analyzes the match using the system prompt and returns:
```json
{
  "recommendations": [
    {
      "resource_id": "AMB_021",
      "final_score": 0.86,
      "component_scores": {
        "suitability": 0.95,
        "availability": 0.85,
        "capacity": 0.90,
        "distance": 0.75
      },
      "reasoning": [
        "Verified medical transport resource",
        "Currently available",
        "Sufficient capacity for 5 people",
        "Estimated response time of 8 minutes"
      ],
      "trade_offs": [
        "Moderate distance but high suitability"
      ],
      "confidence": "high"
    }
  ],
  "human_action_required": true
}
```

### 4. Fallback Mechanism
If AI matching fails or confidence is too low, the system automatically falls back to rule-based matching:
- Uses predefined scoring algorithms
- Applies weighted factors
- Provides deterministic results

## API Usage

### Forcing AI or Rule-Based Matching

```python
# Force AI matching
matches = await resource_matching_service.match_resources(
    extracted_info=request_data,
    max_matches=5,
    use_ai=True
)

# Force rule-based matching
matches = await resource_matching_service.match_resources(
    extracted_info=request_data,
    max_matches=5,
    use_ai=False
)

# Use default behavior (based on config)
matches = await resource_matching_service.match_resources(
    extracted_info=request_data,
    max_matches=5
)
```

## Safety Guarantees

### Verification Constraint
```python
# Only verified resources are fetched
resources = await Resource.find({
    "status": "active",
    "verified": True  # Required
}).to_list()
```

### Human Confirmation Required
All AI recommendations include:
- `"human_action_required": true`
- Explicit confidence levels
- Clear warnings and limitations
- Trade-off analysis

### Uncertainty Handling
When the AI encounters:
- No suitable resources
- Insufficient capacity
- Ambiguous locations

It will:
- Flag the issue clearly
- Suggest fallback options
- Request human review
- Provide alternative recommendations

## Transparency Features

### Explainable Scoring
Every recommendation includes:
1. **Component Scores**: Individual factor breakdowns
2. **Reasoning**: Step-by-step explanation
3. **Trade-offs**: Identified pros and cons
4. **Confidence Level**: High, medium, or low

### Audit Trail
All AI decisions are logged with:
- Timestamp
- Input data
- AI reasoning
- Final recommendations
- Human override (if applicable)

## Best Practices

### 1. Start with AI Disabled
- Test rule-based matching first
- Verify system behavior
- Enable AI once comfortable

### 2. Monitor Confidence Levels
- Adjust `AI_MATCHING_MIN_CONFIDENCE` based on performance
- Higher threshold = more conservative (falls back more often)
- Lower threshold = more AI usage

### 3. Review AI Recommendations
- Always review AI reasoning
- Look for unexpected patterns
- Report inconsistencies

### 4. Validate with Real Scenarios
- Test with diverse emergency types
- Verify against known good matches
- Compare AI vs rule-based results

## Troubleshooting

### AI Matching Not Working
1. Check `ENABLE_AI_MATCHING=true` in `.env`
2. Verify API key is valid
3. Check extraction confidence meets minimum
4. Review logs for errors

### Always Falls Back to Rules
- Extraction confidence may be too low
- Reduce `AI_MATCHING_MIN_CONFIDENCE`
- Check LLM API connectivity
- Verify LLM model is available

### Poor AI Recommendations
- Adjust `LLM_TEMPERATURE` (lower = more conservative)
- Try different LLM model
- Verify resource data quality
- Check system prompt alignment

## Performance Considerations

### Latency
- AI matching adds 1-3 seconds per request
- Rule-based matching is instant
- Use AI selectively for complex cases

### Costs
- Each AI match costs API tokens
- Monitor usage in production
- Consider rate limiting
- Use rule-based for simple cases

### Scalability
- AI requests are stateless
- Can be cached for similar requests
- Consider batch processing
- Implement request throttling

## Future Enhancements

- [ ] Learning from dispatcher overrides
- [ ] Contextual awareness of ongoing emergencies
- [ ] Multi-resource coordination
- [ ] Predictive resource positioning
- [ ] Real-time capacity forecasting
- [ ] Historical pattern analysis

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review configuration: `.env`
3. Test with simple cases first
4. Compare AI vs rule-based results

## References

- [Backend System Prompt](../backend/app/services/resource_matching.py#L18)
- [Configuration Guide](../README.md#configuration)
- [API Documentation](http://localhost:8000/docs)
