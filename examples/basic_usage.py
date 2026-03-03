"""Basic usage examples for LLMGuard."""

from llmguard import LLMGuard

# --- Example 1: Word Filter ---
print("=" * 60)
print("Example 1: Word Filter")
print("=" * 60)

guard = LLMGuard({
    "word_filter": {
        "enabled": True,
        "blocked_words": ["forbidden", "banned"],
        "blocked_phrases": ["not allowed"],
        "use_profanity_list": True,
    }
})

texts = [
    "This is a normal sentence.",
    "This contains a forbidden word.",
    "This phrase is not allowed here.",
]
for text in texts:
    result = guard.validate(text)
    status = "PASS" if result.is_valid else "BLOCKED"
    print(f"  [{status}] {text}")
    for v in result.violations:
        print(f"         -> {v.message}")

# --- Example 2: Content Filter ---
print("\n" + "=" * 60)
print("Example 2: Content Filter")
print("=" * 60)

guard = LLMGuard({
    "content_filter": {
        "enabled": True,
        "categories": {"hate": 0.3, "violence": 0.3},
    }
})

texts = [
    "The weather is beautiful today.",
    "That racist bigot promotes hate and supremacy.",
    "They plan to kill and murder innocent people.",
]
for text in texts:
    result = guard.validate(text)
    status = "PASS" if result.is_valid else "BLOCKED"
    print(f"  [{status}] {text}")
    for v in result.violations:
        print(f"         -> {v.message}")

# --- Example 3: PII Filter ---
print("\n" + "=" * 60)
print("Example 3: PII Filter (mask mode)")
print("=" * 60)

guard = LLMGuard({
    "pii_filter": {
        "enabled": True,
        "entities": ["EMAIL", "PHONE", "SSN"],
        "action": "mask",
    }
})

text = "Contact John at john@example.com or 555-123-4567. SSN: 123-45-6789"
result = guard.validate(text)
print(f"  Original:  {text}")
print(f"  Masked:    {result.masked_text}")
print(f"  PII found: {len(result.violations)}")
for v in result.violations:
    print(f"         -> {v.message}")

# --- Example 4: Topic Filter ---
print("\n" + "=" * 60)
print("Example 4: Topic Filter")
print("=" * 60)

guard = LLMGuard({
    "topic_filter": {
        "enabled": True,
        "denied_topics": ["politics", "religion"],
    }
})

texts = [
    "I enjoy programming in Python.",
    "The election campaign and congress vote was controversial.",
    "The church prayer service was peaceful.",
]
for text in texts:
    result = guard.validate(text)
    status = "PASS" if result.is_valid else "BLOCKED"
    print(f"  [{status}] {text}")
    for v in result.violations:
        print(f"         -> {v.message}")

# --- Example 5: All Filters Combined ---
print("\n" + "=" * 60)
print("Example 5: All Filters Combined")
print("=" * 60)

guard = LLMGuard({
    "word_filter": {
        "enabled": True,
        "blocked_words": ["forbidden"],
        "use_profanity_list": False,
    },
    "content_filter": {
        "enabled": True,
        "categories": {"hate": 0.3, "violence": 0.3},
    },
    "pii_filter": {
        "enabled": True,
        "entities": ["EMAIL"],
        "action": "mask",
    },
    "topic_filter": {
        "enabled": True,
        "denied_topics": ["gambling"],
    },
})

text = "Email admin@example.com about the casino bet"
result = guard.validate(text)
print(f"  Text:       {text}")
print(f"  Valid:      {result.is_valid}")
print(f"  Masked:     {result.masked_text}")
print(f"  Violations: {len(result.violations)}")
for v in result.violations:
    print(f"         -> [{v.filter_name}] {v.message}")

# --- Example 6: mask_pii convenience ---
print("\n" + "=" * 60)
print("Example 6: Quick PII masking")
print("=" * 60)

guard = LLMGuard({"pii_filter": {"enabled": True, "entities": ["EMAIL"], "action": "mask"}})
masked = guard.mask_pii("Send report to ceo@company.com and cfo@company.com")
print(f"  Masked: {masked}")
