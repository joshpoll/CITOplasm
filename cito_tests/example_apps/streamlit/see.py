def render_sight(data):
    markdown_lines = []

    markdown_lines.append(f"### {data.get('title', '')}")
    markdown_lines.append(f"- type: {data.get('description', '')}")

    if "price" in data:
        markdown_lines.append(f"- price: {data.get('price', '')}")
    elif "extracted_price" in data:
        markdown_lines.append(f"- price: ${data.get('extracted_price', '')}")

    markdown_lines.append(f"- rating: {data.get('rating', '')}")
    markdown_lines.append(f"- reviews: {data.get('reviews', '')}")

    return "\n".join(markdown_lines)
