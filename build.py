import json
import os
import re


def _find_all_code_envs(content: str) -> list:
    code_starts = [m.start() for m in re.finditer("<code", content)]
    code_ends = [m.end() for m in re.finditer("</code>", content)]
    return [(s, e) for s, e in zip(code_starts, code_ends)]

def _find_all_link_envs(content: str) -> list:
    link_starts = [m.start() for m in re.finditer("<a", content)]
    link_ends = [m.end() for m in re.finditer("</a>", content)]
    return [(s, e) for s, e in zip(link_starts, link_ends)]

def _find_all_special_envs(content: str) -> list:
    return _find_all_code_envs(content)+_find_all_link_envs(content)

def _found_in_special_env(idx: int, special_envs: list) -> bool:
    for (start, end) in special_envs:
        if start < idx < end:
            return True
    return False


def _convert_md_to_html(content: str, pattern: str, before: str, after: str) -> str:
    special_envs = _find_all_special_envs(content)
    start_search = content.find("<body>") # skip the <head></head>

    idx_start = content.find(pattern, start_search)
    len_pattern = len(pattern)
    while idx_start > 0:
        # If the match is found in special environment, skip the change
        if _found_in_special_env(idx_start, special_envs):
            start_search = idx_start+len_pattern
            idx_start = content.find(pattern, start_search)
            continue

        idx_end = content.find(pattern, idx_start+len_pattern)
        txt = content[idx_start+len_pattern:idx_end]

        content = (
            content[:idx_start]
            +f"{before}{txt}{after}"
            +content[idx_end+len_pattern:]
        )

        # Update the location of special environments
        special_envs = _find_all_special_envs(content)

        idx_start = content.find(pattern, start_search)

    return content


def _convert_links_to_a(content: str) -> str:
    """
    Converts [...](...) to <a href='...'>...</a>
    """
    special_envs = _find_all_special_envs(content)
    start_search = content.find("<body>") # skip the <head></head>

    idx_name_start = content.find("[")
    while idx_name_start > 0:
        # If the match is found in code environment, skip the change
        if _found_in_special_env(idx_name_start, special_envs):
            start_search = idx_name_start+1
            idx_name_start = content.find("[", start_search)
            continue

        idx_name_end = content.find("]", idx_name_start)
        idx_link_start = idx_name_end+1
        idx_link_end = content.find(")", idx_link_start)

        name = content[idx_name_start+1:idx_name_end]
        link = content[idx_link_start+1:idx_link_end]

        content = (
            content[:idx_name_start]
            +f"<a href='{link}' target='_blank'>{name}</a>"
            +content[idx_link_end+1:]
        )

        # Update the location of special environments
        special_envs = _find_all_special_envs(content)

        idx_name_start = content.find("[")

    return content


def parse_markdown_to_html(file_name: str) -> str:
    with open(file_name, "r", encoding="UTF-8") as f:
        text = f.readlines()

    content = "<!DOCTYPE html>\n<html>\n<head>"
    
    # Add some predefined metadata
    content += "\n<meta name='author' content='Domen Mohorčič'>"
    content += "\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    
    # Parse header
    header = False
    for header_skip, line in enumerate(text):
        if line.strip() == "---":
            if not header:
                header = True
            else:
                break
        elif header:
            # get header parameter
            args = line.strip().split(": ", maxsplit=1)
            match args:
                case ("title", title):
                    title = title.replace("\"", "")
                    content += f"\n<title>{title}</title>"
                case ("tags", tags):
                    tags = tags.split(" ")
                    for tag in tags:
                        content += f"\n<meta name='tag' content='{tag}'>"
                case (key, val): # the default case
                    content += f"\n<meta name='{key}' content='{val}'>"

    content += "\n<link rel='stylesheet' href='{BASE_URL}css_code/styles/default.min.css'>"
    content += "\n<script src='{BASE_URL}css_code/highlight.min.js'></script>"
    content += "\n<script>hljs.highlightAll();</script>"

    content += "\n<link rel='stylesheet' href='{BASE_URL}default.css'>"

    content += "\n</head>\n<body>"

    # Add the navbar at the top
    with open("html_components/navbar.html", "r", encoding="UTF-8") as f:
        navbar = "".join(f.readlines())
    content += f"\n{navbar}"

    # Parse the content of the file
    is_table = ""
    is_code = ""
    for line in text[header_skip+1:]:
        if len(is_code) == 0:
            line = line.strip()
        # Parse headings
        if line.startswith("#"):
            heading_number = line.split(" ")[0].count("#")
            heading_text = line.split(" ", 1)[1]
            content += f"\n<h{heading_number}>{heading_text}</h{heading_number}>"
        # Parse lists
        elif (c1 := line.startswith("-")) or (len(line) > 0  and line[0].isdigit()):
            li = line[1:].strip()
            if is_table == "":
                is_table = "ul" if c1 else "ol"
                content += f"\n<{is_table}>"
            content += f"\n<li>{li}</li>"
        # Parse code blocks
        elif (c := line.startswith("```")) or len(is_code):
            if len(is_table) > 0:
                content += f"\n</{is_table}>"
                is_table = ""
            if len(is_code) == 0:
                is_code = line[3:] if len(line) > 3 else "unknown"
                content += "\n<pre><code>" if is_code == "unknown" else f"\n<pre><code class='{is_code}'>"
            elif c:
                content += "</code></pre>"
                is_code = ""
            else:
                content += line
        # Parse quotations
        elif line.startswith(">"):
            bq = line[1:].strip()
            if len(is_table) > 0:
                content += f"\n</{is_table}>"
                is_table = ""
            content += f"\n<blockquote>{bq}</blockquote>"
        # Parse normal text
        elif len(line) > 0 and not is_code:
            if len(is_table) > 0:
                content += f"\n</{is_table}>"
                is_table = ""
            content += f"\n<p>{line}</p>"
        else:
            if len(is_table) > 0:
                content += f"\n</{is_table}>"
                is_table = ""
    
    # End the HTML file
    content += "\n</body>\n</html>"

    # Convert all inline code blocks
    content = _convert_md_to_html(content, "`", "<code class='inline'>", "</code>")

    # Convert all links
    content = _convert_links_to_a(content)

    # Convert all bold, italic, and strikethrough modifications
    content = _convert_md_to_html(content, "***", "<strong><em>", "</em></strong>")
    content = _convert_md_to_html(content, "___", "<strong><em>", "</em></strong>")
    content = _convert_md_to_html(content, "**", "<strong>", "</strong>")
    content = _convert_md_to_html(content, "__", "<strong>", "</strong>")
    content = _convert_md_to_html(content, "*", "<em>", "</em>")
    content = _convert_md_to_html(content, "_", "<em>", "</em>")
    content = _convert_md_to_html(content, "~~", "<del>", "</del>")

    return content


def includes_in_html(content: str) -> str:
    content_lines = content.split("\n")
    for i, line in enumerate(content_lines):
        if "w3-include-html" in line:
            idx_start = line.find("\"")
            idx_end = line.find("\"", idx_start+1)
            include_name = line[idx_start+1:idx_end]
            with open(include_name, "r", encoding="UTF-8") as f:
                include_text = "".join(f.readlines())
            content_lines[i] = include_text
    
    return "\n".join(content_lines)


def builds_in_html(content: str) -> str:
    content_lines = content.split("\n")
    for i, line in enumerate(content_lines):
        if "build" in line:
            # Get from what folder to build
            folder_start = line.find("build")+7 # build='
            folder_end = line.find("'", folder_start)
            folder_name = line[folder_start:folder_end]
            build_folder_name = folder_name[1:]

            # Get the category if it exists
            category_name = None
            if "category" in line:
                category_start = line.find("category")+10 # category='
                category_end = line.find("'", category_start)
                category_name = line[category_start:category_end]
            
            build = "<ul>"
            for file_name in os.listdir(folder_name):
                with open(f"{folder_name}/{file_name}") as f:
                    c = 0
                    for line in f:
                        if line.startswith("title"):
                            file_title = line[7:].strip().replace("\"", "")
                            c += 1
                        elif line.startswith("category"):
                            file_category = line[10:].strip()
                            c += 1
                        if c == 2:
                            break
                if category_name and category_name != file_category:
                    continue
                file_name = file_name.split(".")[0]
                build += f"\n<li><a href='{build_folder_name}/{file_name}.html'>{file_title}</a></li>"
            build += "\n</ul>"
            content_lines[i] = build

    return "\n".join(content_lines)


CONST: dict = None
def _parse_const(env: str = "prod") -> dict:
    with open("constants.json", "r") as f:
        data = json.load(f)
    return data[env]


def replaces_in_html(content: str) -> str:
    keys = CONST.keys()
    for key in keys:
        content = content.replace("{"+key+"}", CONST[key])
    return content


def main():
    # Build all blogs and projects
    for folder in ["blog", "project"]:
        for file_name in os.listdir(f"_{folder}"):
            file_name = file_name.split(".")[0]
            content = parse_markdown_to_html(f"_{folder}/{file_name}.md")
            content = replaces_in_html(content)
            with open(f"{folder}/{file_name}.html", "w", encoding="UTF-8") as f:
                f.write(content)

    # Build 4 base files
    for base_file in ["about", "blog", "index", "project"]:
        with open(f"_{base_file}.html", "r", encoding="UTF-8") as f:
            text = "".join(f.readlines())
        content = includes_in_html(text)
        content = builds_in_html(content)
        content = replaces_in_html(content)
        with open(f"{base_file}.html", "w", encoding="UTF-8") as f:
            f.write(content)


if __name__ == "__main__":
    prod = input("Build for production ([y]/n)? ")
    if prod == "n":
        print("Building for development")
        CONST = _parse_const("dev")
    else:
        print("Building for production")
        CONST = _parse_const("prod")
    main()