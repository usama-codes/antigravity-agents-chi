import os
import re
import sys
import uuid
import yaml

# Threshold settings
MAX_CHARACTER_LIMIT = 500
MAX_LINE_LIMIT = 15

def calculate_minimized_payload(message_text, workspace_path):
    """
    Parses message_text. Detects long stack traces, logs, or file dumps.
    Writes them to the pipeline scratch directory and replaces them with hyperlinks.
    Also collapses dialogue histories.
    """
    scratch_dir = os.path.join(workspace_path, "pipeline_output", "scratch")
    if not os.path.exists(scratch_dir):
        os.makedirs(scratch_dir)

    # 1. Detect and truncate long raw logs/traceblocks
    # Match codeblocks that are long
    codeblock_regex = re.compile(r"```(.*?)\n(.*?)```", re.DOTALL)
    
    def process_codeblock(match):
        lang = match.group(1).strip()
        content = match.group(2)
        lines = content.splitlines()
        
        if len(lines) > MAX_LINE_LIMIT or len(content) > MAX_CHARACTER_LIMIT:
            filename = f"truncated_log_{uuid.uuid4().hex[:8]}.txt"
            filepath = os.path.join(scratch_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Convert Windows backslashes to forward slashes for markdown link URI compatibility
            abs_uri = filepath.replace("\\", "/")
            return f"```\n[Log block truncated for token economy - View raw file](file:///{abs_uri})\n```"
        return match.group(0)

    minimized_text = codeblock_regex.sub(process_codeblock, message_text)

    # 2. Collapse dialogue context details
    # Look for sequential [COMPLETE], [STATUS] or [HANDOFF] blocks that may have been pasted
    lines = minimized_text.splitlines()
    processed_lines = []
    in_dialogue_block = False
    dialogue_buffer = []

    for line in lines:
        if any(prefix in line for prefix in ["[COMPLETE]", "[STATUS]", "[HANDOFF]", "[FAILURE]", "[BLOCKED]"]):
            in_dialogue_block = True
            dialogue_buffer.append(line)
        elif in_dialogue_block and line.strip() == "":
            # blank line ends dialogue header block
            in_dialogue_block = False
            processed_lines.append(f"> **Minimized Conversation Context**: {', '.join(dialogue_buffer)}")
            dialogue_buffer = []
        elif in_dialogue_block:
            dialogue_buffer.append(line.strip())
        else:
            processed_lines.append(line)

    if dialogue_buffer:
        processed_lines.append(f"> **Minimized Conversation Context**: {', '.join(dialogue_buffer)}")

    return "\n".join(processed_lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python context_pruner.py <message_file_path> <workspace_path>")
        sys.exit(1)

    message_file = sys.argv[1]
    workspace = sys.argv[2]

    if not os.path.exists(message_file):
        print(f"Error: Message file '{message_file}' not found.")
        sys.exit(1)

    with open(message_file, "r", encoding="utf-8") as f:
        message_content = f.read()

    minimized = calculate_minimized_payload(message_content, workspace)

    with open(message_file, "w", encoding="utf-8") as f:
        f.write(minimized)

    print("Success: Message context successfully pruned.")

if __name__ == "__main__":
    main()
