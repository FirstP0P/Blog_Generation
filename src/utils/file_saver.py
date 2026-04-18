import os

def save_blog_to_markdown(state: dict, output_dir: str = "generated_blogs"):
    """
    Parses the LangGraph state and saves the blog content to a Markdown file.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Extract data from the state dictionary
    topic = state.get("topic", "unknown_topic")
    blog_data = state.get("blog", {})

    title = blog_data.get("title", "Untitled Blog")
    content = blog_data.get("content", "No content generated.")

    # Check if a specific language was used, otherwise default to english
    language = state.get("current_language", "english")

    # Create a safe filename (e.g., "machine_learning_french.md")
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic]).strip("_")
    filename = f"{safe_topic}_{language}.md"
    filepath = os.path.join(output_dir, filename)

    # Format the markdown text
    markdown_content = f"# {title}\n\n"
    markdown_content += f"**Topic:** {topic} | **Language:** {language.capitalize()}\n\n"
    markdown_content += "---\n\n"
    markdown_content += f"{content}\n"

    # Write to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    return filepath
