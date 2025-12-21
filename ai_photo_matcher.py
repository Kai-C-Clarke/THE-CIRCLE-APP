#!/usr/bin/env python3
"""
Simple Photo Matching for Memories
Uses metadata only (no AI vision) - fast and reliable
"""

import sqlite3
import os
from difflib import SequenceMatcher

def text_similarity(a, b):
    """Calculate similarity between two strings (0-100)."""
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def match_photo_to_memory(memory_text, memory_year, photo_metadata):
    """
    Match photo to memory using metadata only.
    
    Returns: {
        'matches': bool,
        'confidence': float (0-100),
        'reasoning': str
    }
    """
    photo_title = photo_metadata.get('title', '')
    photo_desc = photo_metadata.get('description', '')
    photo_year = photo_metadata.get('year', None)
    photo_filename = photo_metadata.get('filename', '')
    
    confidence = 0
    reasons = []
    
    # Stop words to ignore (common words that don't help matching)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                  'can', 'could', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it',
                  'we', 'they', 'this', 'that', 'these', 'those'}
    
    # Clean and extract meaningful words from memory
    memory_lower = memory_text.lower()
    memory_words = set(w for w in memory_lower.split() if w not in stop_words and len(w) > 2)
    
    # MOST IMPORTANT: Check for exact phrase matches in title
    if photo_title and len(photo_title) > 3:
        if photo_title.lower() in memory_lower:
            confidence += 60
            reasons.append(f"Exact title '{photo_title}' found in memory")
    
    # Check title word matches (meaningful words only)
    if photo_title:
        title_words = set(w for w in photo_title.lower().split() if w not in stop_words and len(w) > 2)
        overlap = memory_words & title_words
        if overlap:
            boost = len(overlap) * 20
            confidence += boost
            reasons.append(f"Title keywords: {', '.join(list(overlap)[:3])}")
    
    # Check description match (meaningful words only)
    if photo_desc:
        desc_words = set(w for w in photo_desc.lower().split() if w not in stop_words and len(w) > 2)
        overlap = memory_words & desc_words
        if overlap:
            boost = len(overlap) * 10
            confidence += boost
            reasons.append(f"Description matches: {len(overlap)} keywords")
    
    # Check filename match (remove extension, numbers, underscores)
    clean_filename = photo_filename.replace('.jpg', '').replace('.png', '').replace('_', ' ')
    clean_filename = ''.join(c if c.isalpha() or c.isspace() else ' ' for c in clean_filename)
    filename_words = set(w for w in clean_filename.lower().split() if w not in stop_words and len(w) > 2)
    overlap = memory_words & filename_words
    if overlap:
        boost = len(overlap) * 15
        confidence += boost
        reasons.append(f"Filename keywords: {', '.join(list(overlap)[:2])}")
    
    # Check year proximity
    if photo_year and memory_year:
        try:
            year_diff = abs(int(photo_year) - int(memory_year))
            if year_diff == 0:
                confidence += 25
                reasons.append(f"Exact year match ({memory_year})")
            elif year_diff <= 1:
                confidence += 15
                reasons.append(f"Year within 1 year ({year_diff} year difference)")
            elif year_diff <= 3:
                confidence += 8
                reasons.append(f"Year within 3 years ({year_diff} years apart)")
        except (ValueError, TypeError):
            pass
    
    # Cap confidence at 100
    confidence = min(confidence, 100)
    
    # Determine if it matches
    matches = confidence >= 50
    
    reasoning = '; '.join(reasons) if reasons else "No significant matches found"
    
    return {
        'matches': matches,
        'confidence': confidence,
        'reasoning': reasoning
    }

def suggest_photos_for_memory(memory_id, db_path='circle_memories.db', confidence_threshold=60):
    """
    Suggest photos for a specific memory using metadata matching.
    
    Returns list of suggestions sorted by confidence.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get memory
    cursor.execute('SELECT id, text, year FROM memories WHERE id = ?', (memory_id,))
    memory = cursor.fetchone()
    
    if not memory:
        print(f"Memory {memory_id} not found")
        return []
    
    mem_id, mem_text, mem_year = memory
    
    print(f"\n{'='*80}")
    print(f"Finding photos for Memory {mem_id}")
    print(f"Year: {mem_year}")
    print(f"Text: {mem_text[:100]}...")
    print(f"{'='*80}\n")
    
    # Get all photos
    cursor.execute('''
        SELECT id, filename, original_filename, title, description, year
        FROM media
        WHERE file_type = 'image'
    ''')
    
    photos = cursor.fetchall()
    suggestions = []
    
    for photo in photos:
        photo_id, filename, original, title, desc, year = photo
        
        print(f"Analyzing: {title or original} ({year})...", end=' ')
        
        # Get metadata match
        metadata = {
            'title': title or '',
            'description': desc or '',
            'year': year,
            'filename': original or filename
        }
        
        result = match_photo_to_memory(mem_text, mem_year, metadata)
        
        if result['matches'] and result['confidence'] >= confidence_threshold:
            suggestions.append({
                'photo_id': photo_id,
                'filename': filename,
                'title': title or original,
                'confidence': result['confidence'],
                'reasoning': result['reasoning']
            })
            print(f"✓ {result['confidence']:.0f}% match")
        else:
            print(f"✗ {result['confidence']:.0f}% (below threshold)")
    
    conn.close()
    
    # Sort by confidence
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    
    return suggestions

def suggest_all_memories(db_path='circle_memories.db', confidence_threshold=70):
    """
    Process all memories and suggest photo matches.
    Returns dict of {memory_id: [suggestions]}
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, text FROM memories')
    memories = cursor.fetchall()
    
    all_suggestions = {}
    
    for mem_id, mem_text in memories:
        print(f"\n\nProcessing Memory {mem_id}...")
        suggestions = suggest_photos_for_memory(mem_id, db_path, confidence_threshold)
        
        if suggestions:
            all_suggestions[mem_id] = suggestions
            print(f"\n✓ Found {len(suggestions)} suggestions for Memory {mem_id}")
        else:
            print(f"\n○ No suggestions for Memory {mem_id}")
    
    conn.close()
    return all_suggestions

def apply_suggestion(memory_id, photo_id, db_path='circle_memories.db'):
    """Accept a suggestion and link the photo."""
    conn = sqlite3.connect(db_path)
    
    # Get current max order
    cursor = conn.execute(
        'SELECT COALESCE(MAX(display_order), -1) FROM memory_media WHERE memory_id = ?',
        (memory_id,)
    )
    max_order = cursor.fetchone()[0]
    
    # Insert link
    conn.execute(
        'INSERT OR IGNORE INTO memory_media (memory_id, media_id, display_order) VALUES (?, ?, ?)',
        (memory_id, photo_id, max_order + 1)
    )
    
    conn.commit()
    conn.close()
    print(f"✓ Linked photo {photo_id} to memory {memory_id}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple photo matching for memories (metadata only)')
    parser.add_argument('--memory', type=int, help='Suggest photos for specific memory ID')
    parser.add_argument('--all', action='store_true', help='Process all memories')
    parser.add_argument('--threshold', type=int, default=60, help='Confidence threshold (0-100)')
    parser.add_argument('--database', default='circle_memories.db', help='Database path')
    
    args = parser.parse_args()
    
    if args.memory:
        # Single memory
        suggestions = suggest_photos_for_memory(
            args.memory, 
            args.database, 
            args.threshold
        )
        
        if suggestions:
            print(f"\n{'='*80}")
            print(f"SUGGESTIONS FOR MEMORY {args.memory}")
            print(f"{'='*80}")
            
            for i, sug in enumerate(suggestions, 1):
                print(f"\n{i}. {sug['title']}")
                print(f"   Confidence: {sug['confidence']:.0f}%")
                print(f"   Reasoning: {sug['reasoning']}")
            
            print(f"\n{'='*80}")
            print("To accept a suggestion:")
            print(f"  python3 -c \"from simple_photo_matcher import apply_suggestion; apply_suggestion({args.memory}, PHOTO_ID)\"")
        else:
            print(f"\n○ No suggestions above {args.threshold}% confidence")
    
    elif args.all:
        # All memories
        all_sug = suggest_all_memories(args.database, args.threshold)
        
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Processed {len(all_sug)} memories with suggestions")
        
        total_suggestions = sum(len(sug) for sug in all_sug.values())
        print(f"Total suggestions: {total_suggestions}")
    
    else:
        parser.print_help()
