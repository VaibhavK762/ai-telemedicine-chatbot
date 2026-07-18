def format_prompt(tokenizer, instruction: str, input_text: str, output_text: str | None = None) -> str:
    """
    Format SFT instructions to match standard template. Attempts to use
    tokenizer's built-in chat template, falling back to standard Mistral
    instructions format if no template is defined.
    """
    messages = [
        {"role": "user", "content": f"{instruction.strip()}\n\n{input_text.strip()}"}
    ]
    if output_text is not None:
        messages.append({"role": "assistant", "content": output_text.strip()})

    try:
        # Check if tokenizer has a default template
        if getattr(tokenizer, "default_chat_template", None) is not None or getattr(tokenizer, "chat_template", None) is not None:
            add_generation = (output_text is None)
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=add_generation)
    except Exception:
        pass

    # Fallback to Mistral instruction format
    bos = tokenizer.bos_token or "<s>"
    eos = tokenizer.eos_token or "</s>"
    
    prompt = f"{bos}[INST] {instruction.strip()}\n\n{input_text.strip()} [/INST]"
    if output_text is not None:
        prompt += f" {output_text.strip()}{eos}"
    return prompt
