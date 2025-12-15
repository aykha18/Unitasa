# 📋 Agent System Rewrite: Incremental Implementation Plan

## 🎯 **Executive Summary**

**Goal:** Rewrite Unitasa's AI agent system to use OpenRouter + Groq with OpenAI fallback for cost optimization.

**Timeline:** 5-7 days with incremental rollout and rollback capability.

**Risk Level:** Medium (incremental approach minimizes risk)

---

## 📅 **Phase-by-Phase Implementation**

### **Phase 1: Foundation & Dependencies (Day 1)**

#### **1.1 Update Dependencies**
```bash
# Remove heavy dependencies
pip uninstall langchain langgraph

# Add lightweight alternatives
pip install openai httpx groq openrouter-py
```

#### **1.2 Create New Configuration**
- Add OpenRouter and Groq API settings
- Implement provider fallback logic
- Update cost tracking configuration

#### **1.3 Clean Up Existing Files**
**Safe Deletions:**
- `app/agents/base.py` (LangChain dependent)
- `app/agents/orchestrator.py` (LangGraph dependent)
- `app/agents/communication.py` (MCP complexity)
- `app/agents/resilience.py` (Over-engineered)
- `app/agents/monitoring.py` (Complex monitoring)

**Keep For Reference:**
- `app/agents/client_analysis.py` (business logic)
- `app/agents/content_creator.py` (content generation)
- `app/agents/social_content_generator.py` (social features)

---

### **Phase 2: Core Infrastructure (Day 2)**

#### **2.1 Create Cost-Optimized LLM Router**
```python
class OpenRouterGrokRouter:
    def __init__(self):
        self.providers = {
            'openrouter': OpenRouterClient(),
            'grok': GrokClient(),
            'openai': OpenAIClient()  # Fallback
        }

    def get_optimal_llm(self, task: str) -> LLMClient:
        # Cost-based routing logic
        pass
```

#### **2.2 Implement Base Agent Class**
```python
class CostOptimizedAgent:
    def __init__(self):
        self.llm_router = OpenRouterGrokRouter()
        self.cost_tracker = TokenCostTracker()

    async def execute_task(self, task: str, **kwargs) -> Dict:
        llm = self.llm_router.get_optimal_llm(task)
        response = await llm.generate(task, **kwargs)
        self.cost_tracker.record_usage(llm.provider, response.tokens)
        return response
```

#### **2.3 Add Token Cost Tracking**
- Per-provider cost monitoring
- Per-client token budgets
- Usage analytics and alerts

---

### **Phase 3: Core Agents Implementation (Days 3-4)**

#### **3.1 IngestionAgent (Day 3)**
**Responsibilities:**
- Website crawling and parsing
- Content summarization
- Document processing

**Migration:** Extract logic from existing agents, simplify for cost optimization

#### **3.2 KnowledgeBaseAgent (Day 3)**
**Responsibilities:**
- RAG implementation with Pinecone
- Chunking and embeddings
- Query optimization

**Migration:** Adapt existing RAG patterns with cost controls

#### **3.3 BusinessAnalysisAgent (Day 4)**
**Responsibilities:**
- Client profiling and analysis
- Business model identification
- Market positioning analysis

**Migration:** Extract proven methods from `ClientAnalysisAgent`

#### **3.4 ContentGenerationAgent (Day 4)**
**Responsibilities:**
- Marketing content creation
- Social media posts
- Email campaigns

**Migration:** Combine logic from `ContentCreatorAgent` and `SocialContentGeneratorAgent`

---

### **Phase 4: Strategy & Intelligence Agents (Day 5)**

#### **4.1 StrategyAgent**
**Responsibilities:**
- Market opportunity identification
- Competitive analysis
- Growth strategy recommendations

#### **4.2 MarketingAgent**
**Responsibilities:**
- Campaign planning and optimization
- Performance analysis
- ROI tracking

---

### **Phase 5: Integration & Testing (Days 6-7)**

#### **5.1 API Endpoint Updates**
- Update existing endpoints to use new agents
- Maintain backward compatibility
- Add cost monitoring endpoints

#### **5.2 Database Migration**
- Update agent-related tables if needed
- Migrate existing knowledge base data
- Add cost tracking tables

#### **5.3 Comprehensive Testing**
- Unit tests for each agent
- Integration tests with API endpoints
- Cost optimization validation
- Performance benchmarking

---

## 🔄 **Incremental Rollout Strategy**

### **Week 1: Parallel Development**
```
Old System: ✅ Production (unchanged)
New System: 🔧 Development (isolated)
```

### **Week 2: Gradual Migration**
```
Phase 1: Deploy new infrastructure alongside old
Phase 2: Route 10% of requests to new agents
Phase 3: Increase to 50% with monitoring
Phase 4: Full migration with rollback capability
```

### **Rollback Plan**
- Keep old agent system intact during migration
- Feature flags for switching between systems
- Database-level routing for gradual migration
- 1-hour rollback capability

---

## 📊 **Success Metrics & Validation**

### **Technical Metrics**
- **Cost Reduction:** 60-80% decrease in API costs
- **Response Time:** < 3 seconds average
- **Uptime:** 99.9% with fallback mechanisms
- **Code Coverage:** 80%+ test coverage

### **Business Metrics**
- **Agent Accuracy:** Maintain >90% quality scores
- **User Satisfaction:** No degradation in user experience
- **Feature Parity:** All existing functionality preserved

---

## 🚨 **Risk Mitigation**

### **High-Risk Items**
1. **Data Migration:** Test thoroughly with production data subset
2. **API Compatibility:** Maintain exact same external interfaces
3. **Cost Monitoring:** Implement hard limits and alerts

### **Contingency Plans**
1. **Immediate Rollback:** Feature flags allow instant reversion
2. **Partial Rollback:** Route specific clients back to old system
3. **Hybrid Operation:** Run both systems in parallel during transition

---

## 🔧 **Technical Architecture Changes**

### **Before (Complex)**
```
LangChain Agents → LangGraph Orchestrator → MCP → Multiple LLMs
```

### **After (Optimized)**
```
Cost-Optimized Agents → OpenRouter/Groq Router → Single API Interface
```

### **Key Simplifications**
- Remove LangChain abstraction overhead
- Direct API calls to providers
- Simplified agent communication
- Cost-aware routing decisions

---

## 📋 **Daily Implementation Checklist**

### **Day 1: Foundation**
- [ ] Update requirements.txt
- [ ] Clean up unwanted files
- [ ] Create new configuration structure
- [ ] Set up basic project structure

### **Day 2: Infrastructure**
- [ ] Implement OpenRouter client
- [ ] Implement Grok client
- [ ] Create cost-optimized router
- [ ] Add token tracking system

### **Day 3: Core Agents I**
- [ ] Implement IngestionAgent
- [ ] Implement KnowledgeBaseAgent
- [ ] Basic RAG functionality
- [ ] Unit tests for core agents

### **Day 4: Core Agents II**
- [ ] Implement BusinessAnalysisAgent
- [ ] Implement ContentGenerationAgent
- [ ] Migrate business logic from old agents
- [ ] Integration tests

### **Day 5: Advanced Agents**
- [ ] Implement StrategyAgent
- [ ] Implement MarketingAgent
- [ ] Add advanced features
- [ ] Performance optimization

### **Day 6: Integration**
- [ ] Update API endpoints
- [ ] Database migration
- [ ] Feature flag implementation
- [ ] End-to-end testing

### **Day 7: Validation & Launch**
- [ ] Comprehensive testing
- [ ] Performance benchmarking
- [ ] Cost analysis validation
- [ ] Production deployment

---

## 🎯 **Definition of Done**

- [ ] All agents functional with OpenRouter/Groq
- [ ] OpenAI fallback working when primary providers unavailable
- [ ] Cost reduction of 60%+ achieved
- [ ] All existing API endpoints maintained
- [ ] Comprehensive test coverage
- [ ] Performance benchmarks met
- [ ] Rollback capability maintained
- [ ] Documentation updated

---

*This incremental plan ensures minimal risk while achieving the cost optimization goals of the new agent architecture.*