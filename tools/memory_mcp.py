#!/usr/bin/env python3

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class MemoryTool:
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
    
    def _load_memories(self) -> List[Dict]:
        """Load memories from JSON file or create empty list."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_memories(self):
        """Save memories to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2, default=str)
    
    def add_memory(self, topic: str, summary: str, tags: List[str] = None, priority: str = "normal") -> str:
        """Add a new memory entry."""
        memory_id = str(uuid.uuid4())[:8]
        memory = {
            "id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "summary": summary,
            "tags": tags or [],
            "priority": priority,  # low, normal, high
            "last_accessed": datetime.now().isoformat()
        }
        self.memories.append(memory)
        self._save_memories()
        return memory_id
    
    def get_memories(self, topic_filter: str = None, tag_filter: str = None, limit: int = None) -> List[Dict]:
        """Retrieve memories with optional filtering."""
        filtered = self.memories.copy()
        
        if topic_filter:
            filtered = [m for m in filtered if topic_filter.lower() in m['topic'].lower()]
        
        if tag_filter:
            filtered = [m for m in filtered if tag_filter in m.get('tags', [])]
        
        # Sort by priority then timestamp
        priority_order = {'high': 0, 'normal': 1, 'low': 2}
        filtered.sort(key=lambda x: (priority_order.get(x['priority'], 1), x['timestamp']), reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        # Update last_accessed for returned memories
        for memory in filtered:
            memory['last_accessed'] = datetime.now().isoformat()
        self._save_memories()
        
        return filtered
    
    def update_memory(self, memory_id: str, **updates) -> bool:
        """Update an existing memory by ID."""
        for memory in self.memories:
            if memory['id'] == memory_id:
                for key, value in updates.items():
                    if key in ['topic', 'summary', 'tags', 'priority']:
                        memory[key] = value
                memory['last_accessed'] = datetime.now().isoformat()
                self._save_memories()
                return True
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        original_count = len(self.memories)
        self.memories = [m for m in self.memories if m['id'] != memory_id]
        if len(self.memories) < original_count:
            self._save_memories()
            return True
        return False
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memories by query in topic and summary."""
        query_lower = query.lower()
        matches = []
        
        for memory in self.memories:
            score = 0
            if query_lower in memory['topic'].lower():
                score += 2
            if query_lower in memory['summary'].lower():
                score += 1
            if any(query_lower in tag.lower() for tag in memory.get('tags', [])):
                score += 1
            
            if score > 0:
                memory['_search_score'] = score
                matches.append(memory)
        
        matches.sort(key=lambda x: x['_search_score'], reverse=True)
        return matches[:limit]
    
    def get_recent_memories(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get memories from last N days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        recent = [
            m for m in self.memories 
            if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff
        ]
        recent.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent[:limit]
    
    def cleanup_old_memories(self, days: int = 90, keep_high_priority: bool = True):
        """Remove memories older than N days (optionally keeping high priority)."""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        
        if keep_high_priority:
            self.memories = [
                m for m in self.memories 
                if (datetime.fromisoformat(m['timestamp']).timestamp() > cutoff or 
                    m.get('priority') == 'high')
            ]
        else:
            self.memories = [
                m for m in self.memories 
                if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff
            ]
        
        self._save_memories()

# Example usage for MCP integration
def main():
    memory = MemoryTool()
    
    # Example operations
    mem_id = memory.add_memory(
        topic="Character Development", 
        summary="Decided protagonist has hockey background, affects romance arc",
        tags=["character", "romance", "sports"],
        priority="high"
    )
    
    # Search and retrieve
    recent = memory.get_recent_memories(days=7)
    search_results = memory.search_memories("romance")
    
    print(f"Added memory: {mem_id}")
    print(f"Recent memories: {len(recent)}")
    print(f"Romance-related: {len(search_results)}")

if __name__ == "__main__":
    main()#!/usr/bin/env python3

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class MemoryTool:
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
    
    def _load_memories(self) -> List[Dict]:
        """Load memories from JSON file or create empty list."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_memories(self):
        """Save memories to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2, default=str)
    
    def add_memory(self, topic: str, summary: str, tags: List[str] = None, priority: str = "normal") -> str:
        """Add a new memory entry."""
        memory_id = str(uuid.uuid4())[:8]
        memory = {
            "id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "summary": summary,
            "tags": tags or [],
            "priority": priority,  # low, normal, high
            "last_accessed": datetime.now().isoformat()
        }
        self.memories.append(memory)
        self._save_memories()
        return memory_id
    
    def get_memories(self, topic_filter: str = None, tag_filter: str = None, limit: int = None) -> List[Dict]:
        """Retrieve memories with optional filtering."""
        filtered = self.memories.copy()
        
        if topic_filter:
            filtered = [m for m in filtered if topic_filter.lower() in m['topic'].lower()]
        
        if tag_filter:
            filtered = [m for m in filtered if tag_filter in m.get('tags', [])]
        
        # Sort by priority then timestamp
        priority_order = {'high': 0, 'normal': 1, 'low': 2}
        filtered.sort(key=lambda x: (priority_order.get(x['priority'], 1), x['timestamp']), reverse=True)
        
        if limit:
            filtered = filtered[:limit]
        
        # Update last_accessed for returned memories
        for memory in filtered:
            memory['last_accessed'] = datetime.now().isoformat()
        self._save_memories()
        
        return filtered
    
    def update_memory(self, memory_id: str, **updates) -> bool:
        """Update an existing memory by ID."""
        for memory in self.memories:
            if memory['id'] == memory_id:
                for key, value in updates.items():
                    if key in ['topic', 'summary', 'tags', 'priority']:
                        memory[key] = value
                memory['last_accessed'] = datetime.now().isoformat()
                self._save_memories()
                return True
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        original_count = len(self.memories)
        self.memories = [m for m in self.memories if m['id'] != memory_id]
        if len(self.memories) < original_count:
            self._save_memories()
            return True
        return False
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memories by query in topic and summary."""
        query_lower = query.lower()
        matches = []
        
        for memory in self.memories:
            score = 0
            if query_lower in memory['topic'].lower():
                score += 2
            if query_lower in memory['summary'].lower():
                score += 1
            if any(query_lower in tag.lower() for tag in memory.get('tags', [])):
                score += 1
            
            if score > 0:
                memory['_search_score'] = score
                matches.append(memory)
        
        matches.sort(key=lambda x: x['_search_score'], reverse=True)
        return matches[:limit]
    
    def get_recent_memories(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get memories from last N days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        recent = [
            m for m in self.memories 
            if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff
        ]
        recent.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent[:limit]
    
    def cleanup_old_memories(self, days: int = 90, keep_high_priority: bool = True):
        """Remove memories older than N days (optionally keeping high priority)."""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        
        if keep_high_priority:
            self.memories = [
                m for m in self.memories 
                if (datetime.fromisoformat(m['timestamp']).timestamp() > cutoff or 
                    m.get('priority') == 'high')
            ]
        else:
            self.memories = [
                m for m in self.memories 
                if datetime.fromisoformat(m['timestamp']).timestamp() > cutoff
            ]
        
        self._save_memories()

# Example usage for MCP integration
def main():
    memory = MemoryTool()
    
    # Example operations
    mem_id = memory.add_memory(
        topic="Character Development", 
        summary="Decided protagonist has hockey background, affects romance arc",
        tags=["character", "romance", "sports"],
        priority="high"
    )
    
    # Search and retrieve
    recent = memory.get_recent_memories(days=7)
    search_results = memory.search_memories("romance")
    
    print(f"Added memory: {mem_id}")
    print(f"Recent memories: {len(recent)}")
    print(f"Romance-related: {len(search_results)}")

if __name__ == "__main__":
    main()