import os
import sys

# Ensure src is on sys.path
sys.path.insert(0, os.path.abspath('src'))

from skintellect.agents.copilot import (
    get_or_create_copilot_session,
    create_new_copilot_session,
    list_copilot_sessions,
)

# Test 1: Just exploring
s1 = create_new_copilot_session()
r1 = s1.ask('just exploring')
print('=== JUST EXPLORING ===')
print('Route:', r1['trace']['intent_route'])
print('Reason:', r1['trace']['route_reason'])
print('Activated:', r1['trace']['activated_agents'])
print('Bypassed:', r1['trace']['bypassed_agents'])
print('Events count:', len(r1['trace']['events']))
print('Curated products count:', len(r1['search'].get('products', [])))
print('Answer excerpt:\n', r1['answer'][:200].strip())
print('-' * 60)

# Test 2: Greeting
s2 = create_new_copilot_session()
r2 = s2.ask('hello')
print('=== GREETING (hello) ===')
print('Route:', r2['trace']['intent_route'])
print('Activated:', r2['trace']['activated_agents'])
print('Bypassed:', r2['trace']['bypassed_agents'])
print('Answer excerpt:\n', r2['answer'][:150].strip())
print('-' * 60)

# Test 3: Fungal-acne safe cleansers with no fragrance
s3 = create_new_copilot_session()
r3 = s3.ask('Find fungal-acne safe cleansers with no fragrance')
print('=== SEARCH (Fungal-acne safe cleansers) ===')
print('Route:', r3['trace']['intent_route'])
print('Activated:', r3['trace']['activated_agents'])
print('Bypassed:', r3['trace']['bypassed_agents'])
print('Products found:', r3['search'].get('total', 0))
print('Needs clarification:', r3['search'].get('needs_clarification'))
print('Answer excerpt:\n', r3['answer'][:200].strip())
print('-' * 60)

# Test 4: Compare barrier repair moisturizers with ceramides
s4 = create_new_copilot_session()
r4 = s4.ask('Compare barrier repair moisturizers with ceramides')
print('=== COMPARE (Ceramide moisturizers) ===')
print('Route:', r4['trace']['intent_route'])
print('Activated:', r4['trace']['activated_agents'])
print('Bypassed:', r4['trace']['bypassed_agents'])
print('Review insights loaded:', len(r4.get('review_insights', [])))
print('Answer excerpt:\n', r4['answer'][:200].strip())
print('-' * 60)

# Test 5: Sessions list
sessions = list_copilot_sessions()
print('=== SESSIONS LIST ===')
print('Total sessions created:', len(sessions))
for s in sessions:
    print(f"Session {s['session_id']}: title='{s['title']}', turns={s['user_turns']}")
