import os
from dotenv import load_dotenv
import supabase
from supabase import create_client
import random
import requests

load_dotenv()
load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def query_groq(messages, model="llama3-8b-8192"):
    """Query Groq LLM for tag similarity analysis."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_message = {
        "role": "system",
        "content": "You are an expert at analyzing experience categories and finding similar tags. You help match user preferences with relevant experience categories."
    }
    
    full_messages = [system_message] + messages
    
    payload = {
        "model": model,
        "messages": full_messages
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"GROQ API error: {response.status_code} - {response.text}")

def get_similar_tags_with_llm(user_tags, available_tags, k=10):
    """Use LLM to find semantically similar tags from available tags."""
    prompt = f"""
    Given the user's preferred tags: {user_tags}
    
    And the available experience tags: {available_tags}
    
    Find the top {k} most semantically similar tags from the available tags that would match the user's preferences.
    Consider:
    - Direct matches
    - Related categories (e.g., 'adventure' matches 'outdoor', 'sports', 'adrenaline')
    - Complementary experiences (e.g., 'romantic' matches 'dining', 'wellness', 'luxury')
    - Contextual relationships
    
    Return only the tag names as a comma-separated list, no explanations.
    """
    
    try:
        response = query_groq([{"role": "user", "content": prompt}])
        # Parse the response to extract tag names
        similar_tags = [tag.strip() for tag in response.split(',')]
        return similar_tags[:k]
    except Exception as e:
        print(f"LLM tag analysis failed: {e}")
        # Fallback to exact matches
        return user_tags

def get_suggested_experiences(user_id, k=5):
    """
    Recommend k experiences for a user based on tags from their wishlisted and viewed experiences.
    Uses LLM to find semantically similar tags and experiences.
    Excludes already liked/viewed experiences. Returns a list of dicts with experience info.
    """
    # 1. Get all liked (wishlisted) and viewed experience IDs
    # wish list / saved / liked from swipes 
    wish_q = supabase_client.table("wishlists").select("experience_id").eq("user_id", user_id).execute()
    viewed_q = supabase_client.table("viewed_experiences").select("experience_id").eq("user_id", user_id).execute()
    wish_ids = set([row["experience_id"] for row in (wish_q.data or [])])
    viewed_ids = set([row["experience_id"] for row in (viewed_q.data or [])])
    all_seen_ids = wish_ids | viewed_ids
    
    if not all_seen_ids:
        # If user has no history, just return k random trending/featured experiences
        exp_q = supabase_client.table("experiences").select("*").or_("trending.eq.true,featured.eq.true").limit(k).execute()
        exps = exp_q.data or []
        random.shuffle(exps)
        return exps[:k]
    
    # 2. Get tags for those experiences
    exp_rows = supabase_client.table("experiences").select("id,category,niche_category,adventurous,romantic,group_a").in_("id", list(all_seen_ids)).execute()
    user_tags = set()
    for row in (exp_rows.data or []):
        for tag in [row.get("category"), row.get("niche_category")]:
            if tag:
                user_tags.add(tag)
        for bool_tag in ["adventurous", "romantic", "group_a"]:
            if row.get(bool_tag):
                user_tags.add(bool_tag)
    
    if not user_tags:
        # fallback: random trending/featured
        exp_q = supabase_client.table("experiences").select("*").or_("trending.eq.true,featured.eq.true").limit(k).execute()
        exps = exp_q.data or []
        random.shuffle(exps)
        return exps[:k]
    
    # 3. Get all available tags from experiences table
    all_exps = supabase_client.table("experiences").select("category,niche_category,adventurous,romantic,group_a").execute()
    available_tags = set()
    for row in (all_exps.data or []):
        for tag in [row.get("category"), row.get("niche_category")]:
            if tag:
                available_tags.add(tag)
        for bool_tag in ["adventurous", "romantic", "group_a"]:
            if row.get(bool_tag):
                available_tags.add(bool_tag)
    
    # 4. Use LLM to find similar tags
    similar_tags = get_similar_tags_with_llm(list(user_tags), list(available_tags))
    
    # 5. Find experiences with similar tags, excluding already seen
    tag_filters = []
    for tag in similar_tags:
        if tag in ["adventurous", "romantic", "group_a"]:
            tag_filters.append(f"{tag}.eq.true")
        else:
            tag_filters.append(f"category.eq.{tag}")
            tag_filters.append(f"niche_category.eq.{tag}")
    
    # Build or_ filter string
    or_filter = ",".join(tag_filters)
    
    # Query for matching experiences
    exp_q = supabase_client.table("experiences").select("*").or_(or_filter).execute()
    candidates = [row for row in (exp_q.data or []) if row["id"] not in all_seen_ids]
    
    # 6. Use LLM to rank and select the best matches
    if candidates:
        ranking_prompt = f"""
        Given the user's preferred tags: {list(user_tags)}
        
        Rank these experiences by relevance to the user's preferences:
        {[f"{i+1}. {exp['title']} (Category: {exp.get('category', 'N/A')}, Niche: {exp.get('niche_category', 'N/A')})" for i, exp in enumerate(candidates[:20])]}
        
        Return only the numbers of the top {k} most relevant experiences, separated by commas.
        """
        
        try:
            ranking_response = query_groq([{"role": "user", "content": ranking_prompt}])
            # Parse ranking response
            ranked_indices = [int(idx.strip()) - 1 for idx in ranking_response.split(',') if idx.strip().isdigit()]
            ranked_candidates = [candidates[i] for i in ranked_indices if i < len(candidates)]
            return ranked_candidates[:k]
        except Exception as e:
            print(f"LLM ranking failed: {e}")
            # Fallback to random selection
            random.shuffle(candidates)
            return candidates[:k]
    
    return []

if __name__ == "__main__":
    # Example usage
    user_id = input("Enter user_id: ")
    recs = get_suggested_experiences(user_id)
    for exp in recs:
        print(f"- {exp['title']} (ID: {exp['id']})")
