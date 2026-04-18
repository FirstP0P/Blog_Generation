from src.states.blogstate import BlogState
from langchain_core.messages import SystemMessage, HumanMessage
from src.states.blogstate import Blog

# ── Helpers ───────────────────────────────────────────────────────────────────
TONE_GUIDE = {
    "professional": "formal, authoritative, and business-appropriate",
    "casual":       "friendly, conversational, and easy-going",
    "academic":     "scholarly, research-oriented, with a formal academic style",
    "creative":     "imaginative, vivid, and storytelling-driven",
    "persuasive":   "compelling, opinion-driven, and call-to-action focused",
}

LENGTH_GUIDE = {
    "short":  "300–500 words",
    "medium": "600–900 words",
    "long":   "1000–1500 words",
}


class BlogNode:
    """
    A class to represent the blog node.
    """

    def __init__(self, llm):
        self.llm = llm

    def title_creation(self, state: BlogState):
        if not state.get("topic"):
            return {"blog": {"title": "No topic provided"}}

        tone       = state.get("tone", "professional")
        tone_desc  = TONE_GUIDE.get(tone, "formal and professional")

        prompt = f"""
You are an expert blog content writer.
Generate ONE compelling, SEO-friendly blog title for the topic below.
The tone should be: {tone_desc}.
Return ONLY the title — no extra text, no quotes.

Topic: {state['topic']}
        """

        response = self.llm.invoke([SystemMessage(content=prompt)])
        return {"blog": {"title": response.content.strip()}}

    def content_generation(self, state: BlogState):
        if not state.get("topic"):
            return {"blog": {"title": "", "content": "No topic provided"}}

        tone        = state.get("tone", "professional")
        length      = state.get("length", "medium")
        tone_desc   = TONE_GUIDE.get(tone, "formal and professional")
        length_desc = LENGTH_GUIDE.get(length, "600–900 words")

        prompt = f"""
You are an expert blog writer. Use Markdown formatting throughout.

Write a complete blog post using the title and topic below.

Requirements:
- Tone: {tone_desc}
- Target length: {length_desc}
- Structure: Introduction → clearly labelled sections (## headings) → Conclusion
- Use **bold** for key terms, bullet points where helpful
- Make it engaging and SEO-friendly
- Return blog content ONLY — no meta-commentary

Title: {state['blog']['title']}
Topic: {state['topic']}
        """

        response = self.llm.invoke([SystemMessage(content=prompt)])
        return {
            "blog": {
                "title":   state["blog"]["title"],
                "content": response.content.strip(),
            }
        }

    def translation(self, state: BlogState):
        prompt = f"""
Translate the following blog post into {state['current_language']}.
Preserve all Markdown formatting, headings, and structure exactly.
Return ONLY the translated blog — no preamble.

{state['blog']['content']}
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            "blog": {
                "title":   state["blog"]["title"],
                "content": response.content.strip(),
            }
        }

    def route(self, state: BlogState):
        return {"current_language": state["current_language"]}

    def route_decision(self, state: BlogState):
        lang = state.get("current_language", "").lower()
        if lang == "hindi":
            return "hindi"
        elif lang == "french":
            return "french"
        else:
            return lang
